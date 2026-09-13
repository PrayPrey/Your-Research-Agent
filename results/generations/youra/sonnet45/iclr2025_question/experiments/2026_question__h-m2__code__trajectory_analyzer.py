"""Trajectory analysis module for H-M2."""

import numpy as np
import torch
from typing import Dict
from scipy.spatial.distance import pdist
from scipy.stats import ttest_1samp


def calculate_loss_cv(loss_trajectories: np.ndarray) -> float:
    """
    Compute coefficient of variation for final epoch losses.

    Args:
        loss_trajectories: [n_seeds, n_epochs] array

    Returns:
        CV as percentage
    """
    final_losses = loss_trajectories[:, -1]
    cv = (np.std(final_losses) / np.mean(final_losses)) * 100
    return float(cv)


def compute_epoch_wise_cv(loss_trajectories: np.ndarray) -> np.ndarray:
    """
    Compute CV for each epoch.

    Returns:
        Array [n_epochs] of CV values
    """
    n_epochs = loss_trajectories.shape[1]
    cv_per_epoch = []

    for epoch in range(n_epochs):
        epoch_losses = loss_trajectories[:, epoch]
        cv = (np.std(epoch_losses) / np.mean(epoch_losses)) * 100
        cv_per_epoch.append(cv)

    return np.array(cv_per_epoch)


def compute_pairwise_distances(weights_dict: Dict[int, torch.Tensor]) -> np.ndarray:
    """
    Compute all pairwise Euclidean distances between weight configurations.

    Args:
        weights_dict: Dict mapping seed -> flattened weight tensor

    Returns:
        Condensed distance array [(n choose 2),]
    """
    # Stack all weight vectors into matrix
    n_seeds = len(weights_dict)
    weights_list = [weights_dict[i].numpy() for i in range(n_seeds)]
    weight_matrix = np.stack(weights_list, axis=0)  # [n_seeds, n_params]

    # Compute pairwise distances
    distances = pdist(weight_matrix, metric='euclidean')
    return distances


def test_distance_significance(distances: np.ndarray) -> Dict[str, float]:
    """
    One-sample t-test: H0: mean=0 vs H1: mean>0

    Returns:
        Dict with keys: mean_distance, std_distance, t_statistic, p_value, n_pairs
    """
    t_stat, p_value = ttest_1samp(distances, 0, alternative='greater')
    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    n_pairs = len(distances)

    return {
        'mean_distance': float(mean_dist),
        'std_distance': float(std_dist),
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'n_pairs': int(n_pairs)
    }


def analyze_weight_divergence(
    final_weights_dict: Dict[int, torch.Tensor]
) -> Dict[str, float]:
    """
    Compute pairwise distances and significance test.

    Returns:
        Dict with statistics including 'distances' array
    """
    distances = compute_pairwise_distances(final_weights_dict)
    stats = test_distance_significance(distances)
    stats['distances'] = distances  # Include for visualization
    return stats
