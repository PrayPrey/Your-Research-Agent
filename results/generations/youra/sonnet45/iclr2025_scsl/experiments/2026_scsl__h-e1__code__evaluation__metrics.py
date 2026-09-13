"""Evaluation metrics for spurious correlation analysis.

Metrics:
1. AMI (Adjusted Mutual Information) - cluster quality
2. WGA (Worst-Group Accuracy) - robustness to spurious correlations
3. Linear AUROC - linear separability of cluster pairs
"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from typing import Tuple, Dict


def compute_ami(
    embeddings: np.ndarray,
    groups: np.ndarray,
    num_clusters: int = 4
) -> Tuple[float, np.ndarray]:
    """Compute Adjusted Mutual Information between k-means clusters and groups.

    AMI measures how well unsupervised clusters (k-means) align with
    ground-truth spurious groups. High AMI means SSL embeddings capture
    spurious correlations.

    Args:
        embeddings: Frozen SSL embeddings (N, embedding_dim)
        groups: Ground truth group labels (N,)
        num_clusters: Number of k-means clusters (default: 4)

    Returns:
        ami: Adjusted Mutual Information score [0, 1]
        cluster_labels: Cluster assignments from k-means (N,)

    Reference:
        Vinh et al. 2010 - Information Theoretic Measures for Clusterings Comparison
    """
    # Run k-means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(embeddings)

    # Compute AMI between clusters and ground truth groups
    ami = adjusted_mutual_info_score(groups, cluster_labels)

    return ami, cluster_labels


def compute_wga(
    preds: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray
) -> Tuple[float, Dict[int, float]]:
    """Compute Worst-Group Accuracy.

    WGA is the minimum accuracy across all spurious groups.
    Measures robustness to minority groups and spurious correlations.

    Args:
        preds: Model predictions (N,)
        labels: Ground truth labels (N,)
        groups: Group membership for each sample (N,)

    Returns:
        wga: Worst-group accuracy (minimum across groups)
        group_accs: Dictionary mapping group_id -> accuracy

    Reference:
        Sagawa et al. 2020 - Distributionally Robust Neural Networks
    """
    unique_groups = np.unique(groups)
    group_accs = {}

    for g in unique_groups:
        # Get samples from this group
        group_mask = (groups == g)
        group_preds = preds[group_mask]
        group_labels = labels[group_mask]

        # Compute accuracy for this group
        accuracy = (group_preds == group_labels).mean()
        group_accs[int(g)] = float(accuracy)

    # Worst-group accuracy is minimum
    wga = min(group_accs.values())

    return wga, group_accs


def compute_linear_auroc(
    embeddings: np.ndarray,
    groups: np.ndarray
) -> float:
    """Compute linear separability of cluster pairs via AUROC.

    Trains a linear classifier to predict binary group membership
    (e.g., landbird vs waterbird) from embeddings. High AUROC means
    embeddings linearly encode the spurious feature.

    Args:
        embeddings: Frozen SSL embeddings (N, embedding_dim)
        groups: Group labels (N,) - will be binarized using midpoint

    Returns:
        auroc: Area under ROC curve for binary classification

    Reference:
        Standard metric for linear separability

    Note:
        For Waterbirds groups {0,1,2,3}, this converts to {0,0,1,1}
        (landbird vs waterbird). For other datasets, adjust the threshold.
    """
    # Binarize groups for binary classification
    # For Waterbirds: groups {0,1,2,3} -> labels {0,0,1,1} (landbird vs waterbird)
    binary_labels = (groups >= 2).astype(int)  # Convert bool to int for sklearn

    # Validate binary labels have both classes
    unique_labels = np.unique(binary_labels)
    if len(unique_labels) < 2:
        raise ValueError(
            f"Binary labels must have 2 classes, but got {len(unique_labels)}: {unique_labels}. "
            f"Groups range: {groups.min()}-{groups.max()}"
        )

    # Train logistic regression (linear classifier)
    clf = LogisticRegression(random_state=42, max_iter=1000)
    clf.fit(embeddings, binary_labels)

    # Get predicted probabilities
    probs = clf.predict_proba(embeddings)[:, 1]

    # Compute AUROC
    auroc = roc_auc_score(binary_labels, probs)

    return auroc
