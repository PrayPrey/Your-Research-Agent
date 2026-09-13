"""
Evaluation utilities for model fingerprinting.
"""

import torch
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from typing import Dict, List, Tuple
import json


def compute_similarity_matrix(embeddings: np.ndarray, metric='cosine') -> np.ndarray:
    """Compute pairwise similarity matrix."""
    if metric == 'cosine':
        return cosine_similarity(embeddings)
    elif metric == 'euclidean':
        distances = euclidean_distances(embeddings)
        # Convert distances to similarities
        return 1.0 / (1.0 + distances)
    else:
        raise ValueError(f"Unknown metric: {metric}")


def evaluate_provenance_tracking(
    embeddings: np.ndarray,
    base_ids: List[str],
    variant_to_base: Dict[str, str],
    top_k_values: List[int] = [1, 5, 10]
) -> Dict[str, float]:
    """
    Evaluate provenance tracking performance.

    Args:
        embeddings: Model embeddings
        base_ids: List of base model IDs
        variant_to_base: Mapping from variant ID to base ID
        top_k_values: K values for top-k accuracy

    Returns:
        Dictionary of metrics
    """
    results = {}

    # Build index mapping
    id_to_idx = {id_: i for i, id_ in enumerate(base_ids)}

    # Compute similarity matrix
    similarities = compute_similarity_matrix(embeddings)

    # For each variant, find nearest base models
    correct_at_k = {k: 0 for k in top_k_values}
    total_variants = len(variant_to_base)

    for variant_id, true_base_id in variant_to_base.items():
        if variant_id not in id_to_idx or true_base_id not in id_to_idx:
            continue

        variant_idx = id_to_idx[variant_id]
        true_base_idx = id_to_idx[true_base_id]

        # Get similarities to all base models
        variant_similarities = similarities[variant_idx]

        # Sort by similarity (descending)
        sorted_indices = np.argsort(-variant_similarities)

        # Check if true base is in top-k
        for k in top_k_values:
            if true_base_idx in sorted_indices[:k]:
                correct_at_k[k] += 1

    # Compute top-k accuracies
    for k in top_k_values:
        results[f'top_{k}_accuracy'] = correct_at_k[k] / max(total_variants, 1)

    return results


def evaluate_symmetry_invariance(
    base_embeddings: np.ndarray,
    variant_embeddings_list: List[np.ndarray]
) -> Dict[str, float]:
    """
    Evaluate how invariant embeddings are to symmetry transformations.

    Args:
        base_embeddings: Embeddings of base models [N, D]
        variant_embeddings_list: List of variant embeddings for each base [N, M, D]

    Returns:
        Dictionary of metrics
    """
    similarities = []
    distances = []

    for i, base_emb in enumerate(base_embeddings):
        if i < len(variant_embeddings_list):
            variant_embs = variant_embeddings_list[i]

            for variant_emb in variant_embs:
                # Cosine similarity
                sim = np.dot(base_emb, variant_emb) / (
                    np.linalg.norm(base_emb) * np.linalg.norm(variant_emb) + 1e-8
                )
                similarities.append(sim)

                # Euclidean distance
                dist = np.linalg.norm(base_emb - variant_emb)
                distances.append(dist)

    results = {
        'mean_similarity': float(np.mean(similarities)) if similarities else 0.0,
        'std_similarity': float(np.std(similarities)) if similarities else 0.0,
        'mean_distance': float(np.mean(distances)) if distances else 0.0,
        'std_distance': float(np.std(distances)) if distances else 0.0,
        'min_similarity': float(np.min(similarities)) if similarities else 0.0,
        'max_similarity': float(np.max(similarities)) if similarities else 0.0
    }

    return results


def evaluate_backdoor_detection(
    clean_embeddings: np.ndarray,
    backdoor_embeddings: np.ndarray,
    labels: np.ndarray
) -> Dict[str, float]:
    """
    Evaluate backdoor detection performance.

    Args:
        clean_embeddings: Embeddings of clean models
        backdoor_embeddings: Embeddings of backdoored models
        labels: Binary labels (0=clean, 1=backdoor)

    Returns:
        Dictionary of metrics
    """
    all_embeddings = np.vstack([clean_embeddings, backdoor_embeddings])

    # Compute centroid of clean models
    clean_centroid = np.mean(clean_embeddings, axis=0)

    # Compute distances to clean centroid
    distances = np.linalg.norm(all_embeddings - clean_centroid, axis=1)

    # Compute ROC AUC
    try:
        auroc = roc_auc_score(labels, distances)
    except:
        auroc = 0.5

    # Compute precision-recall at different thresholds
    precision, recall, thresholds = precision_recall_curve(labels, distances)

    # Find threshold for 1% FPR
    fpr_threshold = 0.01
    sorted_distances = np.sort(distances[labels == 0])
    threshold_idx = int(len(sorted_distances) * (1 - fpr_threshold))
    if threshold_idx < len(sorted_distances):
        threshold = sorted_distances[threshold_idx]
        tpr = np.mean(distances[labels == 1] > threshold)
    else:
        tpr = 0.0

    results = {
        'auroc': float(auroc),
        'tpr_at_1_fpr': float(tpr),
        'mean_clean_distance': float(np.mean(distances[labels == 0])),
        'mean_backdoor_distance': float(np.mean(distances[labels == 1])),
        'std_clean_distance': float(np.std(distances[labels == 0])),
        'std_backdoor_distance': float(np.std(distances[labels == 1]))
    }

    return results


def evaluate_discriminative_power(
    embeddings: np.ndarray,
    model_ids: List[str],
    same_architecture: bool = True
) -> Dict[str, float]:
    """
    Evaluate how well embeddings discriminate between different models.

    Args:
        embeddings: Model embeddings
        model_ids: List of model IDs
        same_architecture: Whether to only compare models of same architecture

    Returns:
        Dictionary of metrics
    """
    similarities = compute_similarity_matrix(embeddings, metric='cosine')

    # Set diagonal to -inf to ignore self-similarity
    np.fill_diagonal(similarities, -np.inf)

    # Compute statistics
    mean_similarity = float(np.mean(similarities[similarities != -np.inf]))
    std_similarity = float(np.std(similarities[similarities != -np.inf]))
    max_similarity = float(np.max(similarities[similarities != -np.inf]))

    # Compute pairwise distances
    distances = euclidean_distances(embeddings)
    np.fill_diagonal(distances, np.inf)

    mean_distance = float(np.mean(distances[distances != np.inf]))
    std_distance = float(np.std(distances[distances != np.inf]))
    min_distance = float(np.min(distances[distances != np.inf]))

    results = {
        'mean_inter_model_similarity': mean_similarity,
        'std_inter_model_similarity': std_similarity,
        'max_inter_model_similarity': max_similarity,
        'mean_inter_model_distance': mean_distance,
        'std_inter_model_distance': std_distance,
        'min_inter_model_distance': min_distance
    }

    return results


class MetricsTracker:
    """Track and aggregate metrics across experiments."""
    def __init__(self):
        self.metrics = {}
        self.history = []

    def update(self, metrics: Dict[str, float], prefix: str = ""):
        """Update metrics with optional prefix."""
        for key, value in metrics.items():
            full_key = f"{prefix}/{key}" if prefix else key
            if full_key not in self.metrics:
                self.metrics[full_key] = []
            self.metrics[full_key].append(value)

    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics for all metrics."""
        summary = {}
        for key, values in self.metrics.items():
            summary[key] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'last': float(values[-1]) if values else 0.0
            }
        return summary

    def save(self, filepath: str):
        """Save metrics to JSON file."""
        summary = self.get_summary()
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)

    def load(self, filepath: str):
        """Load metrics from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        # Convert back to lists
        for key, stats in data.items():
            self.metrics[key] = [stats['last']]


if __name__ == "__main__":
    # Test evaluation functions
    print("Testing evaluation functions...")

    # Test symmetry invariance
    base_embs = np.random.randn(10, 128)
    variant_embs = [np.random.randn(5, 128) for _ in range(10)]
    results = evaluate_symmetry_invariance(base_embs, variant_embs)
    print(f"Symmetry invariance results: {results}")

    # Test backdoor detection
    clean_embs = np.random.randn(50, 128)
    backdoor_embs = np.random.randn(20, 128) + 1.0  # Shifted
    labels = np.array([0] * 50 + [1] * 20)
    results = evaluate_backdoor_detection(clean_embs, backdoor_embs, labels)
    print(f"Backdoor detection results: {results}")

    print("All tests passed!")
