"""
Contrastive Projection Module (Task A-3)
2-layer MLP projector with InfoNCE loss computation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


class ContrastiveProjector(nn.Module):
    """2-layer MLP projector for contrastive learning"""

    def __init__(self, d_z: int = 256, dropout: float = 0.1):
        """
        Args:
            d_z: Embedding dimension (input and output)
            dropout: Dropout rate
        """
        super().__init__()
        self.d_z = d_z

        # 2-layer MLP: d_z -> d_z -> d_z
        self.projector = nn.Sequential(
            nn.Linear(d_z, d_z),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_z, d_z)
        )

    def forward(self, z_op: Tensor) -> Tensor:
        """
        Project embeddings and L2 normalize.

        Args:
            z_op: [B, d_z] operation embeddings
        Returns:
            z_proj: [B, d_z] projected and L2-normalized embeddings
        """
        # Project
        z_proj = self.projector(z_op)  # [B, d_z]

        # L2 normalize (unit vectors)
        z_proj = F.normalize(z_proj, p=2, dim=-1)  # [B, d_z]

        return z_proj

    def infonce_loss(self, z_proj: Tensor, temperature: float = 0.07) -> Tensor:
        """
        Compute InfoNCE contrastive loss.

        Args:
            z_proj: [B, d_z] L2-normalized embeddings
            temperature: Temperature parameter (tau)
        Returns:
            loss: Scalar InfoNCE loss
        """
        B = z_proj.shape[0]

        # Compute similarity matrix: [B, B]
        similarity = torch.matmul(z_proj, z_proj.T) / temperature

        # Create labels: diagonal entries are positive pairs
        labels = torch.arange(B, device=z_proj.device)

        # InfoNCE loss (symmetric cross-entropy)
        # Treat each row as classification over B classes
        loss = F.cross_entropy(similarity, labels)

        return loss
