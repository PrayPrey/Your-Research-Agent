"""NFN-style permutation-equivariant accuracy predictor.

Implements equivariant feature extraction for neural network weights.
Uses DeepSets-style architecture: per-neuron MLP + permutation-invariant pooling.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple


class PerNeuronMLP(nn.Module):
    """Process each neuron's incoming/outgoing weights independently (shared weights)."""
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
    """Process weight matrix with row/column equivariance.

    For weight matrix W[out, in]:
    - Row features (per output neuron): aggregate over input dim
    - Col features (per input neuron): aggregate over output dim
    - Combine with learned transformations
    """
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.row_net = PerNeuronMLP(7, hidden_dim, hidden_dim)  # 7 stats per row
        self.col_net = PerNeuronMLP(7, hidden_dim, hidden_dim)  # 7 stats per col
        self.combine = nn.Linear(hidden_dim * 2, hidden_dim)

    def compute_stats(self, x: torch.Tensor) -> torch.Tensor:
        """Compute 7 statistics along last dim: mean, std, min, max, sum, abs_mean, abs_max."""
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
        B = weight.shape[0]
        row_stats = self.compute_stats(weight)  # [B, out_dim, 7]
        col_stats = self.compute_stats(weight.transpose(-2, -1))  # [B, in_dim, 7]

        row_feats = self.row_net(row_stats)  # [B, out_dim, hidden]
        col_feats = self.col_net(col_stats)  # [B, in_dim, hidden]

        # Invariant pooling (mean over neurons - permutation invariant)
        row_pooled = row_feats.mean(dim=1)  # [B, hidden]
        col_pooled = col_feats.mean(dim=1)  # [B, hidden]

        combined = torch.cat([row_pooled, col_pooled], dim=-1)  # [B, hidden*2]
        return self.combine(combined)  # [B, hidden]


class NFNAccuracyPredictor(nn.Module):
    """NFN-style accuracy predictor using equivariant feature extraction.

    Architecture:
    - Per-layer equivariant processing of weight matrices
    - Global pooling to invariant representation
    - Linear head for accuracy prediction
    """
    def __init__(self, hidden_dim: int = 128, num_layers: int = 3):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Per-weight-matrix processing (applied to each layer's weights)
        self.layer_processor = EquivariantLayer(hidden_dim)

        # Cross-layer processing
        self.cross_layer_net = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # Final head
        self.head = nn.Linear(hidden_dim, 1)

    def forward(self, weight_tensors: List[torch.Tensor]) -> torch.Tensor:
        """
        Args:
            weight_tensors: List of weight matrices, each [B, out, in] or [B, out, in, h, w]
        Returns:
            [B] predicted accuracy
        """
        layer_features = []
        for w in weight_tensors:
            if w.dim() > 3:
                # Flatten spatial dims for conv weights [B, out, in, h, w] -> [B, out, in*h*w]
                B, out_ch, in_ch = w.shape[:3]
                w = w.reshape(B, out_ch, -1)
            feat = self.layer_processor(w)  # [B, hidden]
            layer_features.append(feat)

        # Mean pooling over layers (order-invariant)
        stacked = torch.stack(layer_features, dim=1)  # [B, n_layers, hidden]
        pooled = stacked.mean(dim=1)  # [B, hidden]

        # Cross-layer processing
        out = self.cross_layer_net(pooled)  # [B, hidden]

        return self.head(out).squeeze(-1)  # [B]

    def get_invariant_repr(self, weight_tensors: List[torch.Tensor]) -> torch.Tensor:
        """Get intermediate invariant representation (for equivariance test)."""
        layer_features = []
        for w in weight_tensors:
            if w.dim() > 3:
                B, out_ch, in_ch = w.shape[:3]
                w = w.reshape(B, out_ch, -1)
            feat = self.layer_processor(w)
            layer_features.append(feat)

        stacked = torch.stack(layer_features, dim=1)
        return stacked.mean(dim=1)


def extract_weight_tensors(state_dict: dict) -> List[torch.Tensor]:
    """Extract weight tensors from state_dict as list, adding batch dim."""
    weights = []
    for name, param in state_dict.items():
        if 'weight' in name.lower() and param.dim() >= 2:
            weights.append(param.unsqueeze(0))  # Add batch dim
    return weights


def collate_weights(items: List[Tuple[dict, float]]) -> Tuple[List[torch.Tensor], torch.Tensor]:
    """Collate batch of (state_dict, accuracy) into batched tensors."""
    # Extract weight tensors from each model
    all_weights = [extract_weight_tensors(sd) for sd, _ in items]
    accs = torch.tensor([acc for _, acc in items], dtype=torch.float32)

    # Stack each layer's weights across batch
    n_layers = len(all_weights[0])
    batched = []
    for layer_idx in range(n_layers):
        layer_weights = torch.cat([w[layer_idx] for w in all_weights], dim=0)
        batched.append(layer_weights)

    return batched, accs
