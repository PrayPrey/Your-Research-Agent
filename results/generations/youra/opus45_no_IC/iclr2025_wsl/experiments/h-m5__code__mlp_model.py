"""MLPMatched model for H-M3 variance test."""

import torch
import torch.nn as nn


class MLPMatched(nn.Module):
    """Simple MLP with input_dim -> 256 -> 128 -> 1 architecture."""

    def __init__(self, input_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
