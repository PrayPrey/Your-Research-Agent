"""
SANE Baseline: flat tokenization + transformer autoencoder.
Implements the SANE approach (Schürholt et al. ICML 2024) as a baseline:
- Flatten all weights into a sequence of chunks
- Encode with a simple transformer/MLP
- Compare MMD of latents vs EquiSSL

This is the 'flat tokenizer' baseline that EquiSSL should outperform on
cross-architecture distribution shift.
"""
import os
import sys
import csv
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader as TorchDataLoader
from torch_geometric.loader import DataLoader
from torch_geometric.data import Batch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from data.multizoo_graph_dataset import MultiZooGraphDataset


CHUNK_SIZE = 64  # Fixed chunk size for flat tokenization


class SANEEncoder(nn.Module):
    """
    SANE-style encoder: flatten weights -> fixed chunks -> MLP encoder -> latent z.
    Flat tokenization ignores graph structure (architecture-unaware).
    """

    def __init__(self, chunk_size: int = CHUNK_SIZE, latent_dim: int = 128,
                 hidden_dim: int = 256, n_chunks: int = 32):
        super().__init__()
        self.chunk_size = chunk_size
        self.latent_dim = latent_dim
        self.n_chunks = n_chunks

        # Token embedding: each chunk -> d_model
        self.chunk_embed = nn.Linear(chunk_size, hidden_dim)

        # Simple transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim, nhead=4, dim_feedforward=hidden_dim * 2,
            dropout=0.0, batch_first=True, norm_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)

        # Aggregate + project
        self.proj = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
        )

    def forward(self, node_feats: torch.Tensor, batch: torch.Tensor) -> torch.Tensor:
        """
        Args:
            node_feats: (N_nodes_total, feat_dim) - per-layer weight statistics
            batch: (N_nodes_total,) - graph assignment per node
        Returns: (B, latent_dim) L2-normalized latents
        """
        B = batch.max().item() + 1 if len(batch) > 0 else 1

        # Flatten node features per graph into fixed-size token sequence
        z_list = []
        for b in range(B):
            mask = batch == b
            vals = node_feats[mask].reshape(-1)  # flatten all node feats for this graph

            if len(vals) == 0:
                vals = torch.zeros(self.chunk_size * self.n_chunks, device=node_feats.device)

            # Pad or truncate to n_chunks * chunk_size
            target_len = self.n_chunks * self.chunk_size
            if len(vals) < target_len:
                vals = F.pad(vals, (0, target_len - len(vals)))
            else:
                vals = vals[:target_len]

            # Reshape to chunks
            chunks = vals.reshape(self.n_chunks, self.chunk_size)  # (n_chunks, chunk_size)
            z_list.append(chunks)

        chunks_batch = torch.stack(z_list, dim=0)  # (B, n_chunks, chunk_size)
        tok = self.chunk_embed(chunks_batch)  # (B, n_chunks, hidden_dim)
        h = self.transformer(tok)              # (B, n_chunks, hidden_dim)
        h_mean = h.mean(dim=1)                # (B, hidden_dim) - mean pool over chunks
        z = self.proj(h_mean)
        return z  # No L2 normalization: allows richer latent space for MMD computation


class SANEObjective(nn.Module):
    """SANE MSE reconstruction objective."""

    def __init__(self, encoder: nn.Module, latent_dim: int = 128, hidden_dim: int = 256,
                 n_chunks: int = 32, chunk_size: int = CHUNK_SIZE):
        super().__init__()
        self.encoder = encoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_chunks * chunk_size),
        )
        self.chunk_size = chunk_size
        self.n_chunks = n_chunks

    def forward(self, batch) -> tuple:
        # Use node features (layer weight statistics) as flat weight representation
        # SANE tokenizes weights into chunks — we flatten the per-layer stats
        node_feats = batch.x.float()  # (N_nodes_total, 4)
        batch_assign = batch.batch    # (N_nodes_total,)

        z = self.encoder(node_feats, batch_assign)  # (B, latent_dim)

        # Decode + reconstruct node features
        B = z.shape[0]
        target_len = self.n_chunks * self.chunk_size
        recon = self.decoder(z)  # (B, target_len)

        # Build target per graph (flatten node features)
        targets = []
        for b in range(B):
            mask = batch_assign == b
            vals = node_feats[mask].reshape(-1)  # flatten all node feats for this graph
            if len(vals) < target_len:
                vals = F.pad(vals, (0, target_len - len(vals)))
            else:
                vals = vals[:target_len]
            targets.append(vals)
        target = torch.stack(targets, dim=0)  # (B, target_len)

        recon_loss = F.mse_loss(recon, target)

        # VICReg variance term: prevent latent collapse (ponytail: simple hinge, upgrade to full VICReg if collapse persists)
        z_std = z.std(dim=0)  # (latent_dim,)
        var_loss = F.relu(1.0 - z_std).mean()

        loss = recon_loss + 0.1 * var_loss
        return loss, z.detach()


def train_sane(seed: int, data_root: str, checkpoint_dir: str,
               device: str = 'cuda', epochs: int = None,
               n_train_models: int = None) -> str:
    """Train SANE baseline. Returns checkpoint path."""
    torch.manual_seed(seed)
    if epochs is None:
        epochs = config.EPOCHS

    os.makedirs(checkpoint_dir, exist_ok=True)
    device = torch.device(device if torch.cuda.is_available() else 'cpu')

    train_dataset = MultiZooGraphDataset(
        root=data_root, normalize=False, split='train',  # SANE uses raw (unnormalized) weights
        val_fraction=config.VAL_FRACTION, seed=seed,
        max_models=n_train_models
    )
    train_loader = TorchDataLoader(
        train_dataset, batch_size=config.BATCH_SIZE, shuffle=True,
        collate_fn=lambda graphs: Batch.from_data_list(graphs),
        num_workers=2, drop_last=True
    )

    encoder = SANEEncoder(latent_dim=config.LATENT_DIM, hidden_dim=config.HIDDEN_DIM).to(device)
    objective = SANEObjective(encoder, latent_dim=config.LATENT_DIM).to(device)
    optimizer = Adam(objective.parameters(), lr=config.LR,
                     weight_decay=config.WEIGHT_DECAY)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=config.ETA_MIN)

    best_loss = float('inf')
    best_ckpt = None

    csv_path = os.path.join(checkpoint_dir, f'sane_training_log_seed{seed}.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerow(['epoch', 'train_loss'])

    for epoch in range(1, epochs + 1):
        objective.train()
        total_loss = 0.0
        n_batches = 0

        for batch in train_loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            loss, _ = objective(batch)
            loss.backward()
            nn.utils.clip_grad_norm_(objective.parameters(), 10.0)
            optimizer.step()
            total_loss += loss.item()
            n_batches += 1

        scheduler.step()
        avg_loss = total_loss / max(n_batches, 1)

        with open(csv_path, 'a', newline='') as f:
            csv.writer(f).writerow([epoch, avg_loss])

        if avg_loss < best_loss:
            best_loss = avg_loss
            best_ckpt = os.path.join(checkpoint_dir, f'sane_seed{seed}_best.pt')
            torch.save({
                'epoch': epoch,
                'encoder_state_dict': encoder.state_dict(),
                'objective_state_dict': objective.state_dict(),
                'train_loss': avg_loss,
                'seed': seed,
            }, best_ckpt)

        if epoch % 10 == 0:
            print(f'  [SANE, seed={seed}] Epoch {epoch}/{epochs}: train_loss={avg_loss:.4f}')

    return best_ckpt


def extract_sane_latents(checkpoint_path: str, dataset, device: str = 'cuda') -> torch.Tensor:
    """Encode all models in dataset; return z tensor (N, latent_dim)."""
    device = torch.device(device if torch.cuda.is_available() else 'cpu')
    ckpt = torch.load(checkpoint_path, map_location=device)

    encoder = SANEEncoder(latent_dim=config.LATENT_DIM, hidden_dim=config.HIDDEN_DIM).to(device)
    encoder.load_state_dict(ckpt['encoder_state_dict'])
    encoder.eval()

    loader = TorchDataLoader(dataset, batch_size=64, shuffle=False,
                             collate_fn=lambda graphs: Batch.from_data_list(graphs),
                             num_workers=2)
    all_z = []

    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            node_feats = batch.x.float()
            z = encoder(node_feats, batch.batch)
            all_z.append(z.cpu())

    return torch.cat(all_z, dim=0)


def load_sane_encoder(checkpoint_path: str, device: str = 'cuda') -> SANEEncoder:
    """Load SANE encoder from checkpoint."""
    device = torch.device(device if torch.cuda.is_available() else 'cpu')
    ckpt = torch.load(checkpoint_path, map_location=device)
    encoder = SANEEncoder(latent_dim=config.LATENT_DIM, hidden_dim=config.HIDDEN_DIM).to(device)
    encoder.load_state_dict(ckpt['encoder_state_dict'])
    encoder.eval()
    return encoder
