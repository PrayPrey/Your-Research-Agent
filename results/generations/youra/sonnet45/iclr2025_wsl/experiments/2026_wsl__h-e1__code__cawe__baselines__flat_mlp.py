"""
Flat-Weight MLP Baseline Model.
Naive baseline that concatenates all weights without architecture awareness.
"""
import torch
import torch.nn as nn


class FlatWeightMLP(nn.Module):
    """
    Flat-Weight MLP Baseline.

    Architecture:
        - Flatten all model weights into a single vector
        - Pass through MLP layers
        - Output generalization gap prediction

    Used for baseline comparison (Δρ = ρ_CAWE - ρ_baseline)
    """

    def __init__(self, input_dim: int):
        super().__init__()
        self.input_dim = input_dim

        self.network = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, weights: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through baseline MLP.

        Args:
            weights: Flattened weight vector (input_dim,)

        Returns:
            prediction: Generalization gap prediction (scalar)
        """
        prediction = self.network(weights)
        return prediction.squeeze()
