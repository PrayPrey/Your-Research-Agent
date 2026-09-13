"""Encoder models: FlatMLP, FlatMLPPermAug, NFNEncoder, GNNNFNEncoder."""
import torch
import torch.nn as nn
from torch import Tensor
from typing import Literal
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Flat-MLP (Condition 1)
# ─────────────────────────────────────────────────────────────────────────────

class FlatMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, num_layers: int = 3):
        super().__init__()
        layers = [nn.Linear(input_dim, hidden_dim), nn.ReLU()]
        for _ in range(num_layers - 1):
            layers += [nn.Linear(hidden_dim, hidden_dim), nn.ReLU()]
        layers.append(nn.Linear(hidden_dim, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:  # (B, D) → (B,)
        return self.net(x).squeeze(-1)

    def count_params(self) -> int:
        return sum(p.numel() for p in self.parameters())


# ─────────────────────────────────────────────────────────────────────────────
# Flat-MLP + PermAug (Condition 2)
# ─────────────────────────────────────────────────────────────────────────────

def _permute_flat_weights(flat_x: Tensor, weight_shapes: list, perm_prob: float = 0.5) -> Tensor:
    """Apply random neuron permutation to a batch of flattened weight vectors."""
    # ponytail: skip per-sample permutation — use batch-level permutation for speed
    B = flat_x.shape[0]
    if np.random.random() > perm_prob:
        return flat_x
    # Simple: shuffle segments of the flat vector corresponding to each layer
    x = flat_x.clone()
    offset = 0
    for shape in weight_shapes:
        size = int(np.prod(shape))
        perm = torch.randperm(size, device=flat_x.device)
        x[:, offset:offset + size] = x[:, offset:offset + size][:, perm]
        offset += size
    return x


class FlatMLPPermAug(FlatMLP):
    def __init__(self, input_dim: int, hidden_dim: int = 256, num_layers: int = 3,
                 perm_prob: float = 0.5, weight_shapes: list = None):
        super().__init__(input_dim, hidden_dim, num_layers)
        self.perm_prob = perm_prob
        self.weight_shapes = weight_shapes or []

    def forward(self, x: Tensor, training: bool = False) -> Tensor:
        if training and self.weight_shapes:
            x = _permute_flat_weights(x, self.weight_shapes, self.perm_prob)
        return self.net(x).squeeze(-1)


# ─────────────────────────────────────────────────────────────────────────────
# NFN Encoder (Condition 3 — CNN zoo equivariant, AllanYangZhou/nfn)
# ─────────────────────────────────────────────────────────────────────────────

class NFNEncoder(nn.Module):
    """
    Permutation-equivariant encoder using AllanYangZhou/nfn library.
    Works with CNN zoo models via WeightSpaceFeatures abstraction.
    """

    def __init__(self, hidden_dim: int = 64):
        super().__init__()
        self.hidden_dim = hidden_dim
        self._built = False
        self._net = None

    def _build(self, wsfeat) -> None:
        from nfn.common import network_spec_from_wsfeat
        from nfn import layers

        network_spec = network_spec_from_wsfeat(wsfeat)
        num_outs = layers.HNPPool.get_num_outs(network_spec)
        h = self.hidden_dim

        self._net = nn.Sequential(
            layers.NPLinear(network_spec, 1, h, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.NPLinear(network_spec, h, h, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.HNPPool(network_spec),
            nn.Flatten(start_dim=-2),
            nn.Linear(h * num_outs, 1)
        ).to(next(iter([p for g in [wsfeat] for p in []]), torch.device('cpu')))

        # Move to same device as wsfeat (infer from first tensor)
        device = self._infer_device(wsfeat)
        self._net = self._net.to(device)
        self._built = True

    def _infer_device(self, wsfeat):
        # WeightSpaceFeatures has .weights and .biases attributes
        if hasattr(wsfeat, 'weights') and len(wsfeat.weights) > 0:
            return wsfeat.weights[0].device
        if hasattr(wsfeat, 'biases') and len(wsfeat.biases) > 0:
            return wsfeat.biases[0].device
        # Fallback: iterate fields if namedtuple
        if hasattr(wsfeat, '_fields'):
            for field in wsfeat._fields:
                val = getattr(wsfeat, field)
                if isinstance(val, (list, tuple)) and len(val) > 0:
                    if isinstance(val[0], Tensor):
                        return val[0].device
        return torch.device('cpu')

    def forward(self, wsfeat) -> Tensor:  # → (B,)
        if not self._built:
            self._build(wsfeat)
        return self._net(wsfeat).squeeze(-1)

    def count_params(self) -> int:
        if not self._built:
            return 0
        return sum(p.numel() for p in self._net.parameters())


# ─────────────────────────────────────────────────────────────────────────────
# GNN-NFN Encoder (Condition 4 — Graph Neural Network on neural graph)
# ─────────────────────────────────────────────────────────────────────────────

class GNNNFNEncoder(nn.Module):
    """
    GNN-based equivariant encoder. Represents zoo model as computational graph.
    Uses PyTorch Geometric for graph batching.
    """

    def __init__(self, hidden_dim: int = 64, num_layers: int = 4):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        node_in_dim = 1
        edge_in_dim = 1

        # Node embedding
        self.node_embed = nn.Linear(node_in_dim, hidden_dim)
        self.edge_embed = nn.Linear(edge_in_dim, hidden_dim)

        # Message-passing layers
        self.gnn_layers = nn.ModuleList([
            _GNNLayer(hidden_dim) for _ in range(num_layers)
        ])

        # Global mean pool → regressor
        self.regressor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, batch) -> Tensor:
        from torch_geometric.utils import scatter
        x = batch.x.float()          # (N_total, 1)
        edge_index = batch.edge_index  # (2, E)
        edge_attr = batch.edge_attr.float()  # (E, 1)
        batch_idx = batch.batch       # (N_total,)

        h = self.node_embed(x)        # (N_total, hidden_dim)
        e = self.edge_embed(edge_attr)  # (E, hidden_dim)

        for layer in self.gnn_layers:
            h, e = layer(h, edge_index, e)

        # Global mean pooling
        num_graphs = batch_idx.max().item() + 1
        g = scatter(h, batch_idx, dim=0, dim_size=num_graphs, reduce='mean')  # (B, hidden_dim)
        return self.regressor(g).squeeze(-1)  # (B,)

    def count_params(self) -> int:
        return sum(p.numel() for p in self.parameters())


class _GNNLayer(nn.Module):
    """Simple message-passing layer with edge features."""

    def __init__(self, hidden_dim: int):
        super().__init__()
        self.msg_mlp = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.update_mlp = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.edge_update = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

    def forward(self, h, edge_index, e):
        from torch_geometric.utils import scatter
        src, dst = edge_index[0], edge_index[1]
        # Message: concat(h_src, h_dst, e) → message
        msg_in = torch.cat([h[src], h[dst], e], dim=-1)
        msg = self.msg_mlp(msg_in)  # (E, hidden_dim)

        # Aggregate messages to destination nodes
        n = h.shape[0]
        agg = scatter(msg, dst, dim=0, dim_size=n, reduce='sum')  # (N, hidden_dim)

        # Update node features
        h_new = self.update_mlp(torch.cat([h, agg], dim=-1))

        # Update edge features
        e_new = self.edge_update(torch.cat([h_new[src], h_new[dst], e], dim=-1))

        return h_new, e_new


# ─────────────────────────────────────────────────────────────────────────────
# Factory: build encoder at target parameter budget
# ─────────────────────────────────────────────────────────────────────────────

def build_encoder(name: str, input_dim: int, target_params: int,
                  zoo_arch: str = "cnn", sample_wsfeat=None) -> nn.Module:
    """Grid-search hidden_dim to hit target_params within ±30%."""
    lo, hi = target_params * 0.7, target_params * 1.3

    if name == "flat_mlp":
        for h in [32, 64, 96, 128, 192, 256, 384, 512, 768, 1024]:
            m = FlatMLP(input_dim, hidden_dim=h)
            p = m.count_params()
            if lo <= p <= hi:
                return m
        # Return closest
        best, best_m = float('inf'), None
        for h in [32, 64, 96, 128, 192, 256, 384, 512, 768, 1024]:
            m = FlatMLP(input_dim, hidden_dim=h)
            if abs(m.count_params() - target_params) < best:
                best = abs(m.count_params() - target_params)
                best_m = m
        return best_m

    elif name == "flat_mlp_perm_aug":
        for h in [32, 64, 96, 128, 192, 256, 384, 512, 768, 1024]:
            m = FlatMLPPermAug(input_dim, hidden_dim=h)
            p = m.count_params()
            if lo <= p <= hi:
                return m
        best, best_m = float('inf'), None
        for h in [32, 64, 96, 128, 192, 256, 384, 512, 768, 1024]:
            m = FlatMLPPermAug(input_dim, hidden_dim=h)
            if abs(m.count_params() - target_params) < best:
                best = abs(m.count_params() - target_params)
                best_m = m
        return best_m

    elif name == "nfn":
        # NFN: hidden_dim grid search; param count known after first forward
        for h in [16, 32, 48, 64, 96, 128]:
            m = NFNEncoder(hidden_dim=h)
            if sample_wsfeat is not None:
                with torch.no_grad():
                    _ = m(sample_wsfeat)
                p = m.count_params()
                if lo <= p <= hi:
                    return m
        # Return medium hidden_dim if no wsfeat provided
        return NFNEncoder(hidden_dim=64)

    elif name == "gnn_nfn":
        for h in [32, 48, 64, 80, 96, 128, 192, 256]:
            m = GNNNFNEncoder(hidden_dim=h, num_layers=4)
            p = m.count_params()
            if lo <= p <= hi:
                return m
        best, best_m = float('inf'), None
        for h in [32, 48, 64, 80, 96, 128, 192, 256]:
            m = GNNNFNEncoder(hidden_dim=h, num_layers=4)
            if abs(m.count_params() - target_params) < best:
                best = abs(m.count_params() - target_params)
                best_m = m
        return best_m

    raise ValueError(f"Unknown encoder: {name}")
