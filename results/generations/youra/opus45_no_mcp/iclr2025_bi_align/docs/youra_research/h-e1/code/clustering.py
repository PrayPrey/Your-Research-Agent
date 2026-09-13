"""K-means clustering and silhouette evaluation."""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from typing import Dict, List

from config import CONFIG


def fit_kmeans(X: np.ndarray, k: int, seed: int = 42) -> KMeans:
    """Fit KMeans clustering."""
    kmeans = KMeans(n_clusters=k, random_state=seed, n_init=10)
    kmeans.fit(X)
    return kmeans


def evaluate_k_range(X: np.ndarray, k_range: List[int]) -> Dict[int, float]:
    """Evaluate silhouette score for each k value."""
    silhouette_by_k = {}
    for k in k_range:
        if k >= len(X):
            continue
        kmeans = fit_kmeans(X, k)
        sil = silhouette_score(X, kmeans.labels_)
        silhouette_by_k[k] = sil
        print(f"  k={k}: silhouette={sil:.4f}")
    return silhouette_by_k


def select_best_k(silhouette_by_k: Dict[int, float]) -> int:
    """Select k with maximum silhouette score."""
    return max(silhouette_by_k, key=silhouette_by_k.get)


def cluster_and_evaluate(X: np.ndarray, k: int) -> Dict:
    """Fit KMeans and return full evaluation results."""
    kmeans = fit_kmeans(X, k, CONFIG.seed)
    sil_score = silhouette_score(X, kmeans.labels_)

    return {
        "silhouette_score": sil_score,
        "cluster_labels": kmeans.labels_,
        "cluster_centers": kmeans.cluster_centers_,
        "gate_passed": sil_score > CONFIG.silhouette_gate,
        "k": k
    }
