"""Statistical Analysis Module for Seed Independence."""

import torch
import numpy as np
from scipy import stats
from itertools import combinations
from typing import Dict


def compute_pairwise_distances(models_dict: Dict[int, torch.Tensor]) -> np.ndarray:
    """
    Compute Euclidean distances between all parameter pairs.

    Args:
        models_dict: Dictionary mapping seed -> parameter tensor

    Returns:
        Array of pairwise distances (n_models choose 2 pairs)
    """
    distances = []

    for (seed_i, params_i), (seed_j, params_j) in combinations(models_dict.items(), 2):
        # Euclidean distance (L2 norm)
        dist = torch.norm(params_i - params_j, p=2).item()
        distances.append(dist)

    return np.array(distances)


def test_independence(distances: np.ndarray) -> Dict[str, float]:
    """
    Statistical test: H0: mean_distance = 0 vs H1: mean_distance > 0.

    Args:
        distances: Array of pairwise distances

    Returns:
        Dictionary with test statistics and p-value
    """
    mean_dist = float(np.mean(distances))
    std_dist = float(np.std(distances, ddof=1))  # Sample std deviation

    # One-sample t-test (greater than 0)
    t_stat, p_value = stats.ttest_1samp(distances, 0, alternative='greater')

    return {
        'mean_distance': mean_dist,
        'std_distance': std_dist,
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'n_pairs': len(distances)
    }


def compute_all_statistics(models_dict: Dict[int, torch.Tensor]) -> Dict[str, float]:
    """
    Compute pairwise distances and test statistics.

    Args:
        models_dict: Dictionary mapping seed -> parameter tensor

    Returns:
        Dictionary with all statistics
    """
    distances = compute_pairwise_distances(models_dict)
    stats_dict = test_independence(distances)
    stats_dict['distances'] = distances  # Include raw distances for visualization
    return stats_dict
