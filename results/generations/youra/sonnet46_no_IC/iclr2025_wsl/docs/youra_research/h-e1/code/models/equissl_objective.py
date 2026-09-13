"""
EquiSSL combined loss: NT-Xent contrastive + lambda * MSE reconstruction.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import global_mean_pool


def nt_xent_loss(z_a: torch.Tensor, z_b: torch.Tensor,
                 temperature: float = 0.07) -> torch.Tensor:
    """SimCLR NT-Xent contrastive loss on 2B samples."""
    B = z_a.shape[0]
    z = torch.cat([z_a, z_b], dim=0)  # (2B, D)
    sim = z @ z.T / temperature         # (2B, 2B)

    # Mask self-similarity
    mask = torch.eye(2 * B, dtype=torch.bool, device=z.device)
    sim = sim.masked_fill(mask, -1e9)

    # Labels: (i, i+B) are positive pairs
    labels = torch.cat([
        torch.arange(B, 2 * B),
        torch.arange(B)
    ]).to(z.device)

    loss = F.cross_entropy(sim, labels)
    return loss


class EquiSSLObjective(nn.Module):
    """Combined SSL objective: NT-Xent + lambda * MSE reconstruction."""

    def __init__(self, encoder: nn.Module, decoder: nn.Module,
                 temperature: float = 0.07, lam: float = 0.1):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.temperature = temperature
        self.lam = lam

    def forward(self, graph_a: Data, graph_b: Data) -> tuple:
        """Returns (total_loss scalar, z_a detached (B, latent_dim))."""
        z_a = self.encoder(graph_a)  # (B, latent_dim)
        z_b = self.encoder(graph_b)  # (B, latent_dim)

        contrastive = nt_xent_loss(z_a, z_b, self.temperature)

        # Reconstruction: decode z_a, compare to mean-pooled edge_attr of graph_a
        # This tests if z captures weight distribution information
        batch_a = graph_a.batch if hasattr(graph_a, 'batch') and graph_a.batch is not None else \
            torch.zeros(graph_a.x.shape[0], dtype=torch.long, device=z_a.device)

        if graph_a.edge_attr is not None and graph_a.edge_attr.shape[0] > 0:
            # Pool edge_attr per graph for target signal (per-graph mean of all edge features)
            src = graph_a.edge_index[0]
            edge_batch = batch_a[src]
            edge_mean = global_mean_pool(graph_a.edge_attr.float(), edge_batch)  # (B, edge_dim)
            edge_dim = edge_mean.shape[1]

            # Decode z_a to reconstruct edge statistics
            recon = self.decoder(z_a, graph_a.structure)  # (B, max_edge_dim)
            # Use only first edge_dim dimensions of decoder output
            recon_trunc = recon[:, :edge_dim]
            mse_recon = F.mse_loss(recon_trunc, edge_mean)
        else:
            mse_recon = torch.tensor(0.0, device=z_a.device)

        total_loss = contrastive + self.lam * mse_recon
        return total_loss, z_a.detach()
