"""Run mechanism validation suite (M1/M2/M3 gate checks).

This script extracts embeddings from trained models and validates mechanisms.
Requires completed SimCLR and LA-SSL training.
"""

import sys
import os
from pathlib import Path
import torch
import numpy as np
import json
from torch.utils.data import DataLoader
from tqdm import tqdm

# Setup paths
current_dir = Path(__file__).parent.absolute()
h_e1_path = (current_dir.parent.parent / 'h-e1' / 'code').absolute()

os.chdir(current_dir)
sys.path.insert(0, str(h_e1_path))

# Direct imports
with open(current_dir / 'evaluation' / 'mechanism_validator.py') as f:
    exec(compile(f.read(), 'mechanism_validator.py', 'exec'), globals())

with open(current_dir / 'config.py') as f:
    exec(compile(f.read(), 'config.py', 'exec'), globals())

# Import from h-e1
from models.simclr import SimCLR
from data.dataset import WaterbirdsDataset, get_eval_transforms
from training.ssl_trainer import SSLTrainer


def extract_embeddings(model, dataloader, device):
    """Extract embeddings from trained model.

    Args:
        model: Trained SimCLR or LA-SSL model
        dataloader: DataLoader for dataset
        device: Device to run on

    Returns:
        embeddings: numpy array [N, 2048]
        labels: numpy array [N] (class labels)
        groups: numpy array [N] (group labels)
    """
    model.eval()
    all_embeddings = []
    all_labels = []
    all_groups = []

    with torch.no_grad():
        for batch_data in tqdm(dataloader, desc="Extracting embeddings"):
            # Unpack tuple: (images, labels, groups)
            images, labels, groups = batch_data
            images = images.to(device)

            # Get encoder features (before projection head)
            features = model.encoder(images)

            # Flatten spatial dimensions if needed (ResNet returns [B, C, H, W])
            if len(features.shape) == 4:
                features = features.reshape(features.shape[0], -1)

            all_embeddings.append(features.cpu().numpy())
            all_labels.append(labels.cpu().numpy())
            all_groups.append(groups.cpu().numpy())

    embeddings = np.vstack(all_embeddings)
    labels = np.concatenate(all_labels)
    groups = np.concatenate(all_groups)

    return embeddings, labels, groups


def load_checkpoint_and_extract(checkpoint_path, device, split='test'):
    """Load a checkpoint and extract embeddings.

    Args:
        checkpoint_path: Path to checkpoint file
        device: Device to run on
        split: Dataset split to use ('train', 'val', or 'test')

    Returns:
        embeddings: numpy array [N, 2048]
        labels: numpy array [N] (class labels)
        groups: numpy array [N] (group labels)
    """
    print(f"Loading checkpoint: {checkpoint_path}")

    # Initialize model
    model = SimCLR(
        encoder_name=SIMCLR_CONFIG['encoder_name'],
        projection_dim=SIMCLR_CONFIG['projection_dim'],
        pretrained=False
    ).to(device)

    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])

    # Load dataset
    eval_transform = get_eval_transforms()
    dataset = WaterbirdsDataset(
        root_dir=DATA_CONFIG['root_dir'],
        split=split,
        transform=eval_transform
    )

    dataloader = DataLoader(
        dataset,
        batch_size=128,
        shuffle=False,
        num_workers=DATA_CONFIG['num_workers'],
        pin_memory=True
    )

    # Extract embeddings
    embeddings, labels, groups = extract_embeddings(model, dataloader, device)

    return embeddings, labels, groups


def compute_ami_evolution_from_checkpoints(checkpoint_dir, device):
    """Compute AMI evolution from saved checkpoints.

    Args:
        checkpoint_dir: Directory containing checkpoints
        device: Device to run on

    Returns:
        ami_values: List of AMI scores
        epochs: List of epoch numbers
    """
    # Try multiple patterns for checkpoint files
    checkpoint_paths = list(Path(checkpoint_dir).glob('epoch_*.pt'))
    if len(checkpoint_paths) == 0:
        checkpoint_paths = list(Path(checkpoint_dir).glob('*_epoch_*.pth'))
    if len(checkpoint_paths) == 0:
        checkpoint_paths = list(Path(checkpoint_dir).glob('*_epoch_*.pt'))

    checkpoint_paths = sorted(checkpoint_paths)

    if len(checkpoint_paths) == 0:
        raise FileNotFoundError(f"No checkpoints found in {checkpoint_dir}")

    ami_values = []
    epochs = []

    for ckpt_path in checkpoint_paths:
        # Extract epoch number from filename (handle both formats)
        stem = ckpt_path.stem
        if 'epoch' in stem:
            parts = stem.split('_')
            epoch_idx = parts.index('epoch') + 1 if 'epoch' in parts else -1
            if epoch_idx > 0 and epoch_idx < len(parts):
                epoch = int(parts[epoch_idx])
            else:
                epoch = int(parts[-1])  # Last part should be the number
        else:
            continue  # Skip files without epoch in name
        epochs.append(epoch)

        # Extract embeddings
        embeddings, _, groups = load_checkpoint_and_extract(str(ckpt_path), device, split='test')

        # Compute AMI
        from sklearn.cluster import KMeans
        from sklearn.metrics import adjusted_mutual_info_score

        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
        ami = adjusted_mutual_info_score(groups, cluster_labels)

        ami_values.append(ami)
        print(f"Epoch {epoch}: AMI = {ami:.4f}")

    return ami_values, epochs


def compute_delta_wga_evolution(checkpoint_dir, device):
    """Compute ΔWGA from cluster-balanced retraining across checkpoints.

    Args:
        checkpoint_dir: Directory containing checkpoints
        device: Device to run on

    Returns:
        delta_wga_values: List of ΔWGA improvements (in percentage points)
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score
    from sklearn.cluster import KMeans

    # Try multiple patterns for checkpoint files
    checkpoint_paths = list(Path(checkpoint_dir).glob('epoch_*.pt'))
    if len(checkpoint_paths) == 0:
        checkpoint_paths = list(Path(checkpoint_dir).glob('*_epoch_*.pth'))
    if len(checkpoint_paths) == 0:
        checkpoint_paths = list(Path(checkpoint_dir).glob('*_epoch_*.pt'))

    checkpoint_paths = sorted(checkpoint_paths)
    delta_wga_values = []

    for ckpt_path in checkpoint_paths:
        print(f"Computing ΔWGA for {ckpt_path.name}...")

        # Extract embeddings from train and test splits
        train_embeddings, train_labels, train_groups = load_checkpoint_and_extract(
            str(ckpt_path), device, split='train'
        )
        test_embeddings, test_labels, test_groups = load_checkpoint_and_extract(
            str(ckpt_path), device, split='test'
        )

        # Baseline ERM
        clf_erm = LogisticRegression(max_iter=1000, random_state=42)
        clf_erm.fit(train_embeddings, train_labels)
        preds_erm = clf_erm.predict(test_embeddings)

        # Compute WGA for baseline
        group_accs_erm = []
        for g in range(4):
            mask = test_groups == g
            if mask.sum() > 0:
                acc = accuracy_score(test_labels[mask], preds_erm[mask])
                group_accs_erm.append(acc)
        wga_erm = min(group_accs_erm) if len(group_accs_erm) > 0 else 0.0

        # Cluster-balanced retraining
        # (Simplified - reweight by cluster membership)
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(train_embeddings)

        # Compute cluster weights
        cluster_counts = np.bincount(cluster_labels, minlength=4)
        cluster_weights = 1.0 / (cluster_counts + 1e-6)
        sample_weights = cluster_weights[cluster_labels]
        sample_weights /= sample_weights.sum()

        # Train with cluster balancing
        clf_cb = LogisticRegression(max_iter=1000, random_state=42)
        clf_cb.fit(train_embeddings, train_labels, sample_weight=sample_weights)
        preds_cb = clf_cb.predict(test_embeddings)

        # Compute WGA for cluster-balanced
        group_accs_cb = []
        for g in range(4):
            mask = test_groups == g
            if mask.sum() > 0:
                acc = accuracy_score(test_labels[mask], preds_cb[mask])
                group_accs_cb.append(acc)
        wga_cb = min(group_accs_cb) if len(group_accs_cb) > 0 else 0.0

        # Compute improvement
        delta_wga = (wga_cb - wga_erm) * 100  # Convert to percentage points
        delta_wga_values.append(delta_wga)
        print(f"  WGA_ERM: {wga_erm*100:.2f}%, WGA_CB: {wga_cb*100:.2f}%, ΔWGA: {delta_wga:.2f}pp")

    return delta_wga_values


def main():
    """Run validation suite with real trained models."""
    print("=" * 60)
    print("Mechanism Validation Suite (h-m-integrated)")
    print("=" * 60)

    device = ENVIRONMENT_CONFIG['device']
    print(f"Using device: {device}\n")

    # Paths to trained checkpoints
    simclr_checkpoint_dir = Path(ENVIRONMENT_CONFIG['checkpoint_dir']) / 'simclr' / 'seed_0'
    lassl_checkpoint_dir = Path(ENVIRONMENT_CONFIG['checkpoint_dir']) / 'lassl' / 'seed_0'

    # Check if checkpoints exist
    simclr_final = simclr_checkpoint_dir / 'final.pt'
    lassl_final = lassl_checkpoint_dir / 'final.pt'

    if not simclr_final.exists():
        raise FileNotFoundError(
            f"SimCLR checkpoint not found: {simclr_final}\n"
            "Please run run_simclr.py first to train SimCLR baseline."
        )

    if not lassl_final.exists():
        raise FileNotFoundError(
            f"LA-SSL checkpoint not found: {lassl_final}\n"
            "Please run run_lassl.py first to train LA-SSL."
        )

    # Extract embeddings from final checkpoints
    print("[M1] Extracting SimCLR embeddings from trained model...")
    print("-" * 60)
    embeddings_simclr, _, groups = load_checkpoint_and_extract(str(simclr_final), device, split='test')
    print(f"Extracted {len(embeddings_simclr)} embeddings\n")

    print("[M3] Extracting LA-SSL embeddings from trained model...")
    print("-" * 60)
    embeddings_lassl, _, _ = load_checkpoint_and_extract(str(lassl_final), device, split='test')
    print(f"Extracted {len(embeddings_lassl)} embeddings\n")

    # M1: Validate InfoNCE creates clusters
    print("[M1] Validating InfoNCE Creates Clusters...")
    print("-" * 60)
    m1_result = validate_m1(
        embeddings=embeddings_simclr,
        groups=groups,
        ami_threshold=VALIDATION_CONFIG['ami_threshold'],
        silhouette_threshold=VALIDATION_CONFIG['silhouette_threshold']
    )
    print(f"AMI Score: {m1_result['ami_score']:.4f}")
    print(f"Silhouette Score: {m1_result['silhouette_score']:.4f}")
    print(f"Gate Status: {'✅ PASS' if m1_result['gate_pass'] else '❌ FAIL'}\n")

    # M2: Compute AMI evolution and ΔWGA correlation
    print("[M2] Computing AMI Evolution and ΔWGA Correlation...")
    print("-" * 60)

    # Extract AMI values across checkpoints
    ami_values, epochs = compute_ami_evolution_from_checkpoints(
        simclr_checkpoint_dir, device
    )

    # Compute ΔWGA evolution
    delta_wga_values = compute_delta_wga_evolution(
        simclr_checkpoint_dir, device
    )

    # Validate M2
    m2_result = validate_m2(
        ami_values=ami_values,
        delta_wga_values=delta_wga_values,
        ami_threshold=VALIDATION_CONFIG['ami_threshold'],
        delta_wga_threshold=VALIDATION_CONFIG['delta_wga_threshold'],
        pvalue_threshold=VALIDATION_CONFIG['correlation_pvalue']
    )
    print(f"Correlation: {m2_result['correlation']:.4f}")
    print(f"P-value: {m2_result['pvalue']:.6f}")
    print(f"High-AMI ΔWGA: {m2_result['high_ami_mean_delta_wga']:.2f}pp")
    print(f"Gate Status: {'✅ PASS' if m2_result['gate_pass'] else '❌ FAIL'}\n")

    # M3: Validate LA-SSL disperses clusters
    print("[M3] Validating LA-SSL Disperses Clusters...")
    print("-" * 60)

    # Compute AMI for both methods at final epoch
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_mutual_info_score

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)

    cluster_labels_simclr = kmeans.fit_predict(embeddings_simclr)
    ami_simclr = adjusted_mutual_info_score(groups, cluster_labels_simclr)

    cluster_labels_lassl = kmeans.fit_predict(embeddings_lassl)
    ami_lassl = adjusted_mutual_info_score(groups, cluster_labels_lassl)

    # Compute linear separability
    auc_simclr = compute_linear_separability(embeddings_simclr, groups)
    auc_lassl = compute_linear_separability(embeddings_lassl, groups)

    m3_result = validate_m3(
        ami_simclr=ami_simclr,
        ami_lassl=ami_lassl,
        auc_simclr=auc_simclr,
        auc_lassl=auc_lassl,
        reduction_threshold=VALIDATION_CONFIG['ami_reduction_threshold'],
        auc_threshold=VALIDATION_CONFIG['auc_delta_threshold']
    )
    print(f"SimCLR AMI: {ami_simclr:.4f}")
    print(f"LA-SSL AMI: {ami_lassl:.4f}")
    print(f"AMI Reduction: {m3_result['ami_reduction']*100:.1f}%")
    print(f"AUC Delta: {m3_result['auc_delta']:.4f}")
    print(f"Gate Status: {'✅ PASS' if m3_result['gate_pass'] else '❌ FAIL'}\n")

    # Generate report
    print("=" * 60)
    print("Generating Mechanism Validation Report...")
    print("=" * 60)

    report_path = '../04_validation.md'
    generate_mechanism_report(m1_result, m2_result, m3_result, report_path)

    # Save metrics to JSON (convert numpy types to python types)
    def convert_to_python(obj):
        if isinstance(obj, dict):
            return {k: convert_to_python(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_to_python(x) for x in obj]
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    metrics = {
        'm1': {k: v for k, v in m1_result.items() if k != 'cluster_labels'},
        'm2': m2_result,
        'm3': m3_result,
        'overall_gate_pass': bool(m1_result['gate_pass'] and m2_result['gate_pass']),
        'ami_evolution': {
            'epochs': epochs,
            'ami_values': ami_values,
            'delta_wga_values': delta_wga_values
        }
    }

    metrics = convert_to_python(metrics)

    metrics_path = '../results/mechanism_metrics.json'
    Path('../results').mkdir(exist_ok=True)
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n✓ Validation report: {report_path}")
    print(f"✓ Metrics JSON: {metrics_path}")

    # Overall verdict
    print("\n" + "=" * 60)
    print("OVERALL GATE VERDICT")
    print("=" * 60)
    primary_pass = m1_result['gate_pass'] and m2_result['gate_pass']
    print(f"Primary Gates (M1+M2): {'✅ PASS' if primary_pass else '❌ FAIL'}")
    print(f"Secondary Gate (M3): {'✅ PASS' if m3_result['gate_pass'] else '❌ FAIL'}")
    print(f"\nHypothesis Status: {'VALIDATED' if primary_pass else 'FAILED'}")

    return 0 if primary_pass else 1


if __name__ == '__main__':
    exit(main())
