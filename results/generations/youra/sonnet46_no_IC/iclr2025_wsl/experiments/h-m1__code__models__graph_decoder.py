"""
Graph Decoder: reconstructs edge_attr from latent z.
Used for the MSE reconstruction term in the EquiSSL objective.
"""
import torch
import torch.nn as nn


class GraphDecoder(nn.Module):
    """Decode latent z to edge_attr (flattened weights)."""

    def __init__(self, latent_dim: int = 128, hidden_dim: int = 256,
                 max_edge_dim: int = 512):
        super().__init__()
        self.max_edge_dim = max_edge_dim
        self.mlp = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, max_edge_dim),
        )

    def forward(self, z: torch.Tensor, structure: dict) -> torch.Tensor:
        """
        Reconstruct edge_attr from z.
        Returns tensor of shape (B, max_edge_dim) or (N_edges_total, 1) depending on mode.
        For MSE loss, we decode to a fixed-size vector and compute loss vs mean-pooled edge_attr.
        """
        # Decode to max_edge_dim vector per graph
        out = self.mlp(z)  # (B, max_edge_dim)
        return out
