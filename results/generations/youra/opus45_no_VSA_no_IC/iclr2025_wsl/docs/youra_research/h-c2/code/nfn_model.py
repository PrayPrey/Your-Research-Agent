"""NFN-style permutation-equivariant accuracy predictor.

Uses DeepSets-style architecture: per-neuron MLP + permutation-invariant pooling.
"""
import torch
import torch.nn as nn
from typing import List, Tuple


class PerNeuronMLP(nn.Module):
    """Process each neuron's incoming/outgoing weights independently."""
    def __init__(self, in_dim: int, hidden_dim: int, out_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, out_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class EquivariantLayer(nn.Module):
    """Process weight matrix with row/column equivariance."""
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.row_net = PerNeuronMLP(7, hidden_dim, hidden_dim)
        self.col_net = PerNeuronMLP(7, hidden_dim, hidden_dim)
        self.combine = nn.Linear(hidden_dim * 2, hidden_dim)

    def compute_stats(self, x: torch.Tensor) -> torch.Tensor:
        """Compute 7 statistics along last dim."""
        mean = x.mean(dim=-1, keepdim=True)
        std = x.std(dim=-1, keepdim=True) + 1e-8
        min_v = x.min(dim=-1, keepdim=True).values
        max_v = x.max(dim=-1, keepdim=True).values
        sum_v = x.sum(dim=-1, keepdim=True)
        abs_mean = x.abs().mean(dim=-1, keepdim=True)
        abs_max = x.abs().max(dim=-1, keepdim=True).values
        return torch.cat([mean, std, min_v, max_v, sum_v, abs_mean, abs_max], dim=-1)

    def forward(self, weight: torch.Tensor) -> torch.Tensor:
        """Process weight tensor [B, out_dim, in_dim] -> [B, hidden_dim]."""
        row_stats = self.compute_stats(weight)
        col_stats = self.compute_stats(weight.transpose(-2, -1))

        row_feats = self.row_net(row_stats)
        col_feats = self.col_net(col_stats)

        row_pooled = row_feats.mean(dim=1)
        col_pooled = col_feats.mean(dim=1)

        combined = torch.cat([row_pooled, col_pooled], dim=-1)
        return self.combine(combined)


class NFNAccuracyPredictor(nn.Module):
    """NFN-style accuracy predictor using equivariant feature extraction."""
    def __init__(self, hidden_dim: int = 128, num_layers: int = 3):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.layer_processor = EquivariantLayer(hidden_dim)

        self.cross_layer_net = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

        self.head = nn.Linear(hidden_dim, 1)

    def forward(self, weight_tensors: List[torch.Tensor]) -> torch.Tensor:
        """Process weight tensors -> [B] predicted accuracy."""
        layer_features = []
        for w in weight_tensors:
            if w.dim() > 3:
                B, out_ch, in_ch = w.shape[:3]
                w = w.reshape(B, out_ch, -1)
            feat = self.layer_processor(w)
            layer_features.append(feat)

        stacked = torch.stack(layer_features, dim=1)
        pooled = stacked.mean(dim=1)
        out = self.cross_layer_net(pooled)

        return self.head(out).squeeze(-1)


def extract_weight_tensors(state_dict: dict) -> List[torch.Tensor]:
    """Extract weight tensors from state_dict as list, adding batch dim."""
    weights = []
    for name, param in state_dict.items():
        if 'weight' in name.lower() and param.dim() >= 2:
            weights.append(param.unsqueeze(0))
    return weights


def collate_weights(items: List[Tuple[dict, float]]) -> Tuple[List[torch.Tensor], torch.Tensor]:
    """Collate batch of (state_dict, accuracy) into batched tensors."""
    all_weights = [extract_weight_tensors(sd) for sd, _ in items]
    accs = torch.tensor([acc for _, acc in items], dtype=torch.float32)

    n_layers = len(all_weights[0])
    batched = []
    for layer_idx in range(n_layers):
        layer_weights = torch.cat([w[layer_idx] for w in all_weights], dim=0)
        batched.append(layer_weights)

    return batched, accs
