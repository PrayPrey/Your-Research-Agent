"""H-M5: MLPMatchedWide with [512, 256] hidden dims per PRD FR-2.2."""

import torch
import torch.nn as nn


class MLPMatchedWide(nn.Module):
    """Wider MLP: input_dim -> 512 -> 256 -> 1 for N=50K scale."""

    def __init__(self, input_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
