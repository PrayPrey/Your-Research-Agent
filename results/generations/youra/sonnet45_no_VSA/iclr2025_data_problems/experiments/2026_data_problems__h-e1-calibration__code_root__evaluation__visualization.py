"""Reliability diagram visualization."""
import matplotlib.pyplot as plt
import numpy as np
from .ece import compute_bin_statistics


def plot_reliability_diagram(
    confidences,
    labels,
    predictions=None,
    n_bins=10,
    save_path=None,
    title="Reliability Diagram"
):
    """
    Generate reliability diagram (confidence vs accuracy).

    Args:
        confidences: [N] confidence scores
        labels: [N] ground truth labels
        predictions: [N] predicted labels (if None, use confidences > 0.5)
        n_bins: number of bins
        save_path: path to save figure (optional)
        title: plot title

    Returns:
        matplotlib Figure
    """
    if predictions is None:
        predictions = (confidences > 0.5).astype(int)

    correctness = (predictions == labels).astype(float)

    # Compute bin statistics
    bin_centers, bin_accuracies, bin_counts = compute_bin_statistics(
        confidences, correctness, n_bins
    )

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    # Plot reliability curve
    valid_bins = ~np.isnan(bin_accuracies)
    ax.plot(
        bin_centers[valid_bins],
        bin_accuracies[valid_bins],
        marker='o',
        linewidth=2,
        markersize=8,
        label='Model'
    )

    # Plot perfect calibration line
    ax.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfect Calibration')

    # Add histogram of bin populations
    ax2 = ax.twinx()
    ax2.bar(
        bin_centers,
        bin_counts,
        width=0.08,
        alpha=0.3,
        color='blue',
        label='Count'
    )
    ax2.set_ylabel('Sample Count', fontsize=12)

    # Formatting
    ax.set_xlabel('Confidence', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax.grid(alpha=0.3)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[Plot] Saved reliability diagram to {save_path}")

    return fig
