import numpy as np
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import fcluster
from typing import Dict, Tuple, List


def silhouette_score_for_k(distance_matrix: np.ndarray, labels: np.ndarray) -> float:
    # float in [-1, 1], >0.5 indicates good separation
    return silhouette_score(distance_matrix, labels, metric='precomputed')


def find_optimal_k(
    distance_matrix: np.ndarray,
    linkage_matrix: np.ndarray,
    k_range: List[int] = [2, 3, 4, 5]
) -> Tuple[int, Dict[int, float]]:
    # (optimal_k, silhouette_scores) where silhouette_scores: {k: score}
    n_samples = distance_matrix.shape[0]
    scores = {}
    for k in k_range:
        if k >= n_samples:
            continue
        labels = fcluster(linkage_matrix, k, criterion='maxclust')
        scores[k] = silhouette_score_for_k(distance_matrix, labels)
    optimal_k = max(scores, key=scores.get)
    return optimal_k, scores
