"""SimCLR model with ResNet-50 encoder and projection head.

Reference: Chen et al. 2020 - A Simple Framework for Contrastive Learning
Implementation adapted from sthalles/SimCLR (GitHub)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
from typing import Tuple


class SimCLR(nn.Module):
    """SimCLR model with ResNet-50 encoder and MLP projection head.

    Architecture:
        - Encoder: ResNet-50 (pretrained=False) → 2048-dim embeddings
        - Projection Head: MLP (2048 → 2048 → 128) with ReLU

    Args:
        encoder_name: Name of encoder architecture (default: 'resnet50')
        projection_dim: Dimension of projection space (default: 128)
        pretrained: Whether to use pretrained encoder (default: False for SSL)
    """

    def __init__(
        self,
        encoder_name: str = 'resnet50',
        projection_dim: int = 128,
        pretrained: bool = False
    ):
        super().__init__()

        # Initialize encoder (ResNet-50)
        if encoder_name == 'resnet50':
            base_model = models.resnet50(pretrained=pretrained)
            # Remove classification head
            self.encoder = nn.Sequential(*list(base_model.children())[:-1])
            self.embedding_dim = 2048
        else:
            raise ValueError(f"Unsupported encoder: {encoder_name}")

        # Projection head: 2048 → 2048 → 128 with ReLU
        self.projection_head = nn.Sequential(
            nn.Linear(self.embedding_dim, self.embedding_dim),
            nn.ReLU(),
            nn.Linear(self.embedding_dim, projection_dim)
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass through encoder and projection head.

        Args:
            x: Input images of shape (batch_size, 3, 224, 224)

        Returns:
            embeddings: 2048-dim encoder output (for downstream tasks)
            projections: 128-dim projected embeddings (for contrastive loss)
        """
        # Extract embeddings from encoder
        embeddings = self.encoder(x)
        embeddings = embeddings.view(embeddings.size(0), -1)  # Flatten

        # Project to contrastive space
        projections = self.projection_head(embeddings)

        return embeddings, projections

    def get_encoder(self) -> nn.Module:
        """Get the encoder module for downstream tasks.

        Returns:
            Encoder module (can be frozen for linear probing)
        """
        return self.encoder


def nt_xent_loss(
    z_i: torch.Tensor,
    z_j: torch.Tensor,
    temperature: float = 0.5
) -> torch.Tensor:
    """Normalized Temperature-scaled Cross Entropy (NT-Xent) loss.

    Also known as InfoNCE loss for contrastive learning.
    Attracts positive pairs (i, j) and repels negative pairs.

    Args:
        z_i: Projections from first augmentation (batch_size, projection_dim)
        z_j: Projections from second augmentation (batch_size, projection_dim)
        temperature: Temperature scaling parameter (default: 0.5)

    Returns:
        Scalar loss value

    Reference:
        Chen et al. 2020, Equation 1
        https://github.com/sthalles/SimCLR
    """
    batch_size = z_i.shape[0]

    # Concatenate representations: [z_i; z_j] -> 2N x D
    z = torch.cat([z_i, z_j], dim=0)

    # Compute cosine similarity matrix: 2N x 2N
    # F.cosine_similarity works along dim 2
    similarity_matrix = F.cosine_similarity(
        z.unsqueeze(1), z.unsqueeze(0), dim=2
    ) / temperature

    # Create mask to remove self-similarity (diagonal)
    mask = torch.eye(2 * batch_size, dtype=torch.bool, device=z.device)
    similarity_matrix = similarity_matrix.masked_fill(mask, -1e9)

    # Positive pairs: (i, j+N) and (j+N, i)
    # First N samples paired with second N samples
    positive_indices_i = torch.arange(batch_size, 2 * batch_size, device=z.device)
    positive_indices_j = torch.arange(batch_size, device=z.device)

    # Extract positive similarities
    pos_sim_i = similarity_matrix[
        torch.arange(batch_size, device=z.device), positive_indices_i
    ]
    pos_sim_j = similarity_matrix[
        positive_indices_i, positive_indices_j
    ]

    # All similarities (excluding self) are negatives
    # Positive similarities are part of this set and will be the highest
    # We want: exp(pos_sim) / sum(exp(all_sims_except_self))

    # Compute log-sum-exp for numerical stability
    # For sample i: -log[ exp(sim(i,j)) / sum_k exp(sim(i,k)) ]
    logits_i = similarity_matrix[:batch_size]  # First N rows
    logits_j = similarity_matrix[batch_size:]  # Second N rows

    # Compute cross-entropy loss
    # The positive pair should have highest similarity
    labels_i = torch.arange(batch_size, 2 * batch_size, device=z.device)
    labels_j = torch.arange(batch_size, device=z.device)

    loss_i = F.cross_entropy(logits_i, labels_i)
    loss_j = F.cross_entropy(logits_j, labels_j)

    # Average over both views
    loss = (loss_i + loss_j) / 2

    return loss
