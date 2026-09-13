"""
Architecture GNN Residual Module (Task A-4)
3-layer GCN for architecture graph encoding with learnable residual weight
"""

from typing import Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor

try:
    from torch_geometric.nn import GCNConv
    from torch_geometric.nn import global_mean_pool
    TORCH_GEOMETRIC_AVAILABLE = True
except ImportError:
    TORCH_GEOMETRIC_AVAILABLE = False
    print("Warning: torch_geometric not available. ArchitectureGNN will use fallback.")


class ArchitectureGNN(nn.Module):
    """3-layer GCN for architecture graph encoding"""

    def __init__(
        self,
        d_arch: int = 64,
        d_z: int = 256,
        num_layers: int = 3,
        dropout: float = 0.1
    ):
        """
        Args:
            d_arch: Input node feature dimension
            d_z: Output embedding dimension
            num_layers: Number of GCN layers
            dropout: Dropout rate
        """
        super().__init__()
        self.d_arch = d_arch
        self.d_z = d_z
        self.num_layers = num_layers

        if not TORCH_GEOMETRIC_AVAILABLE:
            # Fallback: simple MLP on node features
            self.fallback_mode = True
            self.node_encoder = nn.Sequential(
                nn.Linear(d_arch, 128),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(128, d_z)
            )
        else:
            self.fallback_mode = False

            # GCN layers
            self.convs = nn.ModuleList()
            hidden_dim = 128

            # First layer: d_arch -> hidden_dim
            self.convs.append(GCNConv(d_arch, hidden_dim))

            # Middle layers: hidden_dim -> hidden_dim
            for _ in range(num_layers - 2):
                self.convs.append(GCNConv(hidden_dim, hidden_dim))

            # Last layer: hidden_dim -> hidden_dim
            self.convs.append(GCNConv(hidden_dim, hidden_dim))

            self.dropout = nn.Dropout(dropout)

            # Project to output dimension
            self.output_proj = nn.Linear(hidden_dim, d_z)

    def forward(
        self,
        node_features: Tensor,
        edge_index: Tensor,
        batch: Optional[Tensor] = None
    ) -> Tensor:
        """
        Process architecture DAG.

        Args:
            node_features: [N_nodes, d_arch] node features
            edge_index: [2, N_edges] edge connectivity
            batch: [N_nodes] batch assignment (None for single graph)
        Returns:
            z_arch: [B, d_z] or [d_z] architecture embedding
        """
        if self.fallback_mode:
            # Fallback: just encode node features and pool
            node_embeds = self.node_encoder(node_features)  # [N_nodes, d_z]
            # Global mean pooling
            if batch is not None:
                # Batched pooling
                z_arch = torch.zeros(
                    batch.max().item() + 1, self.d_z,
                    device=node_features.device
                )
                for i in range(batch.max().item() + 1):
                    mask = (batch == i)
                    z_arch[i] = node_embeds[mask].mean(dim=0)
            else:
                z_arch = node_embeds.mean(dim=0)  # [d_z]
            return z_arch

        # GCN forward pass
        x = node_features
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index)
            if i < len(self.convs) - 1:
                x = F.relu(x)
                x = self.dropout(x)

        # Global pooling
        if batch is not None:
            # Use torch_geometric global pooling
            x = global_mean_pool(x, batch)  # [B, hidden_dim]
        else:
            # Single graph: mean over all nodes
            x = x.mean(dim=0, keepdim=True)  # [1, hidden_dim]

        # Project to output dimension
        z_arch = self.output_proj(x)  # [B, d_z] or [1, d_z]

        # Remove batch dimension if single graph
        if batch is None:
            z_arch = z_arch.squeeze(0)  # [d_z]

        return z_arch
