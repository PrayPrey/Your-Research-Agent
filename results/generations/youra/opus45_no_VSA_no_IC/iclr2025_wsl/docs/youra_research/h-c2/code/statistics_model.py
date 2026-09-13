"""Statistics baseline model for H-C2: per-layer weight statistics + linear regression."""
import torch
import torch.nn as nn
from typing import List, Tuple, Dict
from sklearn.preprocessing import StandardScaler
import numpy as np


def extract_statistics(state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Extract per-layer statistics from model weights.

    Per layer with 2D+ weights: mean, std, L2 norm, spectral norm
    Plus: total params, layer count

    Returns: Tensor of shape [F] where F ~ 20-50 depending on architecture.
    """
    features = []
    layer_count = 0

    for name, param in state_dict.items():
        if 'weight' in name.lower() and param.dim() >= 2:
            layer_count += 1
            w2d = param.reshape(param.size(0), -1).float()
            features.extend([
                param.float().mean().item(),
                param.float().std().item(),
                param.float().norm(2).item(),
                torch.linalg.svdvals(w2d)[0].item(),
            ])

    features.append(float(sum(p.numel() for p in state_dict.values())))
    features.append(float(layer_count))

    return torch.tensor(features, dtype=torch.float32)


def collate_statistics(items: List[Tuple[Dict, float]]) -> Tuple[torch.Tensor, torch.Tensor]:
    """Collate model checkpoints into statistics features + accuracies.

    Returns: (X: [B, F], y: [B])
    """
    feats = torch.stack([extract_statistics(sd) for sd, _ in items])
    accs = torch.tensor([acc for _, acc in items], dtype=torch.float32)
    return feats, accs


class StatisticsPredictor(nn.Module):
    """Linear regression on weight statistics."""

    def __init__(self, in_dim: int):
        super().__init__()
        self.linear = nn.Linear(in_dim, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: [B, F] -> [B]"""
        return self.linear(x).squeeze(-1)


class ScaledStatisticsPredictor(nn.Module):
    """Statistics predictor with built-in feature scaling."""

    def __init__(self, in_dim: int):
        super().__init__()
        self.linear = nn.Linear(in_dim, 1)
        self.register_buffer('mean', torch.zeros(in_dim))
        self.register_buffer('std', torch.ones(in_dim))
        self._fitted = False

    def fit_scaler(self, X_train: torch.Tensor):
        """Fit scaler on training data."""
        self.mean = X_train.mean(dim=0)
        self.std = X_train.std(dim=0).clamp(min=1e-8)
        self._fitted = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: [B, F] -> [B]"""
        if self._fitted:
            x = (x - self.mean) / self.std
        return self.linear(x).squeeze(-1)


def infer_stats_dim(sample_state_dict: Dict) -> int:
    """Infer feature dimension from sample state dict."""
    return extract_statistics(sample_state_dict).shape[0]
