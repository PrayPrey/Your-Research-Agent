import torch
import torch.nn as nn


class FlatMLP(nn.Module):
    """Unterthiner 2020 baseline: flatten weights → MLP → scalar."""
    def __init__(self, input_dim: int, hidden_dim: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, weights_flat: torch.Tensor) -> torch.Tensor:
        """weights_flat: [B, D] -> [B]"""
        return self.net(weights_flat).squeeze(-1)
