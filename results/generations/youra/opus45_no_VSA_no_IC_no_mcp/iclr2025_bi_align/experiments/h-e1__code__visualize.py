"""Visualization for H-E1 benchmark correlation experiment."""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import FIGURES_DIR, CORR_THRESHOLD


def ensure_figures_dir():
    os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_correlation_heatmap(correlations: dict, out_path: str = None):
    """Plot correlation matrix heatmap."""
    ensure_figures_dir()
    out_path = out_path or os.path.join(FIGURES_DIR, "correlation_heatmap.png")

    benchmarks = ["truthfulqa", "hhh_helpful", "hhh_harmless"]
    matrix = np.eye(3)

    for key, val in correlations.items():
        parts = key.split("_vs_")
        i = benchmarks.index(parts[0])
        j = benchmarks.index(parts[1])
        matrix[i, j] = val["r"]
        matrix[j, i] = val["r"]

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        matrix,
        annot=True,
        fmt=".3f",
        xticklabels=benchmarks,
        yticklabels=benchmarks,
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        center=0,
    )
    plt.title("Benchmark Correlation Matrix")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_gate_status(correlations: dict, threshold: float = CORR_THRESHOLD, out_path: str = None):
    """Plot gate pass/fail status."""
    ensure_figures_dir()
    out_path = out_path or os.path.join(FIGURES_DIR, "gate_status.png")

    pairs = list(correlations.keys())
    r_vals = [abs(correlations[p]["r"]) for p in pairs]
    colors = ["green" if r < threshold else "red" for r in r_vals]

    plt.figure(figsize=(10, 5))
    bars = plt.bar(pairs, r_vals, color=colors)
    plt.axhline(y=threshold, color="black", linestyle="--", label=f"Threshold ({threshold})")
    plt.ylabel("|Correlation|")
    plt.title("Gate Check: |r| < 0.5")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_score_distributions(scores: dict, out_path: str = None):
    """Plot score distributions per benchmark."""
    ensure_figures_dir()
    out_path = out_path or os.path.join(FIGURES_DIR, "score_distributions.png")

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    for ax, (name, data) in zip(axes, scores.items()):
        ax.hist(data, bins=2, edgecolor="black", alpha=0.7)
        ax.set_title(f"{name}\nmean={data.mean():.3f}")
        ax.set_xlabel("Score")
        ax.set_ylabel("Count")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")
