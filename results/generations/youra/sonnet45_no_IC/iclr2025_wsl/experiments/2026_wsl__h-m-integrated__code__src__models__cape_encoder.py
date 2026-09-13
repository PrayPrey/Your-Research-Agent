"""
Full CAPE Encoder (Task A-6)
Integrates operation encoders, contrastive projector, and architecture GNN
"""

from typing import Dict, List, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor

from .operation_encoders import SANEConvEncoder, UNFAttentionEncoder, MLPEncoder
from .contrastive_projector import ContrastiveProjector
from .architecture_gnn import ArchitectureGNN


class CAPEEncoder(nn.Module):
    """Full CAPE encoder with 3 components"""

    def __init__(
        self,
        d_z: int = 256,
        d_arch: int = 64,
        d_token: int = 64,
        tau: float = 0.07,
        dropout: float = 0.1,
        gnn_layers: int = 3,
        enable_operation_encoders: bool = True,
        enable_contrastive: bool = True,
        enable_gnn: bool = True,
    ):
        """
        Args:
            d_z: Embedding dimension
            d_arch: Architecture node feature dimension
            d_token: Token dimension for spatial tokenization
            tau: InfoNCE temperature
            dropout: Dropout rate
            gnn_layers: Number of GNN layers
            enable_operation_encoders: Use operation-specific encoders
            enable_contrastive: Use contrastive projection
            enable_gnn: Use architecture GNN residual
        """
        super().__init__()
        self.d_z = d_z
        self.d_arch = d_arch
        self.tau = tau
        self.enable_operation_encoders = enable_operation_encoders
        self.enable_contrastive = enable_contrastive
        self.enable_gnn = enable_gnn

        # Component 1: Operation-specific encoders (FR-3)
        if enable_operation_encoders:
            self.conv_encoder = SANEConvEncoder(d_out=d_z, d_token=d_token, dropout=dropout)
            self.attn_encoder = UNFAttentionEncoder(d_out=d_z, d_hidden=128, dropout=dropout)
            self.mlp_encoder = MLPEncoder(d_out=d_z, d_hidden=128, dropout=dropout)
        else:
            # Fallback: simple set encoder for all weights
            self.simple_encoder = nn.Sequential(
                nn.Linear(3, 128),  # 3 statistics: norm, mean, std
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(128, d_z)
            )

        # Component 2: Contrastive projection (FR-4)
        if enable_contrastive:
            self.projector = ContrastiveProjector(d_z=d_z, dropout=dropout)

        # Component 3: Architecture GNN (FR-5)
        if enable_gnn:
            self.gnn = ArchitectureGNN(
                d_arch=d_arch,
                d_z=d_z,
                num_layers=gnn_layers,
                dropout=dropout
            )
            # Learnable residual weight alpha
            self.alpha = nn.Parameter(torch.tensor(0.5))

    def get_operation_embeddings(
        self,
        model_weights: Dict[str, List[Tensor]]
    ) -> Tensor:
        """
        Get operation-specific embeddings.

        Args:
            model_weights: {"conv": [tensors], "attention": [tensors], "mlp": [tensors]}
        Returns:
            z_op: [d_z] aggregated operation embedding
        """
        if self.enable_operation_encoders:
            # Encode each operation type
            z_conv = self.conv_encoder(model_weights.get("conv", []))  # [d_z]
            z_attn = self.attn_encoder(model_weights.get("attention", []))  # [d_z]
            z_mlp = self.mlp_encoder(model_weights.get("mlp", []))  # [d_z]

            # Mean pooling across operation types
            z_op = torch.stack([z_conv, z_attn, z_mlp], dim=0).mean(dim=0)  # [d_z]
        else:
            # Fallback: aggregate all weights into simple statistics
            all_weights = []
            for op_type in ["conv", "attention", "mlp"]:
                all_weights.extend(model_weights.get(op_type, []))

            if len(all_weights) == 0:
                device = next(self.parameters()).device
                return torch.zeros(self.d_z, device=device)

            # Compute global statistics
            all_flat = torch.cat([w.reshape(-1) for w in all_weights])
            stats = torch.tensor([
                torch.norm(all_flat).item(),
                all_flat.mean().item(),
                all_flat.std().item()
            ], device=all_flat.device)

            z_op = self.simple_encoder(stats)  # [d_z]

        return z_op

    def get_contrastive_embeddings(self, z_op: Tensor) -> Tensor:
        """
        Apply contrastive projection.

        Args:
            z_op: [B, d_z] or [d_z] operation embeddings
        Returns:
            z_proj: [B, d_z] or [d_z] projected and L2-normalized embeddings
        """
        if self.enable_contrastive:
            # Handle both batched and single inputs
            is_batched = (z_op.dim() == 2)
            if not is_batched:
                z_op = z_op.unsqueeze(0)  # [1, d_z]

            z_proj = self.projector(z_op)  # [B, d_z] or [1, d_z]

            if not is_batched:
                z_proj = z_proj.squeeze(0)  # [d_z]
        else:
            # No projection: just normalize
            z_proj = F.normalize(z_op, p=2, dim=-1)

        return z_proj

    def forward(
        self,
        model_weights: Dict[str, List[Tensor]],
        arch_graph: Optional[Tuple[Tensor, Tensor]] = None
    ) -> Tensor:
        """
        Forward pass through full CAPE encoder.

        Args:
            model_weights: {"conv": [tensors], "attention": [tensors], "mlp": [tensors]}
            arch_graph: (node_features: [N_nodes, d_arch], edge_index: [2, N_edges]) or None
        Returns:
            z_final: [d_z] final embedding
        """
        # Step 1: Operation-specific encoding
        z_op = self.get_operation_embeddings(model_weights)  # [d_z]

        # Step 2: Contrastive projection
        z_proj = self.get_contrastive_embeddings(z_op)  # [d_z]

        # Step 3: Architecture GNN residual
        if self.enable_gnn and arch_graph is not None:
            node_features, edge_index = arch_graph
            z_arch = self.gnn(node_features, edge_index)  # [d_z]

            # Residual combination with learnable alpha
            z_final = z_proj + self.alpha * z_arch
        else:
            z_final = z_proj

        return z_final

    def compute_infonce_loss(self, z_proj: Tensor) -> Tensor:
        """
        Compute InfoNCE contrastive loss.

        Args:
            z_proj: [B, d_z] normalized embeddings (batched)
        Returns:
            loss: Scalar InfoNCE loss
        """
        if not self.enable_contrastive:
            # Return zero loss if contrastive learning disabled
            return torch.tensor(0.0, device=z_proj.device)

        return self.projector.infonce_loss(z_proj, temperature=self.tau)

    def get_diagnostic_metrics(
        self,
        model_weights: Dict[str, List[Tensor]]
    ) -> Dict[str, float]:
        """
        Compute diagnostic metrics for component validation.

        Returns:
            diagnostics: {"conv_attn_similarity": float, "alpha": float}
        """
        diagnostics = {}

        if self.enable_operation_encoders:
            # Diagnostic 1: Operation similarity
            with torch.no_grad():
                z_conv = self.conv_encoder(model_weights.get("conv", []))
                z_attn = self.attn_encoder(model_weights.get("attention", []))

                # Cosine similarity
                similarity = F.cosine_similarity(z_conv.unsqueeze(0), z_attn.unsqueeze(0))
                diagnostics["conv_attn_similarity"] = similarity.item()

        if self.enable_gnn:
            # Diagnostic 3: GNN residual weight alpha
            diagnostics["alpha"] = self.alpha.item()

        return diagnostics
