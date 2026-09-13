"""H-C1 visualization: loading comparison plots."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_gate_metrics(loadings: dict, threshold: float, out_path: str) -> None:
    """
    Bar chart of holdout loadings vs threshold.
    Green if >= threshold, red otherwise.
    """
    names = list(loadings.keys())
    values = [loadings[n]["loading"] for n in names]
    colors = ["#2ecc71" if v >= threshold else "#e74c3c" for v in values]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(names, values, color=colors, edgecolor="black", linewidth=1.2)
    ax.axhline(y=threshold, color="#3498db", linestyle="--", linewidth=2, label=f"Threshold ({threshold})")

    ax.set_ylabel("Loading on Frozen PC1", fontsize=12)
    ax.set_xlabel("Holdout Benchmark", fontsize=12)
    ax.set_title("H-C1: Prospective Structural Validity Test", fontsize=14, fontweight="bold")
    ax.legend(loc="upper right")

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10)

    ax.set_ylim(0, max(values) + 0.15)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_loading_comparison(h_e1_loadings: dict, holdout_loadings: dict, out_path: str) -> None:
    """Compare H-E1 original loadings vs holdout benchmark loadings."""
    fig, ax = plt.subplots(figsize=(12, 6))

    h_e1_names = list(h_e1_loadings.keys())
    h_e1_vals = list(h_e1_loadings.values())
    holdout_names = list(holdout_loadings.keys())
    holdout_vals = [holdout_loadings[n]["loading"] for n in holdout_names]

    x1 = np.arange(len(h_e1_names))
    x2 = np.arange(len(holdout_names)) + len(h_e1_names) + 1

    ax.bar(x1, h_e1_vals, color="#3498db", label="H-E1 Original", edgecolor="black")
    ax.bar(x2, holdout_vals, color="#9b59b6", label="Holdout (H-C1)", edgecolor="black")

    ax.axhline(y=0.3, color="#e74c3c", linestyle="--", linewidth=2, label="Threshold (0.3)")

    ax.set_xticks(np.concatenate([x1, x2]))
    ax.set_xticklabels(h_e1_names + holdout_names, rotation=45, ha="right")
    ax.set_ylabel("Loading on PC1", fontsize=12)
    ax.set_title("PC1 Loadings: Original vs Holdout Benchmarks", fontsize=14, fontweight="bold")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_pc1_scatter(pc1_scores: np.ndarray, holdout_df, holdout_cols: list[str], out_path: str) -> None:
    """Scatter plots of PC1 vs each holdout benchmark."""
    n_cols = len(holdout_cols)
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    axes = axes.flatten()

    for i, col in enumerate(holdout_cols):
        ax = axes[i]
        y = holdout_df[col].values
        ax.scatter(pc1_scores, y, alpha=0.3, s=10, color="#3498db")

        z = np.polyfit(pc1_scores, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(pc1_scores.min(), pc1_scores.max(), 100)
        ax.plot(x_line, p(x_line), color="#e74c3c", linewidth=2)

        r = np.corrcoef(pc1_scores, y)[0, 1]
        ax.set_title(f"{col} (r={r:.3f})", fontsize=11)
        ax.set_xlabel("PC1 Score")
        ax.set_ylabel(col)

    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    plt.suptitle("PC1 vs Holdout Benchmarks", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_loading_heatmap(all_loadings: dict, out_path: str) -> None:
    """Heatmap of all loadings sorted by value."""
    names = list(all_loadings.keys())
    values = list(all_loadings.values())
    sorted_idx = np.argsort(values)[::-1]
    names_sorted = [names[i] for i in sorted_idx]
    values_sorted = [values[i] for i in sorted_idx]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2ecc71" if v >= 0.3 else "#e74c3c" for v in values_sorted]
    bars = ax.barh(names_sorted, values_sorted, color=colors, edgecolor="black")

    ax.axvline(x=0.3, color="#3498db", linestyle="--", linewidth=2, label="Threshold")
    ax.set_xlabel("Loading on PC1", fontsize=12)
    ax.set_title("All Benchmark Loadings (Sorted)", fontsize=14, fontweight="bold")
    ax.legend()

    for bar, val in zip(bars, values_sorted):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")
