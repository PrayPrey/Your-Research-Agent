"""Semantic entropy computation for H-M1."""

import numpy as np
from scipy.stats import entropy
from typing import List
from entailment_clusterer import EntailmentClusterer


def compute_cluster_probs(clusters: List[List[int]], logprobs: List[float]) -> np.ndarray:
    """Aggregate probabilities per cluster, normalize to sum=1."""
    cluster_probs = []
    for cluster in clusters:
        # Sum exp(logprob) for responses in this cluster
        cluster_prob = sum(np.exp(logprobs[i]) for i in cluster)
        cluster_probs.append(cluster_prob)

    cluster_probs = np.array(cluster_probs)
    # Normalize
    total = cluster_probs.sum()
    if total > 0:
        cluster_probs = cluster_probs / total
    else:
        cluster_probs = np.ones(len(clusters)) / len(clusters)

    return cluster_probs


def compute_semantic_entropy(responses: List[str], logprobs: List[float],
                              clusterer: EntailmentClusterer, question: str) -> float:
    """Full semantic entropy computation.

    1. Cluster responses by bidirectional entailment
    2. Aggregate probabilities per cluster
    3. Compute Shannon entropy in nats
    """
    if len(responses) == 0:
        return 0.0

    if len(responses) == 1:
        return 0.0  # No uncertainty with single response

    clusters = clusterer.cluster(responses, question)
    cluster_probs = compute_cluster_probs(clusters, logprobs)

    # Shannon entropy in nats (base e)
    se = entropy(cluster_probs)

    return float(se)
