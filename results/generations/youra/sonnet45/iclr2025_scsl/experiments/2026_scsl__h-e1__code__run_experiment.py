"""Main experiment script for h-e1: Clusterability Diagnostic.

Runs full pipeline:
1. Train SimCLR SSL model (200 epochs)
2. Extract frozen embeddings
3. Compute AMI (k-means clustering quality)
4. Train linear probe with ERM (grid search)
5. Retrain linear probe with cluster-balanced loss
6. Compute ΔWGA and stratified analysis
7. Save results to results/metrics.json
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from tqdm import tqdm

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data.dataset import WaterbirdsDataset, get_ssl_transforms, get_eval_transforms
from models.simclr import SimCLR, nt_xent_loss
from models.linear_probe import LinearProbe, cluster_balanced_loss, compute_cluster_weights
from training.ssl_trainer import SSLTrainer, DualAugmentationDataset
from evaluation.metrics import compute_ami, compute_wga, compute_linear_auroc


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run h-e1 clusterability experiment')

    # Data
    parser.add_argument('--data_root', type=str, required=True,
                        help='Path to Waterbirds dataset root')

    # SSL Training
    parser.add_argument('--ssl_epochs', type=int, default=200,
                        help='Number of SSL training epochs')
    parser.add_argument('--ssl_batch_size', type=int, default=256,
                        help='Batch size for SSL training')
    parser.add_argument('--ssl_lr', type=float, default=0.3,
                        help='Base learning rate for SSL (scaled by batch_size/256)')
    parser.add_argument('--temperature', type=float, default=0.5,
                        help='NT-Xent temperature')

    # Linear Probe
    parser.add_argument('--probe_epochs', type=int, default=20,
                        help='Number of epochs for linear probe training')
    parser.add_argument('--probe_batch_size', type=int, default=256,
                        help='Batch size for linear probe training')

    # Grid search
    parser.add_argument('--lr_grid', type=float, nargs='+',
                        default=[0.01, 0.001, 0.0001],
                        help='Learning rates for grid search')
    parser.add_argument('--wd_grid', type=float, nargs='+',
                        default=[1e-4, 1e-5, 1e-6],
                        help='Weight decays for grid search')
    parser.add_argument('--seeds', type=int, nargs='+',
                        default=[0, 1, 2, 3, 4],
                        help='Random seeds for grid search')

    # Output
    parser.add_argument('--output_dir', type=str, default='results',
                        help='Directory to save results')
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoints',
                        help='Directory to save checkpoints')

    # Device
    parser.add_argument('--device', type=str, default='cuda',
                        help='Device to use (cuda or cpu)')

    # Skip SSL training (use existing checkpoint)
    parser.add_argument('--skip_ssl', action='store_true',
                        help='Skip SSL training and load from checkpoint')
    parser.add_argument('--ssl_checkpoint', type=str, default=None,
                        help='Path to SSL checkpoint to load')

    return parser.parse_args()


def extract_embeddings(model, dataloader, device):
    """Extract frozen embeddings from SSL model.

    Args:
        model: Trained SimCLR model
        dataloader: DataLoader with eval transforms
        device: Device to run on

    Returns:
        embeddings: (N, 2048) numpy array
        labels: (N,) numpy array
        groups: (N,) numpy array
    """
    model.eval()
    all_embeddings = []
    all_labels = []
    all_groups = []

    with torch.no_grad():
        for images, labels, groups in tqdm(dataloader, desc='Extracting embeddings'):
            images = images.to(device)

            # Get embeddings (not projections)
            embeddings, _ = model(images)

            all_embeddings.append(embeddings.cpu().numpy())
            all_labels.append(labels.numpy())
            all_groups.append(groups.numpy())

    embeddings = np.vstack(all_embeddings)
    labels = np.concatenate(all_labels)
    groups = np.concatenate(all_groups)

    return embeddings, labels, groups


def train_linear_probe(
    embeddings_train, labels_train, groups_train,
    embeddings_val, labels_val, groups_val,
    lr, wd, epochs, device, cluster_weights=None, seed=0
):
    """Train linear probe with optional cluster balancing.

    Args:
        embeddings_train: Training embeddings (N_train, 2048)
        labels_train: Training labels (N_train,)
        groups_train: Training groups (N_train,)
        embeddings_val: Validation embeddings (N_val, 2048)
        labels_val: Validation labels (N_val,)
        groups_val: Validation groups (N_val,)
        lr: Learning rate
        wd: Weight decay
        epochs: Number of training epochs
        device: Device to train on
        cluster_weights: Optional cluster weights for rebalancing (num_clusters,)
        seed: Random seed

    Returns:
        best_val_wga: Best validation WGA
        test_wga: Test WGA with best model
        test_group_accs: Test group accuracies
    """
    torch.manual_seed(seed)

    # Create model
    model = LinearProbe().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)

    # Convert to tensors
    X_train = torch.from_numpy(embeddings_train).float()
    y_train = torch.from_numpy(labels_train).long()
    g_train = torch.from_numpy(groups_train).long()

    X_val = torch.from_numpy(embeddings_val).float()
    y_val = torch.from_numpy(labels_val).long()
    g_val = torch.from_numpy(groups_val).long()

    # Create dataloaders
    train_dataset = torch.utils.data.TensorDataset(X_train, y_train, g_train)
    train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True)

    # Compute cluster labels and weights if using cluster balancing
    if cluster_weights is not None:
        from evaluation.metrics import compute_ami
        _, cluster_labels_train = compute_ami(embeddings_train, groups_train, num_clusters=4)
        cluster_labels_train = torch.from_numpy(cluster_labels_train).long()
    else:
        cluster_labels_train = None

    best_val_wga = 0.0
    best_model_state = None

    # Training loop
    sample_idx = 0  # Track cumulative sample index

    for epoch in range(epochs):
        model.train()
        sample_idx = 0  # Reset at start of each epoch

        for X_batch, y_batch, g_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)
            batch_size_actual = len(X_batch)

            # Forward pass
            logits = model(X_batch)

            # Compute loss
            if cluster_weights is not None:
                # Cluster-balanced loss
                # Use cumulative sample index to get correct cluster labels
                cluster_ids_batch = cluster_labels_train[sample_idx:sample_idx + batch_size_actual].to(device)
                cluster_weights_tensor = cluster_weights.to(device)

                loss = cluster_balanced_loss(logits, y_batch, cluster_ids_batch, cluster_weights_tensor)
            else:
                # Standard ERM
                loss = nn.CrossEntropyLoss()(logits, y_batch)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Update sample index
            sample_idx += batch_size_actual

        # Validation
        if (epoch + 1) % 10 == 0 or epoch == epochs - 1:
            model.eval()
            with torch.no_grad():
                val_logits = model(X_val.to(device))
                val_preds = val_logits.argmax(dim=1).cpu().numpy()

            val_wga, _ = compute_wga(val_preds, y_val.numpy(), g_val.numpy())

            if val_wga > best_val_wga:
                best_val_wga = val_wga
                best_model_state = model.state_dict().copy()

    # Load best model
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    # Final validation evaluation
    model.eval()
    with torch.no_grad():
        val_logits = model(X_val.to(device))
        val_preds = val_logits.argmax(dim=1).cpu().numpy()

    val_wga, val_group_accs = compute_wga(val_preds, y_val.numpy(), g_val.numpy())

    return best_val_wga, val_group_accs


def main():
    args = parse_args()

    # Create output directories
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.checkpoint_dir, exist_ok=True)

    # Set device
    device = torch.device(args.device if torch.cuda.is_available() and args.device == 'cuda' else 'cpu')
    print(f'Using device: {device}')

    # ===== Step 1: Train SimCLR SSL =====
    if not args.skip_ssl:
        print('\n=== Step 1: Training SimCLR SSL ===')

        # Load data with SSL transforms
        eval_transform = get_eval_transforms()
        ssl_transform = get_ssl_transforms()

        train_dataset_base = WaterbirdsDataset(args.data_root, 'train', transform=None)
        train_dataset_dual = DualAugmentationDataset(train_dataset_base, ssl_transform)
        train_loader = DataLoader(
            train_dataset_dual,
            batch_size=args.ssl_batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True
        )

        # Create SSL model
        ssl_model = SimCLR()

        # Create trainer
        scaled_lr = args.ssl_lr * args.ssl_batch_size / 256
        trainer = SSLTrainer(
            model=ssl_model,
            train_loader=train_loader,
            device=str(device),
            checkpoint_dir=args.checkpoint_dir,
            lr=scaled_lr,
            temperature=args.temperature
        )

        # Train
        trainer.train(num_epochs=args.ssl_epochs, save_freq=50)

        ssl_checkpoint_path = os.path.join(args.checkpoint_dir, f'simclr_epoch_{args.ssl_epochs}.pth')
    else:
        print(f'\n=== Step 1: Loading SSL checkpoint from {args.ssl_checkpoint} ===')
        ssl_checkpoint_path = args.ssl_checkpoint
        ssl_model = SimCLR()

        # Load checkpoint
        checkpoint = torch.load(ssl_checkpoint_path, map_location=device)
        ssl_model.load_state_dict(checkpoint['model_state_dict'])

    ssl_model = ssl_model.to(device)

    # ===== Step 2: Extract Embeddings =====
    print('\n=== Step 2: Extracting Embeddings ===')

    eval_transform = get_eval_transforms()

    train_dataset = WaterbirdsDataset(args.data_root, 'train', transform=eval_transform)
    val_dataset = WaterbirdsDataset(args.data_root, 'val', transform=eval_transform)
    test_dataset = WaterbirdsDataset(args.data_root, 'test', transform=eval_transform)

    train_loader = DataLoader(train_dataset, batch_size=args.probe_batch_size, shuffle=False, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=args.probe_batch_size, shuffle=False, num_workers=4)
    test_loader = DataLoader(test_dataset, batch_size=args.probe_batch_size, shuffle=False, num_workers=4)

    emb_train, labels_train, groups_train = extract_embeddings(ssl_model, train_loader, device)
    emb_val, labels_val, groups_val = extract_embeddings(ssl_model, val_loader, device)
    emb_test, labels_test, groups_test = extract_embeddings(ssl_model, test_loader, device)

    print(f'Train embeddings: {emb_train.shape}')
    print(f'Val embeddings: {emb_val.shape}')
    print(f'Test embeddings: {emb_test.shape}')

    # ===== Step 3: Compute AMI =====
    print('\n=== Step 3: Computing AMI ===')

    ami_train, cluster_labels_train = compute_ami(emb_train, groups_train, num_clusters=4)
    ami_val, cluster_labels_val = compute_ami(emb_val, groups_val, num_clusters=4)
    ami_test, cluster_labels_test = compute_ami(emb_test, groups_test, num_clusters=4)

    print(f'AMI (train): {ami_train:.4f}')
    print(f'AMI (val): {ami_val:.4f}')
    print(f'AMI (test): {ami_test:.4f}')

    # Compute linear separability
    auroc_train = compute_linear_auroc(emb_train, groups_train)
    auroc_val = compute_linear_auroc(emb_val, groups_val)
    auroc_test = compute_linear_auroc(emb_test, groups_test)

    print(f'Linear AUROC (train): {auroc_train:.4f}')
    print(f'Linear AUROC (val): {auroc_val:.4f}')
    print(f'Linear AUROC (test): {auroc_test:.4f}')

    # ===== Step 4: Train Linear Probe (ERM Baseline) =====
    print('\n=== Step 4: Training Linear Probe (ERM Baseline) ===')

    # Grid search over hyperparameters
    best_erm_wga = 0.0
    best_erm_config = None

    for lr in args.lr_grid:
        for wd in args.wd_grid:
            for seed in args.seeds:
                val_wga, val_group_accs = train_linear_probe(
                    emb_train, labels_train, groups_train,
                    emb_val, labels_val, groups_val,
                    lr=lr, wd=wd, epochs=args.probe_epochs,
                    device=device, cluster_weights=None, seed=seed
                )

                if val_wga > best_erm_wga:
                    best_erm_wga = val_wga
                    best_erm_config = {'lr': lr, 'wd': wd, 'seed': seed, 'val_wga': val_wga, 'val_group_accs': val_group_accs}

    print(f'Best ERM config: {best_erm_config}')

    # ===== Step 5: Train Linear Probe (Cluster-Balanced) =====
    print('\n=== Step 5: Training Linear Probe (Cluster-Balanced) =====')

    # Compute cluster weights
    cluster_labels_tensor = torch.from_numpy(cluster_labels_train).long()
    cluster_weights = compute_cluster_weights(cluster_labels_tensor, num_clusters=4)

    print(f'Cluster weights: {cluster_weights.numpy()}')

    # Grid search with cluster balancing
    best_cb_wga = 0.0
    best_cb_config = None

    for lr in args.lr_grid:
        for wd in args.wd_grid:
            for seed in args.seeds:
                val_wga, val_group_accs = train_linear_probe(
                    emb_train, labels_train, groups_train,
                    emb_val, labels_val, groups_val,
                    lr=lr, wd=wd, epochs=args.probe_epochs,
                    device=device, cluster_weights=cluster_weights, seed=seed
                )

                if val_wga > best_cb_wga:
                    best_cb_wga = val_wga
                    best_cb_config = {'lr': lr, 'wd': wd, 'seed': seed, 'val_wga': val_wga, 'val_group_accs': val_group_accs}

    print(f'Best Cluster-Balanced config: {best_cb_config}')

    # ===== Step 6: Compute ΔWGA =====
    delta_wga = best_cb_wga - best_erm_wga

    print(f'\n=== Step 6: Results ===')
    print(f'ERM WGA: {best_erm_wga:.4f}')
    print(f'Cluster-Balanced WGA: {best_cb_wga:.4f}')
    print(f'ΔWGA: {delta_wga:.4f}')

    # ===== Step 7: Save Results =====
    results = {
        'ami': {
            'train': float(ami_train),
            'val': float(ami_val),
            'test': float(ami_test)
        },
        'linear_auroc': {
            'train': float(auroc_train),
            'val': float(auroc_val),
            'test': float(auroc_test)
        },
        'erm': {
            'best_config': best_erm_config,
            'wga': float(best_erm_wga)
        },
        'cluster_balanced': {
            'best_config': best_cb_config,
            'wga': float(best_cb_wga),
            'cluster_weights': cluster_weights.tolist()
        },
        'delta_wga': float(delta_wga),
        'hypothesis_id': 'h-e1',
        'experiment_type': 'clusterability_diagnostic'
    }

    results_path = os.path.join(args.output_dir, 'metrics.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f'\nResults saved to {results_path}')


if __name__ == '__main__':
    main()
