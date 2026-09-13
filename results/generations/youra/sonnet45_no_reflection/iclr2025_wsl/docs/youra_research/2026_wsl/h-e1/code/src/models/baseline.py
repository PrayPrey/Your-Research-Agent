"""Baseline Deep Sets encoder without equivariance constraints"""

import torch
import torch.nn as nn


class PerElementEncoder(nn.Module):
    """Phi function: per-element MLP"""

    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, hidden_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.mlp(x)


class PostAggregationDecoder(nn.Module):
    """Rho function: post-aggregation MLP"""

    def __init__(self, hidden_dim: int, output_dim: int):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(hidden_dim, 256),
            nn.ReLU(),
            nn.Linear(256, output_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.mlp(x)


class DeepSetsEncoder(nn.Module):
    """Standard Deep Sets encoder without equivariance"""

    def __init__(self, weight_dim: int, hidden_dim: int = 128, output_dim: int = 32):
        super().__init__()
        self.weight_dim = weight_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        self.phi = PerElementEncoder(weight_dim, hidden_dim)
        self.rho = PostAggregationDecoder(hidden_dim, output_dim)

        # Reconstruction decoder
        self.reconstruct_mlp = nn.Sequential(
            nn.Linear(output_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, weight_dim)
        )

    def forward(self, weights: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        Args:
            weights: [B, D] weight vectors
        Returns:
            z: [B, K] quotient space representation
        """
        # Treat each weight as a single element (no set structure for PoC)
        x = self.phi(weights)  # [B, H]
        z = self.rho(x)  # [B, K]
        return z

    def reconstruct(self, z: torch.Tensor) -> torch.Tensor:
        """Reconstruct weights from quotient space"""
        return self.reconstruct_mlp(z)
