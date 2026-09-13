"""Visualization functions for H-M2: distribution comparison plots."""

import matplotlib.pyplot as plt
import numpy as np


def plot_distribution_comparison(
    consistency_correct: np.ndarray,
    consistency_incorrect: np.ndarray,
    path: str,
) -> None:
    """Side-by-side box + violin, labels 'Correct'/'Incorrect'. Saves PNG to path."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    data = [consistency_correct, consistency_incorrect]
    labels = ["Correct", "Incorrect"]
    colors = ["#4CAF50", "#F44336"]

    # Box plot
    bp = axes[0].boxplot(data, labels=labels, patch_artist=True)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    axes[0].set_ylabel("N-Sample Consistency")
    axes[0].set_title("Distribution Comparison (Box Plot)")
    axes[0].grid(axis="y", alpha=0.3)

    # Violin plot
    vp = axes[1].violinplot(data, positions=[1, 2], showmeans=True, showmedians=True)
    for i, body in enumerate(vp["bodies"]):
        body.set_facecolor(colors[i])
        body.set_alpha(0.7)
    axes[1].set_xticks([1, 2])
    axes[1].set_xticklabels(labels)
    axes[1].set_ylabel("N-Sample Consistency")
    axes[1].set_title("Distribution Comparison (Violin Plot)")
    axes[1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_histogram_overlay(
    consistency_correct: np.ndarray,
    consistency_incorrect: np.ndarray,
    path: str,
) -> None:
    """Overlaid alpha-blended histograms, correct vs incorrect. Saves PNG to path."""
    fig, ax = plt.subplots(figsize=(10, 6))

    bins = np.linspace(
        min(consistency_correct.min(), consistency_incorrect.min()),
        max(consistency_correct.max(), consistency_incorrect.max()),
        30,
    )

    ax.hist(consistency_correct, bins=bins, alpha=0.6, label="Correct", color="#4CAF50", density=True)
    ax.hist(consistency_incorrect, bins=bins, alpha=0.6, label="Incorrect", color="#F44336", density=True)

    ax.set_xlabel("N-Sample Consistency")
    ax.set_ylabel("Density")
    ax.set_title("Consistency Distribution by Factual Correctness")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
