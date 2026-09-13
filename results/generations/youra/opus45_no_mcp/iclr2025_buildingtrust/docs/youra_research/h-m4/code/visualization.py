"""H-M4 Visualization: Scatter, box plot, gate comparison, histogram."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple


def plot_scatter_regression(
    hedging_counts: List[int],
    confidence_scores: List[float],
    r: float,
    p: float,
    output_path: Path,
    dpi: int = 150
) -> None:
    """Scatter plot with regression line."""
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.array(hedging_counts)
    y = np.array(confidence_scores)

    ax.scatter(x, y, alpha=0.5, s=30)

    z = np.polyfit(x, y, 1)
    p_line = np.poly1d(z)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, p_line(x_line), 'r-', linewidth=2, label=f'Regression (r={r:.3f})')

    ax.set_xlabel('Hedging Marker Count')
    ax.set_ylabel('Verbalized Confidence (%)')
    ax.set_title(f'H-M4: Hedging vs Confidence (r={r:.3f}, p={p:.2e})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi)
    plt.close()


def plot_box_by_bucket(
    hedging_counts: List[int],
    confidence_scores: List[float],
    buckets: List[Tuple[int, int]],
    output_path: Path,
    dpi: int = 150
) -> None:
    """Box plot of confidence by hedging bucket."""
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.array(hedging_counts)
    y = np.array(confidence_scores)

    bucket_data = []
    bucket_labels = []

    for low, high in buckets:
        mask = (x >= low) & (x <= high)
        bucket_data.append(y[mask])
        if high >= 999:
            bucket_labels.append(f'{low}+')
        elif low == high:
            bucket_labels.append(str(low))
        else:
            bucket_labels.append(f'{low}-{high}')

    ax.boxplot(bucket_data, labels=bucket_labels)
    ax.set_xlabel('Hedging Marker Count')
    ax.set_ylabel('Verbalized Confidence (%)')
    ax.set_title('H-M4: Confidence Distribution by Hedging Bucket')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi)
    plt.close()


def plot_gate_comparison(
    gate_metrics: Dict,
    output_path: Path,
    dpi: int = 150
) -> None:
    """Bar chart comparing threshold vs actual r."""
    fig, ax = plt.subplots(figsize=(6, 5))

    threshold = gate_metrics['gate_1_threshold']
    actual = gate_metrics['spearman_r']

    x_pos = [0, 1]
    values = [threshold, actual]
    colors = ['gray', 'green' if gate_metrics['gate_1_r_pass'] else 'red']
    labels = ['Threshold', 'Actual r']

    bars = ax.bar(x_pos, values, color=colors, width=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Spearman r')
    ax.set_title(f"H-M4 Gate: r < {threshold} ({'PASS' if gate_metrics['gate_1_r_pass'] else 'FAIL'})")
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.grid(True, alpha=0.3, axis='y')

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, val, f'{val:.3f}',
                ha='center', va='bottom' if val >= 0 else 'top')

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi)
    plt.close()


def plot_hedging_histogram(
    hedging_counts: List[int],
    output_path: Path,
    dpi: int = 150
) -> None:
    """Histogram of hedging marker counts."""
    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.array(hedging_counts)
    max_count = min(int(x.max()), 20)
    bins = range(0, max_count + 2)

    ax.hist(x, bins=bins, edgecolor='black', alpha=0.7)
    ax.set_xlabel('Hedging Marker Count')
    ax.set_ylabel('Frequency')
    ax.set_title(f'H-M4: Hedging Marker Distribution (n={len(x)})')
    ax.grid(True, alpha=0.3, axis='y')

    mean_val = x.mean()
    ax.axvline(x=mean_val, color='red', linestyle='--', label=f'Mean={mean_val:.2f}')
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi)
    plt.close()
