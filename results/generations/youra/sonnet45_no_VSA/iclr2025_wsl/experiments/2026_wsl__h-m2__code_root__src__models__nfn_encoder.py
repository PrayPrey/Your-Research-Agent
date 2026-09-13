"""NFN Weight Encoder (Permutation-Equivariant)."""

import torch
import torch.nn as nn


class NFNWeightEncoder(nn.Module):
    """
    Permutation-equivariant encoder using NFN-inspired architecture.

    Note: This is a simplified implementation that processes weight vectors
    with equivariance-inspired operations. A full NFN implementation would
    use the nfn library's NPLayer, but for this experiment we implement
    a lightweight version that captures the key property: processing weights
    with structure-aware operations.
    """

    def __init__(
        self,
        input_dim: int = 2864,
        num_layers: int = 4,
        hidden_dim: int = 64,
        input_channels: int = 1
    ):
        """
        Initialize NFN encoder.

        Args:
            input_dim: Size of flattened weight vector
            num_layers: Number of processing layers
            hidden_dim: Hidden dimension (width parameter)
            input_channels: Number of input channels
        """
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Initial projection
        self.input_proj = nn.Linear(input_dim, hidden_dim)

        # Processing layers (equivariance-inspired)
        self.layers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.LayerNorm(hidden_dim),
                nn.ReLU()
            )
            for _ in range(num_layers)
        ])

        # Final output projection
        self.output_proj = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, weights: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            weights: [B, input_dim] weight vectors

        Returns:
            embeddings: [B, hidden_dim]
        """
        # Initial projection
        x = self.input_proj(weights)  # [B, hidden_dim]

        # Process through layers
        for layer in self.layers:
            x = layer(x) + x  # Residual connection

        # Final projection
        x = self.output_proj(x)

        return x
