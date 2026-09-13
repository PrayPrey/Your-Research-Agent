"""Visualization for H-E1: Model Zoo Dataset Validity."""

import numpy as np
import matplotlib.pyplot as plt
import os


def plot_gate_comparison(stats: dict, out_dir: str) -> None:
    """Bar chart: observed std vs GATE_THRESHOLD."""
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4))

    observed = stats["std"]
    threshold = stats["gate_threshold"]
    color = "green" if stats["gate_passed"] else "red"

    bars = ax.bar(["Observed σ", "Threshold"], [observed, threshold], color=[color, "gray"])
    ax.axhline(y=threshold, color="black", linestyle="--", alpha=0.5)

    ax.set_ylabel("Accuracy Std Dev (%)")
    ax.set_title(f"H-E1 Gate: {'PASS' if stats['gate_passed'] else 'FAIL'}")
    ax.set_ylim(0, max(observed, threshold) * 1.3)

    for bar, val in zip(bars, [observed, threshold]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{val:.1f}%", ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gate_comparison.png"), dpi=150)
    plt.close()


def plot_histogram(accuracies: np.ndarray, stats: dict, out_dir: str) -> None:
    """Histogram of accuracies with mean/std annotations."""
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(accuracies, bins=50, edgecolor="black", alpha=0.7)
    ax.axvline(stats["mean"], color="red", linestyle="-", linewidth=2, label=f"Mean: {stats['mean']:.1f}%")
    ax.axvline(stats["mean"] - stats["std"], color="orange", linestyle="--", label=f"±σ: {stats['std']:.1f}%")
    ax.axvline(stats["mean"] + stats["std"], color="orange", linestyle="--")

    ax.set_xlabel("Test Accuracy (%)")
    ax.set_ylabel("Count")
    ax.set_title(f"Model Zoo Accuracy Distribution (N={stats['n_samples']})")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "histogram.png"), dpi=150)
    plt.close()


def plot_boxplot(accuracies: np.ndarray, out_dir: str) -> None:
    """Boxplot with quartiles/outliers."""
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 5))

    bp = ax.boxplot(accuracies, vert=True, patch_artist=True)
    bp["boxes"][0].set_facecolor("lightblue")

    ax.set_ylabel("Test Accuracy (%)")
    ax.set_title("Model Zoo Accuracy Box Plot")
    ax.set_xticklabels(["CIFAR-10 Models"])

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "boxplot.png"), dpi=150)
    plt.close()
