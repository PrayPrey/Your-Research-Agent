"""Visualization for H-M1 reward conflation analysis."""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List


def setup_style():
    """Set consistent plot style."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['savefig.dpi'] = 150
    plt.rcParams['font.size'] = 10


def plot_gate_metrics(
    overlap: float, mean_diff: float,
    overlap_gate: float, mean_diff_gate: float,
    out_path: str
) -> None:
    """Bar plot comparing metrics to gate thresholds."""
    setup_style()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Overlap
    colors = ['green' if overlap > overlap_gate else 'red', 'gray']
    axes[0].bar(['Measured', 'Threshold'], [overlap, overlap_gate], color=colors)
    axes[0].set_ylabel('Distribution Overlap')
    axes[0].set_title(f'Overlap: {overlap:.3f} (gate: >{overlap_gate})')
    axes[0].set_ylim(0, 1)

    # Mean Diff
    colors = ['green' if mean_diff < mean_diff_gate else 'red', 'gray']
    axes[1].bar(['Measured', 'Threshold'], [mean_diff, mean_diff_gate], color=colors)
    axes[1].set_ylabel('Mean Confidence Difference')
    axes[1].set_title(f'Mean Diff: {mean_diff:.3f} (gate: <{mean_diff_gate})')

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_confidence_histograms(
    dist_a: np.ndarray, dist_b: np.ndarray, out_path: str
) -> None:
    """Overlapping histograms for Type A vs Type B."""
    setup_style()
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(dist_a, bins=50, alpha=0.5, label=f'Type A (n={len(dist_a)})', color='blue', density=True)
    ax.hist(dist_b, bins=50, alpha=0.5, label=f'Type B (n={len(dist_b)})', color='orange', density=True)

    ax.axvline(np.mean(dist_a), color='blue', linestyle='--', label=f'Mean A: {np.mean(dist_a):.3f}')
    ax.axvline(np.mean(dist_b), color='orange', linestyle='--', label=f'Mean B: {np.mean(dist_b):.3f}')

    ax.set_xlabel('Confidence')
    ax.set_ylabel('Density')
    ax.set_title('Confidence Distribution: Type A (Correctness) vs Type B (User-Modeling)')
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_cross_model_heatmap(
    overlap_by_model: Dict[str, float], out_path: str
) -> None:
    """Heatmap of overlap scores across models."""
    setup_style()

    models = list(overlap_by_model.keys())
    model_short = [m.split('/')[-1][:20] for m in models]
    values = [overlap_by_model[m] for m in models]

    fig, ax = plt.subplots(figsize=(8, 3))

    # Single-row heatmap
    data = np.array([values])
    sns.heatmap(data, annot=True, fmt='.3f', cmap='RdYlGn',
                xticklabels=model_short, yticklabels=['Overlap'],
                ax=ax, vmin=0, vmax=1, cbar_kws={'label': 'Overlap Score'})

    ax.set_title('Cross-Model Confidence Overlap (Type A vs Type B)')

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_cluster_correlation_scatter(
    cluster_labels: List[int], task_types: List[str],
    r: float, out_path: str
) -> None:
    """Scatter plot with jitter showing cluster vs task type."""
    setup_style()
    fig, ax = plt.subplots(figsize=(8, 5))

    type_binary = np.array([1 if t == "B" else 0 for t in task_types])
    clusters = np.array(cluster_labels)

    # Add jitter for visibility
    x_jitter = clusters + np.random.normal(0, 0.1, len(clusters))
    y_jitter = type_binary + np.random.normal(0, 0.1, len(type_binary))

    ax.scatter(x_jitter, y_jitter, alpha=0.3, s=10)

    ax.set_xlabel('Cluster Label')
    ax.set_ylabel('Task Type (0=A, 1=B)')
    ax.set_title(f'Cluster-TaskType Correlation: r={r:.3f}')
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Type A', 'Type B'])

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_per_dataset_overlap(
    overlap_by_dataset: Dict[str, float], out_path: str
) -> None:
    """Bar chart of overlap per dataset (ABL-3)."""
    setup_style()
    fig, ax = plt.subplots(figsize=(8, 4))

    datasets = list(overlap_by_dataset.keys())
    values = [overlap_by_dataset[d] for d in datasets]

    colors = ['green' if v > 0.7 else 'orange' if v > 0.5 else 'red' for v in values]
    ax.bar(datasets, values, color=colors)
    ax.axhline(0.7, color='green', linestyle='--', label='Pass threshold (0.7)')
    ax.axhline(0.5, color='red', linestyle='--', label='Fail threshold (0.5)')

    ax.set_ylabel('Distribution Overlap')
    ax.set_title('Per-Dataset Overlap Analysis (ABL-3)')
    ax.set_ylim(0, 1)
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")
