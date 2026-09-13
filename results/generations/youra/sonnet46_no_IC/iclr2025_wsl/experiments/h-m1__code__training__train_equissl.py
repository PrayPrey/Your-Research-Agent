"""
EquiSSL SSL training loop: lambda sweep + best-lambda selection.
"""
import os
import sys
import csv
import time
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader as TorchDataLoader
from torch_geometric.data import Batch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from data.multizoo_graph_dataset import MultiZooGraphDataset
from data.augmentations import make_positive_pair
from models.equissl_encoder import EquiSSLEncoder
from models.graph_decoder import GraphDecoder
from models.equissl_objective import EquiSSLObjective


def seed_worker(worker_id):
    import numpy as np, random
    seed = torch.initial_seed() % (2**32)
    np.random.seed(seed)
    random.seed(seed)


def collate_augmented(batch):
    """Collate function that creates positive pairs for each graph."""
    graphs_a, graphs_b = [], []
    for g in batch:
        a, b = make_positive_pair(g)
        graphs_a.append(a)
        graphs_b.append(b)
    return Batch.from_data_list(graphs_a), Batch.from_data_list(graphs_b)


def train_one_epoch(model: nn.Module, loader, optimizer, device) -> dict:
    model.train()
    total_loss = 0.0
    n_batches = 0

    for batch_a, batch_b in loader:
        batch_a = batch_a.to(device)
        batch_b = batch_b.to(device)

        optimizer.zero_grad()
        loss, _ = model(batch_a, batch_b)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 10.0)
        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return {'loss': total_loss / max(n_batches, 1)}


def eval_recon_loss(model: nn.Module, loader, device) -> float:
    """Compute validation reconstruction loss for lambda selection."""
    model.eval()
    total_loss = 0.0
    n_batches = 0

    with torch.no_grad():
        for batch_a, batch_b in loader:
            batch_a = batch_a.to(device)
            batch_b = batch_b.to(device)
            loss, _ = model(batch_a, batch_b)
            total_loss += loss.item()
            n_batches += 1

    return total_loss / max(n_batches, 1)


def train_equissl(lam: float, seed: int, data_root: str, checkpoint_dir: str,
                  device: str = 'cuda', epochs: int = None,
                  n_train_models: int = None) -> str:
    """Train EquiSSL for given lambda and seed. Returns path to best checkpoint."""
    torch.manual_seed(seed)
    if epochs is None:
        epochs = config.EPOCHS

    os.makedirs(checkpoint_dir, exist_ok=True)

    # Dataset
    train_dataset = MultiZooGraphDataset(
        root=data_root, normalize=True, split='train',
        val_fraction=config.VAL_FRACTION, seed=seed,
        max_models=n_train_models
    )
    val_dataset = MultiZooGraphDataset(
        root=data_root, normalize=True, split='val',
        val_fraction=config.VAL_FRACTION, seed=seed,
        max_models=n_train_models
    )

    g = torch.Generator()
    g.manual_seed(seed)

    train_loader = TorchDataLoader(
        train_dataset, batch_size=config.BATCH_SIZE, shuffle=True,
        collate_fn=collate_augmented, num_workers=2,
        worker_init_fn=seed_worker, generator=g,
        drop_last=True  # NT-Xent needs >1 sample
    )
    val_loader = TorchDataLoader(
        val_dataset, batch_size=config.BATCH_SIZE, shuffle=False,
        collate_fn=collate_augmented, num_workers=2, drop_last=True
    )

    if len(train_dataset) < 2:
        raise ValueError(f"Too few training samples: {len(train_dataset)}")

    device = torch.device(device if torch.cuda.is_available() else 'cpu')

    # Model
    encoder = EquiSSLEncoder(
        node_in_dim=4, edge_in_dim=4,
        hidden_dim=config.HIDDEN_DIM, latent_dim=config.LATENT_DIM,
        num_layers=config.NUM_LAYERS
    ).to(device)
    decoder = GraphDecoder(
        latent_dim=config.LATENT_DIM, hidden_dim=config.HIDDEN_DIM
    ).to(device)
    objective = EquiSSLObjective(encoder, decoder, config.TEMPERATURE, lam=lam).to(device)

    optimizer = Adam(objective.parameters(), lr=config.LR,
                     weight_decay=config.WEIGHT_DECAY, betas=config.BETAS)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=config.ETA_MIN)

    # CSV log
    csv_path = os.path.join(checkpoint_dir, f'training_log_lam{lam}_seed{seed}.csv')
    best_val_loss = float('inf')
    best_ckpt_path = None

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['epoch', 'ntxent_loss', 'val_loss'])

    for epoch in range(1, epochs + 1):
        train_stats = train_one_epoch(objective, train_loader, optimizer, device)
        val_loss = eval_recon_loss(objective, val_loader, device)
        scheduler.step()

        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([epoch, train_stats['loss'], val_loss])

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_ckpt_path = os.path.join(checkpoint_dir, f'equissl_lam{lam}_seed{seed}_best.pt')
            torch.save({
                'epoch': epoch,
                'encoder_state_dict': encoder.state_dict(),
                'decoder_state_dict': decoder.state_dict(),
                'val_loss': val_loss,
                'lam': lam,
                'seed': seed,
            }, best_ckpt_path)

        if epoch % 10 == 0:
            print(f'  [lam={lam}, seed={seed}] Epoch {epoch}/{epochs}: '
                  f'train_loss={train_stats["loss"]:.4f}, val_loss={val_loss:.4f}')

    return best_ckpt_path


def run_lambda_sweep(seed: int, data_root: str, checkpoint_dir: str,
                     device: str = 'cuda', lambda_list=None,
                     epochs: int = None, n_train_models: int = None) -> dict:
    """Train all lambda values; return {lam: best_ckpt_path}."""
    if lambda_list is None:
        lambda_list = config.LAMBDA_SWEEP
    results = {}
    for lam in lambda_list:
        print(f'\n--- Lambda sweep: lam={lam}, seed={seed} ---')
        ckpt_path = train_equissl(
            lam=lam, seed=seed, data_root=data_root,
            checkpoint_dir=checkpoint_dir, device=device,
            epochs=epochs, n_train_models=n_train_models
        )
        results[lam] = ckpt_path
    return results


def select_best_lambda(sweep_results: dict, val_dataset_or_loader, device: str = 'cuda') -> tuple:
    """Pick lambda with lowest validation loss. Returns (best_lam, best_ckpt_path)."""
    device = torch.device(device if torch.cuda.is_available() else 'cpu')
    best_lam = None
    best_loss = float('inf')

    for lam, ckpt_path in sweep_results.items():
        if ckpt_path is None or not os.path.exists(ckpt_path):
            continue
        ckpt = torch.load(ckpt_path, map_location=device)
        val_loss = ckpt.get('val_loss', float('inf'))
        if val_loss < best_loss:
            best_loss = val_loss
            best_lam = lam

    best_ckpt = sweep_results.get(best_lam)
    return best_lam, best_ckpt


def load_encoder_from_checkpoint(ckpt_path: str, device: str = 'cuda') -> EquiSSLEncoder:
    """Load encoder from checkpoint."""
    device = torch.device(device if torch.cuda.is_available() else 'cpu')
    ckpt = torch.load(ckpt_path, map_location=device)
    encoder = EquiSSLEncoder(
        node_in_dim=4, edge_in_dim=4,
        hidden_dim=config.HIDDEN_DIM, latent_dim=config.LATENT_DIM,
        num_layers=config.NUM_LAYERS
    ).to(device)
    encoder.load_state_dict(ckpt['encoder_state_dict'])
    encoder.eval()
    return encoder
