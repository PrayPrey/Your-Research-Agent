"""Slot-Equivariant encoder with architecture embeddings"""

import torch
import torch.nn as nn


class ArchitectureEmbedder(nn.Module):
    """Embed architecture family (CNN/Transformer/RNN)"""

    def __init__(self, num_classes: int = 3, embed_dim: int = 64):
        super().__init__()
        self.embedding = nn.Embedding(num_classes, embed_dim)

    def forward(self, arch_labels: torch.Tensor) -> torch.Tensor:
        """
        Args:
            arch_labels: [B] architecture indices
        Returns:
            [B, embed_dim] embeddings
        """
        return self.embedding(arch_labels)


class SlotEquivariantEncoder(nn.Module):
    """Deep Sets encoder with equivariance constraints"""

    def __init__(
        self,
        weight_dim: int,
        K: int = 32,
        hidden_dim: int = 256,
        num_arch_classes: int = 3,
        arch_embed_dim: int = 64
    ):
        super().__init__()
        self.weight_dim = weight_dim
        self.K = K
        self.hidden_dim = hidden_dim

        # Architecture embedding
        self.arch_embedder = ArchitectureEmbedder(num_arch_classes, arch_embed_dim)

        # Per-element encoder (phi)
        self.phi = nn.Sequential(
            nn.Linear(weight_dim + arch_embed_dim, 256),
            nn.ReLU(),
            nn.LayerNorm(256),
            nn.Linear(256, hidden_dim),
            nn.ReLU()
        )

        # Post-aggregation decoder (rho)
        self.rho = nn.Sequential(
            nn.Linear(hidden_dim, 256),
            nn.ReLU(),
            nn.Linear(256, K)
        )

        # Reconstruction decoder
        self.reconstruct_mlp = nn.Sequential(
            nn.Linear(K, 256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, weight_dim)
        )

    def forward(self, weights: torch.Tensor, arch_labels: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        Args:
            weights: [B, D] weight vectors
            arch_labels: [B] architecture indices
        Returns:
            z: [B, K] quotient space representation
        """
        # Get architecture embeddings
        arch_embed = self.arch_embedder(arch_labels)  # [B, 64]

        # Concatenate weights with architecture context
        x = torch.cat([weights, arch_embed], dim=-1)  # [B, D+64]

        # Per-element encoding
        x = self.phi(x)  # [B, H]

        # Post-aggregation
        z = self.rho(x)  # [B, K]

        return z

    def reconstruct_weights(self, z: torch.Tensor) -> torch.Tensor:
        """Reconstruct weights from quotient space"""
        return self.reconstruct_mlp(z)
