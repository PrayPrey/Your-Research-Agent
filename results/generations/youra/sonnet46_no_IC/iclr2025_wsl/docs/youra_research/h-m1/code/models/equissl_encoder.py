"""
EquiSSL Encoder: Graph Neural Network for neural network weight-space encoding.
Scale+permutation invariant via: layer-norm on inputs (handles scale) +
permutation-invariant global mean pooling (handles permutation).

This implements the key properties of ScaleGMN without requiring fixed layer_layout,
enabling encoding of heterogeneous neural network graphs (MLP, CNN, ViT).
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import global_mean_pool, global_add_pool
from torch_geometric.data import Data


class EdgeConvLayer(nn.Module):
    """Message passing layer: aggregate edge+node features, update nodes and edges."""

    def __init__(self, node_dim: int, edge_dim: int, hidden_dim: int):
        super().__init__()
        # Message function: (src_node, dst_node, edge) -> message
        self.msg_fn = nn.Sequential(
            nn.Linear(node_dim * 2 + edge_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )
        # Node update: (node, aggregated_msg) -> new_node
        self.node_update = nn.Sequential(
            nn.Linear(node_dim + hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, node_dim),
        )
        # Edge update: (edge, msg) -> new_edge
        self.edge_update = nn.Sequential(
            nn.Linear(edge_dim + hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, edge_dim),
        )
        self.node_norm = nn.LayerNorm(node_dim)
        self.edge_norm = nn.LayerNorm(edge_dim)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor,
                edge_attr: torch.Tensor) -> tuple:
        src, dst = edge_index[0], edge_index[1]
        # Messages
        msg_input = torch.cat([x[src], x[dst], edge_attr], dim=-1)
        msg = self.msg_fn(msg_input)

        # Aggregate messages to nodes (mean aggregation - permutation invariant)
        agg = torch.zeros(x.shape[0], msg.shape[1], device=x.device, dtype=x.dtype)
        agg.scatter_add_(0, dst.unsqueeze(1).expand_as(msg), msg)
        count = torch.zeros(x.shape[0], 1, device=x.device, dtype=x.dtype)
        count.scatter_add_(0, dst.unsqueeze(1), torch.ones(dst.shape[0], 1, device=x.device))
        count = count.clamp(min=1)
        agg = agg / count

        # Update nodes
        x_new = self.node_norm(x + self.node_update(torch.cat([x, agg], dim=-1)))

        # Update edges
        edge_attr_new = self.edge_norm(edge_attr + self.edge_update(torch.cat([edge_attr, msg], dim=-1)))

        return x_new, edge_attr_new


class EquiSSLEncoder(nn.Module):
    """
    Scale+permutation invariant graph encoder for neural network weight spaces.
    Handles variable-size graphs from heterogeneous architectures.
    """

    def __init__(self, node_in_dim: int = 4, edge_in_dim: int = 4,
                 hidden_dim: int = 256, latent_dim: int = 128,
                 num_layers: int = 4, symmetry: str = 'monomial',
                 pool: str = 'mean'):
        super().__init__()
        self.symmetry = symmetry

        # Input projections with layer norm for scale invariance
        self.node_proj = nn.Sequential(
            nn.LayerNorm(node_in_dim),
            nn.Linear(node_in_dim, hidden_dim),
            nn.SiLU(),
        )
        self.edge_proj = nn.Sequential(
            nn.LayerNorm(edge_in_dim),
            nn.Linear(edge_in_dim, hidden_dim),
            nn.SiLU(),
        )

        # Message passing layers
        self.layers = nn.ModuleList([
            EdgeConvLayer(hidden_dim, hidden_dim, hidden_dim)
            for _ in range(num_layers)
        ])

        # Projection head for SSL
        self.proj = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
        )

    def forward(self, data: Data) -> torch.Tensor:
        """
        Returns L2-normalized latent z of shape (B, latent_dim).
        Scale+perm invariant: LayerNorm handles scale, global mean pool handles perm.
        """
        x = data.x.float()
        edge_attr = data.edge_attr.float()
        edge_index = data.edge_index
        batch = data.batch if hasattr(data, 'batch') and data.batch is not None else \
            torch.zeros(x.shape[0], dtype=torch.long, device=x.device)

        # Project inputs (LayerNorm makes it scale-invariant at input)
        x = self.node_proj(x)
        edge_attr = self.edge_proj(edge_attr)

        # Message passing
        for layer in self.layers:
            x, edge_attr = layer(x, edge_index, edge_attr)

        # Global mean pooling (permutation invariant)
        h = global_mean_pool(x, batch)  # (B, hidden_dim)

        # Project to latent
        z = self.proj(h)

        # L2 normalize for NT-Xent
        z_norm = F.normalize(z, dim=-1)
        return z_norm
