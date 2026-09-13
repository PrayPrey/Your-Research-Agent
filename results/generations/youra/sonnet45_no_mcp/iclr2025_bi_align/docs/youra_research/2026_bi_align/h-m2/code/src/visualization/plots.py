"""
Visualization module for embedding analysis.
Tasks: task-011, task-012, task-013, task-014, task-015 - All required figures
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


def plot_gate_metrics_comparison(
    cohens_d: float,
    baseline_d: float,
    threshold: float,
    output_path: str
) -> None:
    """
    Bar chart: Baseline vs RoBERTa embeddings Cohen's d.
    Task: task-011
    """
    methods = ["Random Baseline", "RoBERTa Embeddings"]
    values = [baseline_d, cohens_d]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(methods, values, color=['#95a5a6', '#3498db'], alpha=0.8)

    # Add threshold line
    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Gate Threshold (d={threshold})')

    # Annotate bars with values
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.3f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel("Cohen's d Effect Size", fontsize=12)
    ax.set_title("Gate Metrics Comparison: Method vs Random Baseline", fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved gate metrics figure to {output_path}")


def plot_pca_scatter(
    chosen_2d: np.ndarray,
    rejected_2d: np.ndarray,
    variance_explained: Tuple[float, float],
    output_path: str
) -> None:
    """
    2D scatter plot of PCA projection.
    Task: task-012
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot points
    ax.scatter(chosen_2d[:, 0], chosen_2d[:, 1], c='blue', alpha=0.3, s=10, label='Chosen')
    ax.scatter(rejected_2d[:, 0], rejected_2d[:, 1], c='red', alpha=0.3, s=10, label='Rejected')

    ax.set_xlabel(f'PC1 ({variance_explained[0]*100:.1f}% variance)', fontsize=12)
    ax.set_ylabel(f'PC2 ({variance_explained[1]*100:.1f}% variance)', fontsize=12)
    ax.set_title('PCA 2D Projection: Chosen vs Rejected Responses', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved PCA scatter plot to {output_path}")


def plot_effect_size_distribution(
    per_dimension_d: np.ndarray,
    output_path: str
) -> None:
    """
    Histogram of Cohen's d across embedding dimensions.
    Task: task-013
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(per_dimension_d, bins=50, color='#3498db', alpha=0.7, edgecolor='black')

    ax.set_xlabel("Cohen's d per Dimension", fontsize=12)
    ax.set_ylabel('Frequency (Number of Dimensions)', fontsize=12)
    ax.set_title('Effect Size Distribution Across 768 Embedding Dimensions', fontsize=14, fontweight='bold')
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved effect size distribution to {output_path}")


def plot_variance_explained(
    cumulative_variance: np.ndarray,
    output_path: str
) -> None:
    """
    PCA scree plot showing cumulative variance.
    Task: task-014
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    components = np.arange(1, len(cumulative_variance) + 1)
    ax.plot(components, cumulative_variance * 100, marker='o', linewidth=2, markersize=4, color='#3498db')

    ax.set_xlabel('Principal Component Number', fontsize=12)
    ax.set_ylabel('Cumulative Variance Explained (%)', fontsize=12)
    ax.set_title('PCA Scree Plot: Cumulative Variance Explained', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3)
    ax.set_xlim(1, len(cumulative_variance))
    ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved variance scree plot to {output_path}")


def plot_distance_heatmap(
    chosen_sample: np.ndarray,
    rejected_sample: np.ndarray,
    output_path: str
) -> None:
    """
    Distance matrix heatmap for sample pairs.
    Task: task-015
    """
    # Combine samples
    combined = np.vstack([chosen_sample, rejected_sample])

    # Compute distance matrix
    from scipy.spatial.distance import cdist
    distances = cdist(combined, combined, metric='euclidean')

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(distances, cmap='viridis', ax=ax, cbar_kws={'label': 'Euclidean Distance'})

    n_chosen = len(chosen_sample)
    ax.axhline(y=n_chosen, color='red', linewidth=2)
    ax.axvline(x=n_chosen, color='red', linewidth=2)

    ax.set_xlabel('Sample Index', fontsize=12)
    ax.set_ylabel('Sample Index', fontsize=12)
    ax.set_title('Embedding Distance Heatmap (100 Chosen + 100 Rejected)', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved distance heatmap to {output_path}")
