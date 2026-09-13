import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

FIGURE_COLORS = {
    "primary": "#4C72B0",
    "secondary": "#DD8452",
    "threshold_line": "#DD8452",
}
THRESHOLD_LINESTYLE = "--"
THRESHOLD_LINEWIDTH = 2.0
CDF_THRESHOLD_VALUE = 4  # N-1 = 5-1


def plot_aggregation_rate(
    aggregation_rate: float,
    ci_lower: float,
    ci_upper: float,
    gate_threshold: float,
    output_path: str,
) -> None:
    """Bar chart: aggregation rate vs 50% threshold with bootstrap CI error bar."""
    fig, ax = plt.subplots(figsize=(7, 5))
    yerr_lower = aggregation_rate - ci_lower
    yerr_upper = ci_upper - aggregation_rate
    ax.bar(
        ["Aggregation Rate"],
        [aggregation_rate],
        color=FIGURE_COLORS["primary"],
        yerr=[[yerr_lower], [yerr_upper]],
        capsize=8,
        width=0.4,
    )
    ax.axhline(
        y=gate_threshold,
        color=FIGURE_COLORS["threshold_line"],
        linestyle=THRESHOLD_LINESTYLE,
        linewidth=THRESHOLD_LINEWIDTH,
        label=f"Gate threshold ({gate_threshold:.0%})",
    )
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Metric")
    ax.set_ylabel("Rate")
    ax.set_title("Aggregation Rate vs Gate Threshold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_cluster_count_dist(
    cluster_counts: np.ndarray,
    output_path: str,
) -> None:
    """Histogram of cluster_count values 1–5."""
    fig, ax = plt.subplots(figsize=(8, 5))
    bins = np.arange(0.5, 6.5, 1)
    ax.hist(cluster_counts, bins=bins, color=FIGURE_COLORS["primary"], edgecolor="white")
    ax.set_xlabel("Cluster Count")
    ax.set_ylabel("Frequency")
    ax.set_title("Cluster Count Distribution (N=2000)")
    ax.set_xticks(range(1, 6))
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_cluster_count_by_label(
    cluster_counts: np.ndarray,
    labels: np.ndarray,
    output_path: str,
) -> None:
    """Box plot of cluster_count for hallucinated (1) vs factual (0)."""
    fig, ax = plt.subplots(figsize=(7, 5))
    factual = cluster_counts[labels == 0]
    hallucinated = cluster_counts[labels == 1]
    bp = ax.boxplot(
        [factual, hallucinated],
        labels=["0 (Factual)", "1 (Hallucinated)"],
        patch_artist=True,
    )
    colors = [FIGURE_COLORS["primary"], FIGURE_COLORS["secondary"]]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_xlabel("Hallucination Label (0=Factual, 1=Hallucinated)")
    ax.set_ylabel("Cluster Count")
    ax.set_title("Cluster Count by Hallucination Label")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_cluster_count_cdf(
    cluster_counts: np.ndarray,
    threshold: int,
    output_path: str,
) -> None:
    """CDF of cluster_counts with vertical dashed line at threshold (N-1=4)."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sorted_counts = np.sort(cluster_counts)
    cdf = np.arange(1, len(sorted_counts) + 1) / len(sorted_counts)
    ax.plot(sorted_counts, cdf, color=FIGURE_COLORS["primary"], linewidth=2)
    ax.axvline(
        x=threshold,
        color=FIGURE_COLORS["threshold_line"],
        linestyle=THRESHOLD_LINESTYLE,
        linewidth=THRESHOLD_LINEWIDTH,
        label=f"Threshold x={threshold}",
    )
    ax.set_xlabel("Cluster Count")
    ax.set_ylabel("CDF")
    ax.set_title(f"CDF of Cluster Counts (threshold={threshold})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_aggregation_by_type(
    type_rates: Optional[Dict[str, float]],
    output_path: str,
) -> None:
    """Bar chart of aggregation rate by question type. Skipped if type_rates is None."""
    if type_rates is None:
        return
    fig, ax = plt.subplots(figsize=(9, 5))
    types = list(type_rates.keys())
    rates = [type_rates[t] for t in types]
    ax.bar(types, rates, color=FIGURE_COLORS["primary"])
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Question Type")
    ax.set_ylabel("Aggregation Rate")
    ax.set_title("Aggregation Rate by Question Type")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
