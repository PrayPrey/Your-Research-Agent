"""Visualization: 4 required figures for H-E1."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from config import PEARSON_R_THRESHOLD, PARTIAL_R2_THRESHOLD, FIGURES_DIR


def _ensure_dir(out_dir: str) -> None:
    Path(out_dir).mkdir(parents=True, exist_ok=True)


def plot_gate_metrics(pearson_r: float, partial_r2: float, out_dir: str = FIGURES_DIR) -> None:
    """Bar chart: |r| vs 0.7 threshold, partial R² vs 0.02 threshold."""
    _ensure_dir(out_dir)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    abs_r = abs(pearson_r)
    axes[0].bar(["Pearson |r|", "Threshold"], [abs_r, PEARSON_R_THRESHOLD],
                color=["steelblue", "coral"])
    axes[0].set_title("Pearson |r|(SE_N5, min_logprob)")
    axes[0].set_ylabel("|r|")
    axes[0].axhline(PEARSON_R_THRESHOLD, color="red", linestyle="--", alpha=0.5)
    axes[0].text(0, abs_r + 0.01, f"{abs_r:.3f}", ha="center")

    axes[1].bar(["Partial R²(SE)", "Threshold"], [partial_r2, PARTIAL_R2_THRESHOLD],
                color=["steelblue", "coral"])
    axes[1].set_title("McFadden Partial R²(SE) in Conditional LR")
    axes[1].set_ylabel("Partial R²")
    axes[1].axhline(PARTIAL_R2_THRESHOLD, color="red", linestyle="--", alpha=0.5)
    axes[1].text(0, partial_r2 + 0.001, f"{partial_r2:.4f}", ha="center")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gate_metrics.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_dir}/gate_metrics.png")


def plot_scatter(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
    correctness: np.ndarray,
    out_dir: str = FIGURES_DIR,
) -> None:
    """Scatter: SE_N5 vs min_logprob, colored by correctness."""
    _ensure_dir(out_dir)
    fig, ax = plt.subplots(figsize=(8, 6))

    colors = ["#d62728" if c == 0 else "#2ca02c" for c in correctness]
    ax.scatter(se_scores, min_logprob_scores, c=colors, alpha=0.3, s=10)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#d62728", label="Incorrect"),
        Patch(facecolor="#2ca02c", label="Correct"),
    ]
    ax.legend(handles=legend_elements)
    ax.set_xlabel("SE_N5 (Semantic Entropy)")
    ax.set_ylabel("min_logprob (Greedy Token Log-Prob)")
    ax.set_title(f"SE_N5 vs min_logprob (n={len(se_scores)}, colored by LM-judge correctness)")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "scatter_se_vs_minlogprob.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_dir}/scatter_se_vs_minlogprob.png")


def plot_correlation_heatmap(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
    response_lengths: np.ndarray,
    correctness: np.ndarray,
    out_dir: str = FIGURES_DIR,
) -> None:
    """Seaborn heatmap: [SE_N5, min_logprob, response_length, correctness]."""
    import pandas as pd
    _ensure_dir(out_dir)

    df = pd.DataFrame({
        "SE_N5": se_scores,
        "min_logprob": min_logprob_scores,
        "response_length": response_lengths,
        "correctness": correctness.astype(float),
    })
    corr = df.corr()

    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(corr, annot=True, fmt=".3f", cmap="coolwarm", center=0,
                square=True, ax=ax, vmin=-1, vmax=1)
    ax.set_title("Correlation Matrix: SE_N5, min_logprob, response_length, correctness")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "correlation_heatmap.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_dir}/correlation_heatmap.png")


def plot_lr_coefficients(stats: dict, out_dir: str = FIGURES_DIR) -> None:
    """Bar chart of β coefficients for full LR model."""
    _ensure_dir(out_dir)
    coefs = stats.get("coefs_full", [])
    if not coefs:
        print("  Skipping LR coefficient plot: no coefs found")
        return

    labels = ["β_min_logprob", "β_SE", "β_L", "β_SE×min_lp"]
    coefs = coefs[:len(labels)]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#2ca02c" if c > 0 else "#d62728" for c in coefs]
    bars = ax.bar(labels[:len(coefs)], coefs, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Coefficient value")
    ax.set_title("Full Model LR Coefficients: logit(correct) ~ min_logprob + SE + L + SE×min_lp")

    for bar, val in zip(bars, coefs):
        ax.text(bar.get_x() + bar.get_width() / 2, val + (0.002 if val >= 0 else -0.005),
                f"{val:.4f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "lr_coefficients.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_dir}/lr_coefficients.png")


def save_all(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
    response_lengths: np.ndarray,
    correctness: np.ndarray,
    stats: dict,
    out_dir: str = FIGURES_DIR,
) -> None:
    """Generate all 4 figures."""
    print("Generating figures...")
    plot_gate_metrics(stats["pearson_r"], stats["partial_r2_se"], out_dir)
    plot_scatter(se_scores, min_logprob_scores, correctness, out_dir)
    plot_correlation_heatmap(se_scores, min_logprob_scores, response_lengths, correctness, out_dir)
    plot_lr_coefficients(stats, out_dir)
    print(f"All figures saved to {out_dir}")
