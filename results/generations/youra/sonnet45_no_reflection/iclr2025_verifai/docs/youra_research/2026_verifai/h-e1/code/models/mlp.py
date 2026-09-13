"""Multi-layer perceptron helper module."""
import torch.nn as nn
from torch import Tensor


class MLP(nn.Module):
    """Multi-layer perceptron for message functions."""

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, num_layers: int = 3):
        super().__init__()
        layers = []

        # Input layer
        layers.append(nn.Linear(input_dim, hidden_dim))
        layers.append(nn.ReLU())

        # Hidden layers
        for _ in range(num_layers - 2):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.ReLU())

        # Output layer
        layers.append(nn.Linear(hidden_dim, output_dim))

        self.net = nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        """x: [*, D_in] -> [*, D_out]"""
        return self.net(x)
