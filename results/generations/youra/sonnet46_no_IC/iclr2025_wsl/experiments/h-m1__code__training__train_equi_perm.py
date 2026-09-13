"""
EquiSSL-perm training: permutation-only augmentation (ablation variable vs H-E1 EquiSSL).
Uses perm_augment ONLY — no scale_augment. Everything else identical to H-E1.
"""
import os
import sys
import csv
import random
import numpy as np
import torch
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch_geometric.data import Batch

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H_E1_CODE = os.environ.get('H_E1_CODE',
    '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl/docs/youra_research/h-e1/code')
# Add H_E1 BEFORE code dir so H_M1 modules (already in sys.path[0]) take priority
if H_E1_CODE not in sys.path:
    sys.path.append(H_E1_CODE)  # append, not insert — don't shadow H_M1 modules

import config
from models.equissl_encoder import EquiSSLEncoder
from models.graph_decoder import GraphDecoder
from models.equissl_objective import EquiSSLObjective, nt_xent_loss
import torch.nn.functional as F
from torch_geometric.nn import global_mean_pool


def perm_only_pair(graph):
    """Create positive pair using perm_augment ONLY (no scale_augment)."""
    from data.augmentations import perm_augment
    return perm_augment(graph), perm_augment(graph)


def collate_perm_only(batch):
    """Collate with permutation-only augmentation."""
    graphs_a, graphs_b = [], []
    for g in batch:
        a, b = perm_only_pair(g)
        graphs_a.append(a)
        graphs_b.append(b)
    return Batch.from_data_list(graphs_a), Batch.from_data_list(graphs_b)


def seed_worker(worker_id):
    seed = torch.initial_seed() % (2**32)
    np.random.seed(seed)
    random.seed(seed)


def compute_loss(encoder, decoder, batch_a, batch_b, lam, temperature):
    """Compute NT-Xent + lambda_rec * MSE loss matching H-E1's EquiSSLObjective."""
    z_a = encoder(batch_a)
    z_b = encoder(batch_b)

    contrastive = nt_xent_loss(z_a, z_b, temperature)

    # Reconstruction: decode z_a vs mean-pooled edge_attr of batch_a
    if batch_a.edge_attr is not None and batch_a.edge_attr.shape[0] > 0:
        src = batch_a.edge_index[0]
        edge_batch = batch_a.batch[src]
        edge_mean = global_mean_pool(batch_a.edge_attr.float(), edge_batch)
        edge_dim = edge_mean.shape[1]
        recon = decoder(z_a, None)
        recon_trunc = recon[:, :edge_dim]
        mse = F.mse_loss(recon_trunc, edge_mean)
    else:
        mse = torch.tensor(0.0, device=z_a.device)

    return contrastive + lam * mse


def train_equi_perm(seed, checkpoint_dir, results_dir, multizoo_root,
                    device='cuda', epochs=None):
    """Train EquiSSL-perm for one seed. Returns path to best checkpoint."""
    if epochs is None:
        epochs = config.EPOCHS

    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

    os.makedirs(checkpoint_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    from data.multizoo_graph_dataset import MultiZooGraphDataset
    train_ds = MultiZooGraphDataset(root=multizoo_root, normalize=True, split='train')
    val_ds = MultiZooGraphDataset(root=multizoo_root, normalize=True, split='val')

    g_tr = torch.Generator(); g_tr.manual_seed(seed)
    train_loader = torch.utils.data.DataLoader(
        train_ds, batch_size=config.BATCH_SIZE, shuffle=True,
        collate_fn=collate_perm_only, num_workers=4,
        worker_init_fn=seed_worker, generator=g_tr)
    val_loader = torch.utils.data.DataLoader(
        val_ds, batch_size=config.BATCH_SIZE, shuffle=False,
        collate_fn=collate_perm_only, num_workers=2)

    encoder = EquiSSLEncoder(
        node_in_dim=4, edge_in_dim=4,
        hidden_dim=config.HIDDEN_DIM, latent_dim=config.LATENT_DIM,
        num_layers=config.NUM_LAYERS, symmetry='permutation'
    ).to(device)
    decoder = GraphDecoder(latent_dim=config.LATENT_DIM,
                           hidden_dim=config.HIDDEN_DIM).to(device)

    optimizer = Adam(
        list(encoder.parameters()) + list(decoder.parameters()),
        lr=config.LR, weight_decay=config.WEIGHT_DECAY, betas=config.BETAS)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=config.ETA_MIN)

    log_path = os.path.join(results_dir, f'training_log_equi_perm_seed{seed}.csv')
    best_ckpt = os.path.join(checkpoint_dir, f'equi_perm_seed{seed}.pt')
    best_loss = float('inf')

    with open(log_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['epoch', 'train_loss', 'val_loss', 'lr'])

        for epoch in range(1, epochs + 1):
            encoder.train(); decoder.train()
            total_loss, n_batches = 0.0, 0
            for batch_a, batch_b in train_loader:
                batch_a = batch_a.to(device)
                batch_b = batch_b.to(device)
                loss = compute_loss(encoder, decoder, batch_a, batch_b,
                                    config.LAMBDA_REC, config.TEMPERATURE)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
                n_batches += 1
            avg_loss = total_loss / max(n_batches, 1)

            encoder.eval(); decoder.eval()
            val_loss, n_val = 0.0, 0
            with torch.no_grad():
                for batch_a, batch_b in val_loader:
                    batch_a = batch_a.to(device)
                    batch_b = batch_b.to(device)
                    loss = compute_loss(encoder, decoder, batch_a, batch_b,
                                        config.LAMBDA_REC, config.TEMPERATURE)
                    val_loss += loss.item()
                    n_val += 1
            avg_val = val_loss / max(n_val, 1)

            scheduler.step()
            lr = scheduler.get_last_lr()[0]
            writer.writerow([epoch, avg_loss, avg_val, lr])

            if avg_val < best_loss:
                best_loss = avg_val
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': encoder.state_dict(),
                    'decoder_state_dict': decoder.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'loss': avg_val,
                    'config': {'symmetry': 'permutation', 'seed': seed,
                               'lambda_rec': config.LAMBDA_REC}
                }, best_ckpt)

            if epoch % 10 == 0 or epoch == 1:
                print(f'  [seed={seed}] epoch {epoch:3d}/{epochs} '
                      f'train={avg_loss:.4f} val={avg_val:.4f} '
                      f'lr={lr:.2e} best={best_loss:.4f}')
            if epoch == 10 and avg_loss > 10.0:
                print(f'  WARNING: loss not decreasing (seed={seed})')
            if epoch % 10 == 0:
                ep_ckpt = os.path.join(checkpoint_dir,
                    f'equi_perm_seed{seed}_ep{epoch}.pt')
                torch.save({'epoch': epoch, 'model_state_dict': encoder.state_dict(),
                            'loss': avg_loss}, ep_ckpt)

    print(f'  [seed={seed}] Done. Best val loss: {best_loss:.4f} -> {best_ckpt}')
    return best_ckpt


def train_all_seeds(seeds, checkpoint_dir, results_dir, multizoo_root,
                    device='cuda', epochs=None):
    paths = []
    for seed in seeds:
        print(f'\n=== EquiSSL-perm seed={seed} ===')
        ckpt = train_equi_perm(seed, checkpoint_dir, results_dir,
                               multizoo_root, device, epochs)
        paths.append(ckpt)
    return paths
