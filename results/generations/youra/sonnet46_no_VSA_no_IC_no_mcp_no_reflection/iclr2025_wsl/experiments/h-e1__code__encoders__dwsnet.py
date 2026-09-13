"""
DWSNet-inspired encoder (Navon 2023).
Per-layer equivariant processing via row+col linear transforms,
mean pool across layers, MLP scalar head.
"""
import torch
import torch.nn as nn


class EquivariantLayer(nn.Module):
    """Row+col equivariant transform for a single weight matrix."""
    def __init__(self, fan_in: int, fan_out: int, hidden_dim: int):
        super().__init__()
        self.row_proj = nn.Linear(fan_in, hidden_dim)
        self.col_proj = nn.Linear(fan_out, hidden_dim)
        self.norm = nn.LayerNorm(hidden_dim)

    def forward(self, w: torch.Tensor) -> torch.Tensor:
        """w: [B, fan_in, fan_out] -> [B, hidden_dim]"""
        # row: mean over fan_out dim after projecting fan_in
        row_feat = self.row_proj(w.transpose(1, 2)).mean(1)   # [B, hidden_dim]
        # col: mean over fan_in dim after projecting fan_out
        col_feat = self.col_proj(w).mean(1)                    # [B, hidden_dim]
        return self.norm(torch.relu(row_feat + col_feat))      # [B, hidden_dim]


class DWSNet(nn.Module):
    def __init__(self, weight_shapes: list, hidden_dim: int = 256, **kwargs):
        """
        weight_shapes: list of (fan_in, fan_out) per weight layer (2D matrices only).
        For conv layers, we reshape to 2D: (C_in * kH * kW, C_out).
        """
        super().__init__()
        self.weight_shapes = weight_shapes
        self.hidden_dim = hidden_dim
        self.eq_layers = nn.ModuleList([
            EquivariantLayer(fan_in, fan_out, hidden_dim)
            for fan_in, fan_out in weight_shapes
        ])
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, weights_flat: torch.Tensor) -> torch.Tensor:
        """
        weights_flat: [B, D] — extract 2D weight matrices.
        Layout: conv1.weight(fan_in*fan_out), conv1.bias, conv2.weight, conv2.bias, ...
        We skip biases: bias sizes are fan_out of each layer.
        Returns [B].
        """
        B = weights_flat.shape[0]
        layer_feats = []
        offset = 0
        for i, (fan_in, fan_out) in enumerate(self.weight_shapes):
            size = fan_in * fan_out
            w = weights_flat[:, offset:offset + size].reshape(B, fan_in, fan_out)
            feat = self.eq_layers[i](w)   # [B, H]
            layer_feats.append(feat)
            offset += size + fan_out  # skip bias (size = fan_out for weight layers)
        pooled = torch.stack(layer_feats, dim=0).mean(0)  # [B, H]
        return self.head(pooled).squeeze(-1)               # [B]
