"""
Visualization Module for H-E1

Generates figures for the Grassmann distance analysis results.
"""

import os
import json
import logging

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from config import FIGURES_DIR, TASK_CATEGORIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


def plot_cluster_bar(stats: dict, out_dir: str) -> None:
    """
    Bar chart: within vs between means with std error bars + p/d annotation.

    Args:
        stats: Statistical results dict
        out_dir: Output directory for figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    categories = ['Within-Cluster', 'Between-Cluster']
    means = [stats['within_mean'], stats['between_mean']]
    stds = [stats['within_std'], stats['between_std']]

    # Calculate standard errors
    n_within = stats.get('within_n', 1)
    n_between = stats.get('between_n', 1)
    ses = [
        stats['within_std'] / np.sqrt(n_within),
        stats['between_std'] / np.sqrt(n_between)
    ]

    colors = ['#3498db', '#e74c3c']
    bars = ax.bar(categories, means, yerr=ses, capsize=5, color=colors, alpha=0.8)

    ax.set_ylabel('Grassmann Distance', fontsize=12)
    ax.set_title('Within-Cluster vs Between-Cluster Grassmann Distances', fontsize=14)

    # Add significance annotation
    p_value = stats['p_value']
    cohens_d = stats['cohens_d']

    if p_value < 0.001:
        p_text = "p < 0.001"
    else:
        p_text = f"p = {p_value:.4f}"

    significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"

    # Add annotation box
    textstr = f'{p_text}\nCohen\'s d = {cohens_d:.2f}\n{significance}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)

    # Add value labels on bars
    for bar, mean, se in zip(bars, means, ses):
        height = bar.get_height()
        ax.annotate(f'{mean:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height + se),
                    ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'cluster_comparison_bar.png'), dpi=150)
    plt.close()

    logger.info("Saved: cluster_comparison_bar.png")


def plot_distance_distributions(
    within: np.ndarray,
    between: np.ndarray,
    out_dir: str
) -> None:
    """
    KDE/histogram overlay of within vs between distance distributions.

    Args:
        within: Within-cluster distances
        between: Between-cluster distances
        out_dir: Output directory for figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot histograms with KDE
    sns.histplot(within, kde=True, stat='density', alpha=0.5,
                 label=f'Within-Cluster (n={len(within)})', color='#3498db', ax=ax)
    sns.histplot(between, kde=True, stat='density', alpha=0.5,
                 label=f'Between-Cluster (n={len(between)})', color='#e74c3c', ax=ax)

    # Add mean lines
    ax.axvline(np.mean(within), color='#2980b9', linestyle='--', linewidth=2,
               label=f'Within Mean: {np.mean(within):.3f}')
    ax.axvline(np.mean(between), color='#c0392b', linestyle='--', linewidth=2,
               label=f'Between Mean: {np.mean(between):.3f}')

    ax.set_xlabel('Grassmann Distance', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.set_title('Distribution of Pairwise Grassmann Distances', fontsize=14)
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'distance_distributions.png'), dpi=150)
    plt.close()

    logger.info("Saved: distance_distributions.png")


def plot_distance_heatmap(
    distance_matrix: np.ndarray,
    adapter_meta: list,
    out_dir: str
) -> None:
    """
    Annotated heatmap of pairwise distances with category color blocks.

    Args:
        distance_matrix: [n, n] symmetric distance matrix
        adapter_meta: List of adapter metadata dicts
        out_dir: Output directory for figure
    """
    n = len(adapter_meta)

    # Sort by category for better visualization
    sorted_indices = sorted(range(n), key=lambda i: (adapter_meta[i]['category'], adapter_meta[i]['task']))
    sorted_matrix = distance_matrix[np.ix_(sorted_indices, sorted_indices)]
    sorted_meta = [adapter_meta[i] for i in sorted_indices]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot heatmap
    im = ax.imshow(sorted_matrix, cmap='viridis', aspect='auto')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Grassmann Distance', fontsize=12)

    # Add category boundaries
    categories = [m['category'] for m in sorted_meta]
    boundaries = []
    for i in range(1, len(categories)):
        if categories[i] != categories[i-1]:
            boundaries.append(i)

    for b in boundaries:
        ax.axhline(y=b - 0.5, color='white', linewidth=2)
        ax.axvline(x=b - 0.5, color='white', linewidth=2)

    # Labels
    ax.set_title('Pairwise Grassmann Distance Matrix\n(sorted by category)', fontsize=14)
    ax.set_xlabel('Adapter Index', fontsize=12)
    ax.set_ylabel('Adapter Index', fontsize=12)

    # Add category labels
    if boundaries:
        midpoints = [boundaries[0] / 2]
        for i in range(len(boundaries) - 1):
            midpoints.append((boundaries[i] + boundaries[i+1]) / 2)
        midpoints.append((boundaries[-1] + n) / 2)

        unique_cats = []
        prev_cat = None
        for cat in categories:
            if cat != prev_cat:
                unique_cats.append(cat)
                prev_cat = cat

        for mp, cat in zip(midpoints, unique_cats):
            ax.text(-0.02, mp / n, cat.upper(), transform=ax.transAxes,
                    fontsize=10, va='center', ha='right', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'distance_heatmap.png'), dpi=150)
    plt.close()

    logger.info("Saved: distance_heatmap.png")


def plot_per_category_boxplot(
    distance_matrix: np.ndarray,
    adapter_meta: list,
    out_dir: str
) -> None:
    """
    Box plot of distances grouped by task category pairs.

    Args:
        distance_matrix: [n, n] symmetric distance matrix
        adapter_meta: List of adapter metadata dicts
        out_dir: Output directory for figure
    """
    n = len(adapter_meta)

    # Collect distances by category pair
    category_pairs = {}

    for i in range(n):
        for j in range(i + 1, n):
            cat_i = adapter_meta[i]['category']
            cat_j = adapter_meta[j]['category']

            # Create consistent pair key
            pair = tuple(sorted([cat_i, cat_j]))
            if pair not in category_pairs:
                category_pairs[pair] = []
            category_pairs[pair].append(distance_matrix[i, j])

    # Prepare data for plotting
    labels = []
    data = []

    for pair, distances in sorted(category_pairs.items()):
        if pair[0] == pair[1]:
            label = f'{pair[0]}-{pair[0]}\n(within)'
        else:
            label = f'{pair[0]}-{pair[1]}\n(between)'
        labels.append(label)
        data.append(distances)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    bp = ax.boxplot(data, labels=labels, patch_artist=True)

    # Color boxes
    colors = ['#3498db' if 'within' in l else '#e74c3c' for l in labels]
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ax.set_ylabel('Grassmann Distance', fontsize=12)
    ax.set_xlabel('Category Pair', fontsize=12)
    ax.set_title('Grassmann Distances by Category Pair', fontsize=14)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#3498db', alpha=0.6, label='Within-Cluster'),
        Patch(facecolor='#e74c3c', alpha=0.6, label='Between-Cluster'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'category_boxplot.png'), dpi=150)
    plt.close()

    logger.info("Saved: category_boxplot.png")


def generate_all_figures(
    hypothesis_folder: str,
    stats: dict,
    distance_matrix: np.ndarray,
    adapter_meta: list
) -> None:
    """
    Generate all figures for the validation report.

    Args:
        hypothesis_folder: Base folder for hypothesis
        stats: Statistical results dict
        distance_matrix: [n, n] pairwise distance matrix
        adapter_meta: List of adapter metadata dicts
    """
    figures_dir = os.path.join(hypothesis_folder, "figures")
    os.makedirs(figures_dir, exist_ok=True)

    # Load within/between arrays
    results_dir = os.path.join(hypothesis_folder, "results")
    within = np.load(os.path.join(results_dir, "within_distances.npy"))
    between = np.load(os.path.join(results_dir, "between_distances.npy"))

    logger.info("Generating figures...")

    # Generate all plots
    plot_cluster_bar(stats, figures_dir)
    plot_distance_distributions(within, between, figures_dir)
    plot_distance_heatmap(distance_matrix, adapter_meta, figures_dir)
    plot_per_category_boxplot(distance_matrix, adapter_meta, figures_dir)

    logger.info(f"All figures saved to: {figures_dir}")


if __name__ == "__main__":
    from config import HYPOTHESIS_FOLDER

    # Load results
    results_dir = os.path.join(HYPOTHESIS_FOLDER, "results")

    with open(os.path.join(results_dir, "statistical_results.json")) as f:
        stats = json.load(f)

    with open(os.path.join(results_dir, "adapter_metadata.json")) as f:
        adapter_meta = json.load(f)

    distance_matrix = np.load(os.path.join(results_dir, "pairwise_distances.npy"))

    generate_all_figures(HYPOTHESIS_FOLDER, stats, distance_matrix, adapter_meta)
