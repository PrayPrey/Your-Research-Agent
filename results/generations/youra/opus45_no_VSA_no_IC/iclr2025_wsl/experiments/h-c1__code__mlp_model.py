"""MLP baseline model for H-M2 comparison."""
import torch
import torch.nn as nn
from typing import List, Tuple


class MLPBaseline(nn.Module):
    """2-layer MLP baseline (non-equivariant)."""
    def __init__(self, input_dim: int, hidden_dim: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: [B, D] -> [B] (squeezed)."""
        return self.net(x).squeeze(-1)


def flatten_state_dict(state_dict: dict) -> torch.Tensor:
    """Concat all param tensors into 1D vector."""
    params = []
    for name, param in sorted(state_dict.items()):
        params.append(param.flatten())
    return torch.cat(params)


def infer_input_dim(sample_state_dict: dict) -> int:
    """Get total param count from one sample."""
    return len(flatten_state_dict(sample_state_dict))


def collate_flat(items: List[Tuple[dict, float]]) -> Tuple[torch.Tensor, torch.Tensor]:
    """Collate batch into (X [B,D], y [B])."""
    X = torch.stack([flatten_state_dict(sd) for sd, _ in items])
    y = torch.tensor([acc for _, acc in items], dtype=torch.float32)
    return X, y
