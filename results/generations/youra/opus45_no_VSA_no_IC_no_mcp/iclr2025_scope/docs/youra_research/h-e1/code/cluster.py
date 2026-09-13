"""H-E1: KMeans clustering and evaluation metrics."""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

from config import N_CLUSTERS, RANDOM_SEED


def run_kmeans(embeddings: np.ndarray, k: int = N_CLUSTERS, seed: int = RANDOM_SEED) -> np.ndarray:
    """Fit KMeans and return cluster assignments."""
    kmeans = KMeans(n_clusters=k, random_state=seed, n_init=10)
    return kmeans.fit_predict(embeddings)


def cluster_purity(cluster_ids: np.ndarray, task_labels: np.ndarray) -> float:
    """Compute cluster purity: fraction of samples in majority class per cluster."""
    n = len(cluster_ids)
    total = 0
    for c in np.unique(cluster_ids):
        mask = cluster_ids == c
        if mask.sum() == 0:
            continue
        counts = np.bincount(task_labels[mask])
        total += counts.max()
    return total / n


def compute_ari(cluster_ids: np.ndarray, task_labels: np.ndarray) -> float:
    """Compute Adjusted Rand Index."""
    return adjusted_rand_score(task_labels, cluster_ids)


def compute_nmi(cluster_ids: np.ndarray, task_labels: np.ndarray) -> float:
    """Compute Normalized Mutual Information."""
    return normalized_mutual_info_score(task_labels, cluster_ids)


def evaluate(cluster_ids: np.ndarray, task_labels: np.ndarray) -> dict:
    """Compute all clustering metrics."""
    return {
        "purity": cluster_purity(cluster_ids, task_labels),
        "ari": compute_ari(cluster_ids, task_labels),
        "nmi": compute_nmi(cluster_ids, task_labels),
    }
