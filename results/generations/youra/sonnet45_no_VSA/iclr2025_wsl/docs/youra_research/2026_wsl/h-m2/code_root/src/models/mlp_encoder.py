"""MLP Weight Encoder (Non-Equivariant Baseline)."""

import torch
import torch.nn as nn
from typing import List


class MLPWeightEncoder(nn.Module):
    """
    Non-equivariant baseline encoder.

    Processes flattened weight vectors through standard MLP.
    """

    def __init__(
        self,
        input_dim: int = 2864,
        hidden_dims: List[int] = [512, 256],
        output_dim: int = 64
    ):
        """
        Initialize MLP encoder.

        Args:
            input_dim: Size of flattened weight vector
            hidden_dims: List of hidden layer dimensions
            output_dim: Final embedding dimension (width parameter)
        """
        super().__init__()

        layers = []
        prev_dim = input_dim

        # Build hidden layers
        for h_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, h_dim))
            layers.append(nn.ReLU())
            prev_dim = h_dim

        # Output layer
        layers.append(nn.Linear(prev_dim, output_dim))

        self.net = nn.Sequential(*layers)

    def forward(self, weights: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            weights: [B, input_dim] flattened weight vectors

        Returns:
            embeddings: [B, output_dim]
        """
        return self.net(weights)
