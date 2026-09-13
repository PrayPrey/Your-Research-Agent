"""Visualization for AUROC comparison."""

import matplotlib.pyplot as plt
import numpy as np
import os


def plot_auroc_comparison(results: dict, out_path: str) -> None:
    """Bar chart: SEP vs SE AUROC per model family."""
    models = list(results.keys())
    sep_aurocs = [results[m]["auroc_sep"] for m in models]
    se_aurocs = [results[m]["auroc_se"] for m in models]

    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, sep_aurocs, width, label="SEP (Probe)", color="#2196F3")
    bars2 = ax.bar(x + width/2, se_aurocs, width, label="SE (Multi-sample)", color="#FF9800")

    ax.set_xlabel("Model Family")
    ax.set_ylabel("AUROC")
    ax.set_title("SEP vs Multi-sample SE: AUROC Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.set_ylim(0, 1)
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)

    for bar, val in zip(bars1, sep_aurocs):
        ax.annotate(f"{val:.3f}", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    ha="center", va="bottom", fontsize=9)
    for bar, val in zip(bars2, se_aurocs):
        ax.annotate(f"{val:.3f}", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    ha="center", va="bottom", fontsize=9)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
