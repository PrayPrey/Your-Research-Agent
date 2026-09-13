"""Visualization for H-M1 calibration analysis."""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def plot_ece_vs_metrics(
    ece: np.ndarray,
    truthfulqa: np.ndarray,
    advglue: np.ndarray,
    r_tqa: float,
    p_tqa: float,
    r_adv: float,
    p_adv: float,
    output_path: Path,
):
    """Dual scatter plot: ECE vs TruthfulQA and ECE vs AdvGLUE."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # ECE vs TruthfulQA
    axes[0].scatter(ece, truthfulqa, c="#3498db", s=60, alpha=0.7)
    z = np.polyfit(ece, truthfulqa, 1)
    p = np.poly1d(z)
    x_line = np.linspace(ece.min(), ece.max(), 100)
    axes[0].plot(x_line, p(x_line), "r--", linewidth=2)
    axes[0].set_xlabel("ECE (15-bin)", fontsize=12)
    axes[0].set_ylabel("TruthfulQA MC1 Accuracy", fontsize=12)
    axes[0].set_title(f"ECE vs TruthfulQA\nr={r_tqa:.3f}, p={p_tqa:.4f}", fontsize=12)
    axes[0].grid(True, alpha=0.3)

    # ECE vs AdvGLUE
    axes[1].scatter(ece, advglue, c="#e74c3c", s=60, alpha=0.7)
    z = np.polyfit(ece, advglue, 1)
    p = np.poly1d(z)
    axes[1].plot(x_line, p(x_line), "r--", linewidth=2)
    axes[1].set_xlabel("ECE (15-bin)", fontsize=12)
    axes[1].set_ylabel("AdvGLUE Average Accuracy", fontsize=12)
    axes[1].set_title(f"ECE vs AdvGLUE\nr={r_adv:.3f}, p={p_adv:.4f}", fontsize=12)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path / "ece_vs_metrics.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_tertile_comparison(
    r_low: float,
    r_high: float,
    fisher_p: float,
    output_path: Path,
):
    """Bar chart comparing within-tertile correlations."""
    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(
        ["Low ECE\n(best calibrated)", "High ECE\n(worst calibrated)"],
        [r_low, r_high],
        color=["#2ecc71", "#e74c3c"],
        width=0.5,
    )

    ax.set_ylabel("TruthfulQA-AdvGLUE Correlation (r)", fontsize=12)
    ax.set_title(f"Tertile Moderation Test\nFisher z-test p={fisher_p:.4f}", fontsize=14)
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.set_ylim(-0.2, 1.1)
    ax.grid(True, axis="y", alpha=0.3)

    for bar, val in zip(bars, [r_low, r_high]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, f"r={val:.3f}", ha="center", fontsize=11)

    plt.tight_layout()
    plt.savefig(output_path / "tertile_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()
