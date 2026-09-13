"""Visualization for PC1 vs BSI correlation."""

import numpy as np
import matplotlib.pyplot as plt


def scatter_with_fit(
    pc1_scores: np.ndarray,
    bsi_scores: np.ndarray,
    corr_result: dict,
    out_path: str = "outputs/pc1_vs_bsi_scatter.png"
) -> None:
    """
    Create scatter plot with regression line.

    Args:
        pc1_scores: (M,) PC1 scores
        bsi_scores: (M,) BSI scores
        corr_result: dict with rho, p_value, n
        out_path: Output path for figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(pc1_scores, bsi_scores, alpha=0.6, s=30, edgecolors='none')

    slope, intercept = np.polyfit(pc1_scores, bsi_scores, 1)
    x_line = np.linspace(pc1_scores.min(), pc1_scores.max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, 'r-', linewidth=2, label='Regression line')

    rho = corr_result["rho"]
    p_value = corr_result["p_value"]
    n = corr_result["n"]

    annotation = f"ρ = {rho:.3f}\np = {p_value:.4f}\nn = {n}"
    ax.annotate(
        annotation,
        xy=(0.05, 0.95),
        xycoords='axes fraction',
        verticalalignment='top',
        fontsize=12,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )

    ax.set_xlabel("PC1,residual", fontsize=12)
    ax.set_ylabel("Behavioral Stability Index (BSI)", fontsize=12)
    ax.set_title("H-M1: PC1 vs BSI Correlation", fontsize=14)
    ax.legend(loc='lower right')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Figure saved: {out_path}")
