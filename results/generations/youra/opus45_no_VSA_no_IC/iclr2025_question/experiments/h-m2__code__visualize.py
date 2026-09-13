"""Visualization for h-m2 cross-model transfer results."""

import numpy as np
import matplotlib.pyplot as plt
import os


def plot_transfer_heatmap(matrix: np.ndarray, model_names: list[str], out_path: str) -> None:
    """Plot 3x3 transfer AUROC heatmap."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0.5, vmax=1.0)

    ax.set_xticks(np.arange(len(model_names)))
    ax.set_yticks(np.arange(len(model_names)))
    ax.set_xticklabels(model_names)
    ax.set_yticklabels(model_names)
    ax.set_xlabel("Eval Model")
    ax.set_ylabel("Train Model")
    ax.set_title("Cross-Model Transfer AUROC Matrix")

    for i in range(len(model_names)):
        for j in range(len(model_names)):
            ax.text(j, i, f"{matrix[i, j]:.3f}", ha="center", va="center", color="black")

    fig.colorbar(im, ax=ax, label="AUROC")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved heatmap: {out_path}")


def plot_gap_bar(gap_stats: dict, out_path: str) -> None:
    """Plot per-pair transfer gap bar chart."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    pairs = list(gap_stats["per_pair_gaps"].keys())
    gaps = [gap_stats["per_pair_gaps"][p] for p in pairs]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(pairs, gaps, color="steelblue")

    ax.axhline(y=0.10, color="orange", linestyle="--", label="Mean threshold (0.10)")
    ax.axhline(y=0.15, color="red", linestyle="--", label="Max threshold (0.15)")

    ax.set_xlabel("Transfer Pair")
    ax.set_ylabel("AUROC Gap (vs baseline)")
    ax.set_title(f"Transfer Gaps | Mean: {gap_stats['mean_gap']:.3f} | Max: {gap_stats['max_gap']:.3f}")
    ax.legend()

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved gap bar: {out_path}")
