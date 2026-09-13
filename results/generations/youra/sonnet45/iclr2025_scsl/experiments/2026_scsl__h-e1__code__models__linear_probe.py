"""Linear probe model for classification on frozen SSL embeddings.

Used for:
1. ERM baseline (standard cross-entropy)
2. Cluster-balanced retraining (reweighted cross-entropy)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


class LinearProbe(nn.Module):
    """Linear classifier for frozen SSL embeddings.

    Simple single-layer linear classifier:
        logits = W @ embeddings + b

    Args:
        input_dim: Dimension of input embeddings (default: 2048 for ResNet-50)
        num_classes: Number of output classes (default: 2 for binary)
    """

    def __init__(self, input_dim: int = 2048, num_classes: int = 2):
        super().__init__()

        self.fc = nn.Linear(input_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through linear layer.

        Args:
            x: Input embeddings of shape (batch_size, input_dim)

        Returns:
            Logits of shape (batch_size, num_classes)
        """
        return self.fc(x)


def cluster_balanced_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
    cluster_ids: torch.Tensor,
    cluster_weights: torch.Tensor
) -> torch.Tensor:
    """Cluster-balanced cross-entropy loss.

    Reweights samples by cluster membership to balance minority clusters.
    Each sample is weighted by the inverse frequency of its cluster.

    Args:
        logits: Model predictions (batch_size, num_classes)
        targets: Ground truth labels (batch_size,)
        cluster_ids: Cluster assignment for each sample (batch_size,)
        cluster_weights: Weight for each cluster (num_clusters,)

    Returns:
        Weighted cross-entropy loss (scalar)

    Reference:
        Standard ERM when cluster_weights are uniform.
        Cluster reweighting for fairness when cluster_weights are inverse-frequency.
    """
    batch_size = logits.shape[0]

    # Get per-sample weights based on cluster membership
    # cluster_ids[i] -> cluster_weights[cluster_ids[i]]
    sample_weights = cluster_weights[cluster_ids]

    # Compute weighted cross-entropy loss
    # reduction='none' gives per-sample losses
    ce_loss = F.cross_entropy(logits, targets, reduction='none')

    # Apply cluster weights and average
    # Handle edge case: if all weights are zero, fallback to standard CE
    if sample_weights.sum() == 0:
        return F.cross_entropy(logits, targets)

    weighted_loss = (ce_loss * sample_weights).sum() / sample_weights.sum()

    return weighted_loss


def compute_cluster_weights(
    cluster_labels: torch.Tensor,
    num_clusters: int = 4
) -> torch.Tensor:
    """Compute inverse-frequency weights for each cluster.

    Balances minority clusters by upweighting rare clusters.
    Weight formula: w_c = 1 / count_c (normalized)

    Args:
        cluster_labels: Cluster assignment for each sample (N,)
        num_clusters: Total number of clusters

    Returns:
        Cluster weights (num_clusters,)

    Example:
        cluster_labels = [0, 0, 0, 1, 2, 2]
        num_clusters = 3
        Counts: [3, 1, 2]
        Weights: [1/3, 1/1, 1/2] -> normalized
    """
    # Count samples in each cluster
    cluster_counts = torch.zeros(num_clusters, dtype=torch.float32)

    for c in range(num_clusters):
        cluster_counts[c] = (cluster_labels == c).sum().float()

    # Inverse frequency weighting
    # Add small epsilon to avoid division by zero
    weights = 1.0 / (cluster_counts + 1e-8)

    # Set weight to 0 for empty clusters
    weights[cluster_counts == 0] = 0.0

    # Normalize so weights sum to num_clusters (for balanced scaling)
    if weights.sum() > 0:
        weights = weights * num_clusters / weights.sum()

    return weights
