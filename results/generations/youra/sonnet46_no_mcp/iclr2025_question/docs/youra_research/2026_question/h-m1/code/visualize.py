import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict, Any, List


def plot_scatter_te_vs_se(
    te: np.ndarray,
    se: np.ndarray,
    r_obs: float,
    save_path: str,
) -> None:
    """Scatter plot with identity line (y=x) and Pearson r annotation."""
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.scatter(te, se, alpha=0.3, s=5, color="steelblue", rasterized=True)

    # Identity line y=x
    lims = [
        min(ax.get_xlim()[0], ax.get_ylim()[0]),
        max(ax.get_xlim()[1], ax.get_ylim()[1]),
    ]
    ax.plot(lims, lims, color="gray", linestyle="--", linewidth=1.5, label="y=x")
    ax.set_xlim(lims)
    ax.set_ylim(lims)

    ax.set_xlabel("Token Entropy (mean)", fontsize=12)
    ax.set_ylabel("Semantic Entropy", fontsize=12)
    ax.set_title(f"Token Entropy vs Semantic Entropy\nPearson r = {r_obs:.4f}", fontsize=13)
    ax.legend(fontsize=10)
    ax.text(
        0.05, 0.95, f"r = {r_obs:.4f}",
        transform=ax.transAxes, fontsize=12,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, format="png")
    plt.close(fig)


def plot_cluster_count_dist(cluster_counts: List[int], save_path: str) -> None:
    """Histogram of NLI cluster counts (1-5) across examples."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    bins = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
    ax.hist(cluster_counts, bins=bins, color="steelblue", edgecolor="white", rwidth=0.8)
    ax.set_xlabel("Cluster Count", fontsize=12)
    ax.set_ylabel("Number of Examples", fontsize=12)
    ax.set_title("NLI Cluster Count Distribution", fontsize=13)
    ax.set_xticks([1, 2, 3, 4, 5])
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, format="png")
    plt.close(fig)


def plot_divergence_dist(divergence: np.ndarray, threshold: float, save_path: str) -> None:
    """Histogram/KDE of |TE-SE| with threshold line."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    ax.hist(divergence, bins=50, color="steelblue", edgecolor="white", alpha=0.75, density=True)
    ax.axvline(threshold, color="red", linestyle="--", linewidth=2,
               label=f"High-divergence threshold = {threshold:.4f}")
    ax.set_xlabel("|Token Entropy - Semantic Entropy|", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.set_title("Pointwise Divergence Distribution", fontsize=13)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, format="png")
    plt.close(fig)


def plot_ttr_vs_divergence(
    ttr_values: np.ndarray,
    divergence: np.ndarray,
    high_div_indices: np.ndarray,
    save_path: str,
) -> None:
    """Scatter plot of TTR vs |TE-SE| with high-divergence highlighted."""
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    mask = np.ones(len(ttr_values), dtype=bool)
    mask[high_div_indices] = False

    ax.scatter(divergence[mask], ttr_values[mask], alpha=0.4, s=5,
               color="steelblue", label="Low divergence")
    ax.scatter(divergence[high_div_indices], ttr_values[high_div_indices],
               alpha=0.6, s=10, color="red", label="High divergence")

    ax.set_xlabel("|Token Entropy - Semantic Entropy|", fontsize=12)
    ax.set_ylabel("Type-Token Ratio (TTR)", fontsize=12)
    ax.set_title("Lexical Diversity vs Pointwise Divergence", fontsize=13)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, format="png")
    plt.close(fig)


def plot_bootstrap_ci(
    r_boot: List[float],
    r_obs: float,
    ci_lower: float,
    ci_upper: float,
    gate_threshold: float,
    save_path: str,
) -> None:
    """CDF of bootstrap Pearson r distribution with 95% CI bounds and gate threshold."""
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    sorted_r = np.sort(r_boot)
    cdf = np.arange(1, len(sorted_r) + 1) / len(sorted_r)
    ax.plot(sorted_r, cdf, color="steelblue", linewidth=2, label="Bootstrap r CDF")

    ax.axvline(r_obs, color="black", linestyle="-", linewidth=2, label=f"r_obs = {r_obs:.4f}")
    ax.axvline(ci_lower, color="green", linestyle="--", linewidth=1.5,
               label=f"95% CI lower = {ci_lower:.4f}")
    ax.axvline(ci_upper, color="green", linestyle="--", linewidth=1.5,
               label=f"95% CI upper = {ci_upper:.4f}")
    ax.axvline(gate_threshold, color="orange", linestyle="--", linewidth=2,
               label=f"Gate threshold = {gate_threshold}")

    ax.set_xlabel("Pearson r", fontsize=12)
    ax.set_ylabel("Cumulative Probability", fontsize=12)
    ax.set_title("Bootstrap Distribution of Pearson r\nwith 95% CI and Gate Threshold", fontsize=13)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, format="png")
    plt.close(fig)
