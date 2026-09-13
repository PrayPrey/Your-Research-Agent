"""
GNN-inspired encoder (Kofinas 2024).
Batched bipartite neuron graph → message passing → global pool → scalar.
Uses torch_geometric with vectorized batch construction.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import MessagePassing, global_mean_pool
from torch_geometric.data import Data, Batch


class EdgeWeightedConv(MessagePassing):
    """Edge-weighted message passing layer."""
    def __init__(self, in_dim: int, edge_dim: int, out_dim: int):
        super().__init__(aggr="mean")
        self.edge_lin = nn.Linear(edge_dim, in_dim)
        self.update_lin = nn.Sequential(
            nn.Linear(in_dim + in_dim, out_dim),
            nn.ReLU(),
        )

    def forward(self, x, edge_index, edge_attr):
        return self.propagate(edge_index, x=x, edge_attr=edge_attr)

    def message(self, x_j, edge_attr):
        return x_j + self.edge_lin(edge_attr)

    def update(self, aggr_out, x):
        return self.update_lin(torch.cat([x, aggr_out], dim=-1))


class GNN(nn.Module):
    def __init__(self, node_dim: int = 16, edge_dim: int = 1, hidden_dim: int = 128,
                 n_layers: int = 3, max_edges: int = 512, **kwargs):
        super().__init__()
        self.node_dim = node_dim
        self.max_edges = max_edges
        self.node_embed = nn.Embedding(2, node_dim)  # 2 node types: src, dst
        dims = [node_dim] + [hidden_dim] * n_layers
        self.conv_layers = nn.ModuleList([
            EdgeWeightedConv(dims[i], edge_dim, dims[i+1])
            for i in range(n_layers)
        ])
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
        )

    def build_batch(self, weights_flat: torch.Tensor):
        """Vectorized batch graph construction. weights_flat: [B, D]"""
        B, D = weights_flat.shape
        device = weights_flat.device
        E = min(D, self.max_edges)

        # Subsample E edges per sample (same indices for all in batch for speed)
        if D > E:
            edge_idx = torch.arange(E, device=device)
        else:
            edge_idx = torch.arange(D, device=device)
            E = D

        # Edge attributes: weight values for selected edges
        edge_vals = weights_flat[:, edge_idx]  # [B, E]

        # Build batched graph: 2 nodes per sample (node 0=src, node 1=dst)
        # Edge: src(0) -> dst(1) for each of E edges per sample
        # Using PyG Batch

        # Node features: type embedding
        # For B samples, 2 nodes each: node types alternating [0,1, 0,1, ...]
        node_types = torch.tensor([0, 1], device=device).repeat(B)  # [2B]
        x = self.node_embed(node_types)  # [2B, node_dim]

        # Edge index: for sample b, src=2b, dst=2b+1, E edges each
        batch_offsets = torch.arange(B, device=device) * 2  # [B]
        src_nodes = batch_offsets.unsqueeze(1).expand(-1, E)  # [B, E]
        dst_nodes = (batch_offsets + 1).unsqueeze(1).expand(-1, E)  # [B, E]
        src_flat = src_nodes.reshape(-1)   # [B*E]
        dst_flat = dst_nodes.reshape(-1)   # [B*E]
        edge_index = torch.stack([src_flat, dst_flat], dim=0)  # [2, B*E]
        edge_attr = edge_vals.reshape(-1, 1)  # [B*E, 1]

        # Batch vector for global pooling
        batch_vec = torch.arange(B, device=device).unsqueeze(1).expand(-1, 2).reshape(-1)  # [2B]

        return x, edge_index, edge_attr, batch_vec

    def forward(self, weights_flat: torch.Tensor) -> torch.Tensor:
        """weights_flat: [B, D] -> [B]"""
        x, edge_index, edge_attr, batch_vec = self.build_batch(weights_flat)

        for conv in self.conv_layers:
            x = conv(x, edge_index, edge_attr)

        out = global_mean_pool(x, batch_vec)  # [B, hidden_dim]
        return self.head(out).squeeze(-1)      # [B]
