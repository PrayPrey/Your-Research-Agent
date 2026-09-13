"""Visualization for overlap results."""

import os
import matplotlib.pyplot as plt
from config import OVERLAP_THRESHOLD, FIGURES_DIR


def plot_overlap_by_benchmark(aggregated: dict[str, dict], out_path: str) -> None:
    """Bar chart: mean overlap per benchmark."""
    names = list(aggregated.keys())
    means = [aggregated[n]["mean_overlap"] * 100 for n in names]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(names, means, color="steelblue")
    ax.axhline(y=OVERLAP_THRESHOLD * 100, color="red", linestyle="--", label=f"Threshold ({OVERLAP_THRESHOLD*100}%)")
    ax.set_ylabel("Mean Overlap (%)")
    ax.set_xlabel("Benchmark")
    ax.set_title("13-gram Overlap with The Pile by Benchmark")
    ax.legend()
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f"{val:.2f}%", ha="center", va="bottom")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_overlap_histogram(results_by_benchmark: dict[str, list[dict]], out_path: str) -> None:
    """Histograms of per-item overlap per benchmark."""
    n = len(results_by_benchmark)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for i, (name, results) in enumerate(results_by_benchmark.items()):
        overlaps = [r["overlap"] * 100 for r in results]
        axes[i].hist(overlaps, bins=50, color="steelblue", edgecolor="black", alpha=0.7)
        axes[i].axvline(x=OVERLAP_THRESHOLD * 100, color="red", linestyle="--")
        axes[i].set_title(f"{name} (n={len(results)})")
        axes[i].set_xlabel("Overlap (%)")
        axes[i].set_ylabel("Count")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_comparison_with_prior_work(aggregated: dict[str, dict], out_path: str) -> None:
    """Bar chart with Yang et al. RedPajama reference band."""
    names = list(aggregated.keys())
    means = [aggregated[n]["mean_overlap"] * 100 for n in names]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(names, means, color="steelblue", label="The Pile")
    ax.axhspan(8, 18, alpha=0.2, color="orange", label="Yang et al. RedPajama (8-18%)")
    ax.axhline(y=OVERLAP_THRESHOLD * 100, color="red", linestyle="--", label=f"Threshold ({OVERLAP_THRESHOLD*100}%)")
    ax.set_ylabel("Mean Overlap (%)")
    ax.set_xlabel("Benchmark")
    ax.set_title("13-gram Overlap: The Pile vs Prior Work")
    ax.legend()
    ax.set_ylim(0, max(20, max(means) + 2))
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
