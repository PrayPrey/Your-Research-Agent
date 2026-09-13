"""
Visualization module for H-E1. Saves 4 PNG figures at 300 DPI.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram
from itertools import combinations


def plot_partial_corr_bar(
    rho_partial: np.ndarray,
    pvals: np.ndarray,
    dim_names: list,
    alpha: float,
    out_path: str,
) -> None:
    """Bar chart |rho_partial| for all 15 pairs, threshold line at 0.5, color by significance."""
    pairs = []
    for i, j in combinations(range(len(dim_names)), 2):
        label = f"{dim_names[i][:4]}\n{dim_names[j][:4]}"
        rho = rho_partial[i, j]
        p = pvals[i, j]
        sig = abs(rho) > 0.5 and p < alpha
        pairs.append((label, rho, sig))

    pairs.sort(key=lambda x: abs(x[1]), reverse=True)
    labels, rhos, sigs = zip(*pairs)

    colors = ["tomato" if s else "steelblue" for s in sigs]
    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(range(len(labels)), [abs(r) for r in rhos], color=colors)
    ax.axhline(0.5, color="red", linestyle="--", linewidth=1.2, label="ρ threshold = 0.5")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("|ρ_partial|")
    ax.set_title("Partial Spearman Correlations (15 pairs)\nRed = significant (Bonferroni-corrected)")
    ax.legend()
    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_heatmap_comparison(
    rho_raw: np.ndarray,
    rho_partial: np.ndarray,
    dim_names: list,
    out_path: str,
) -> None:
    """Side-by-side 6×6 heatmaps, diverging colormap."""
    short = [d[:6] for d in dim_names]
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, rho, title in zip(
        axes,
        [rho_raw, rho_partial],
        ["Raw Spearman ρ", "Partial Spearman ρ\n(controlling log-params, RLHF)"],
    ):
        sns.heatmap(
            rho,
            ax=ax,
            cmap="RdBu_r",
            vmin=-1,
            vmax=1,
            annot=True,
            fmt=".2f",
            xticklabels=short,
            yticklabels=short,
            square=True,
        )
        ax.set_title(title)
    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_dendrogram(linkage_matrix: np.ndarray, dim_names: list, out_path: str) -> None:
    """scipy dendrogram with 2-cluster color threshold."""
    fig, ax = plt.subplots(figsize=(8, 5))
    # Color threshold set to split at 2 clusters
    color_threshold = 0.7 * max(linkage_matrix[:, 2])
    dendrogram(
        linkage_matrix,
        labels=dim_names,
        ax=ax,
        color_threshold=color_threshold,
        above_threshold_color="grey",
    )
    ax.axhline(color_threshold, linestyle="--", color="red", linewidth=1, label="2-cluster threshold")
    ax.set_title("Hierarchical Clustering Dendrogram\n(average linkage, distance = 1 − |ρ_partial|)")
    ax.set_xlabel("Dimension")
    ax.set_ylabel("Distance")
    ax.legend()
    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_scatter_confound(
    scores_df: pd.DataFrame,
    residuals_df: pd.DataFrame,
    dim_pair: tuple,
    out_path: str,
) -> None:
    """Before/after residualization scatter for top pair, colored by is_RLHF."""
    d1, d2 = dim_pair
    is_rlhf = scores_df["is_RLHF"].values if "is_RLHF" in scores_df.columns else np.zeros(len(scores_df))
    colors = ["tomato" if r else "steelblue" for r in is_rlhf]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Raw scores
    axes[0].scatter(scores_df[d1], scores_df[d2], c=colors, s=60, edgecolors="k", linewidths=0.5)
    axes[0].set_xlabel(d1)
    axes[0].set_ylabel(d2)
    axes[0].set_title(f"Raw scores\n{d1} vs {d2}")

    # Residuals
    axes[1].scatter(residuals_df[d1], residuals_df[d2], c=colors, s=60, edgecolors="k", linewidths=0.5)
    axes[1].set_xlabel(f"{d1} residual")
    axes[1].set_ylabel(f"{d2} residual")
    axes[1].set_title(f"After OLS residualization\n{d1} vs {d2}")

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="tomato", markersize=8, label="RLHF"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="steelblue", markersize=8, label="Base"),
    ]
    axes[1].legend(handles=legend_elements)

    plt.suptitle("Confound Effect: Before vs After OLS Residualization")
    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
