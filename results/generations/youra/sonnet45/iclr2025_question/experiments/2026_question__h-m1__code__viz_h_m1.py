"""Visualization Module for Seed Independence Analysis."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import torch
from pathlib import Path
from typing import Dict
from itertools import combinations


def plot_distance_distribution(
    distances: np.ndarray,
    condition: str,
    save_path: Path,
    mean_dist: float = None,
    p_value: float = None
) -> None:
    """
    Generate histogram of pairwise distance distribution.

    Args:
        distances: Array of pairwise distances
        condition: Condition name (e.g., '1layer_mnist')
        save_path: Path to save figure
        mean_dist: Mean distance for annotation
        p_value: P-value for annotation
    """
    plt.figure(figsize=(10, 6))
    plt.hist(distances, bins=30, alpha=0.7, edgecolor='black')
    plt.xlabel('Pairwise Distance (L2 Norm)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title(f'Distance Distribution: {condition}', fontsize=14, fontweight='bold')

    # Add mean line
    if mean_dist is not None:
        plt.axvline(mean_dist, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_dist:.2f}')

    # Add p-value annotation
    if p_value is not None:
        plt.text(0.95, 0.95, f'p-value: {p_value:.4f}',
                transform=plt.gca().transAxes,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                fontsize=11)

    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_distance_heatmap(
    models_dict: Dict[int, torch.Tensor],
    condition: str,
    save_path: Path
) -> None:
    """
    Generate 30x30 heatmap of pairwise distances between seeds.

    Args:
        models_dict: Dictionary mapping seed -> parameter tensor
        condition: Condition name
        save_path: Path to save figure
    """
    seeds = sorted(models_dict.keys())
    n_seeds = len(seeds)

    # Compute full distance matrix
    dist_matrix = np.zeros((n_seeds, n_seeds))

    for i, seed_i in enumerate(seeds):
        for j, seed_j in enumerate(seeds):
            if i == j:
                dist_matrix[i, j] = 0
            elif i < j:
                params_i = models_dict[seed_i]
                params_j = models_dict[seed_j]
                dist = torch.norm(params_i - params_j, p=2).item()
                dist_matrix[i, j] = dist
                dist_matrix[j, i] = dist  # Symmetric

    # Plot heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(dist_matrix, cmap='viridis', annot=False, fmt='.1f',
                xticklabels=seeds, yticklabels=seeds, cbar_kws={'label': 'Distance (L2 Norm)'})
    plt.xlabel('Seed', fontsize=12)
    plt.ylabel('Seed', fontsize=12)
    plt.title(f'Pairwise Distance Heatmap: {condition}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_condition_comparison(
    all_results: Dict[str, Dict],
    save_path: Path
) -> None:
    """
    Generate boxplot comparing distance distributions across conditions.

    Args:
        all_results: Dictionary mapping condition -> results dict (with 'distances')
        save_path: Path to save figure
    """
    conditions = sorted(all_results.keys())
    distances_list = [all_results[cond]['distances'] for cond in conditions]

    plt.figure(figsize=(12, 7))
    bp = plt.boxplot(distances_list, labels=conditions, patch_artist=True)

    # Color boxes
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    plt.ylabel('Pairwise Distance (L2 Norm)', fontsize=12)
    plt.xlabel('Condition', fontsize=12)
    plt.title('Distance Distribution Across Conditions', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_gate_metrics(
    results: Dict[str, Dict[str, float]],
    save_path: Path,
    alpha: float = 0.05
) -> None:
    """
    Generate gate metrics comparison: p-values vs threshold.

    Args:
        results: Dictionary mapping condition -> statistics dict
        save_path: Path to save figure
        alpha: Significance level threshold (default 0.05)
    """
    conditions = sorted(results.keys())
    p_values = [results[cond]['p_value'] for cond in conditions]

    plt.figure(figsize=(12, 7))

    # Bar chart of p-values
    colors = ['green' if p < alpha else 'red' for p in p_values]
    bars = plt.bar(conditions, p_values, color=colors, alpha=0.7, edgecolor='black')

    # Add threshold line
    plt.axhline(alpha, color='red', linestyle='--', linewidth=2, label=f'Threshold (α={alpha})')

    # Add value labels on bars
    for bar, p_val in zip(bars, p_values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 0.005,
                f'{p_val:.4f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.ylabel('p-value', fontsize=12)
    plt.xlabel('Condition', fontsize=12)
    plt.title('Gate Metrics: p-values (Must be < 0.05 for PASS)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.ylim(0, max(p_values) * 1.2)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
