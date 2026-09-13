"""Visualization generation for experiment results."""

from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path


def plot_gate_metrics(mean_slope: float, target_slope: float, output_path: str):
    """
    Required figure: Gate metrics comparison.

    Args:
        mean_slope: Actual mean slope from experiment
        target_slope: Target slope (< 0 for h-e1)
        output_path: Output file path
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    metrics = ["Reformulation Slope"]
    actual = [mean_slope]
    target = [target_slope]

    x = np.arange(len(metrics))
    width = 0.35

    ax.bar(x - width/2, actual, width, label="Actual", color="#2ecc71")
    ax.bar(x + width/2, target, width, label="Target", color="#e74c3c")

    ax.set_ylabel("Slope Coefficient")
    ax.set_title("Gate Metrics: Target vs Actual")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.axhline(y=0, color="black", linestyle="--", linewidth=0.5)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_reformulation_over_turns(slopes_by_turn: List[float], output_path: str):
    """
    Recommended: Reformulation rate over turns.

    Args:
        slopes_by_turn: Average reformulation rate per turn
        output_path: Output file path
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    turns = np.arange(len(slopes_by_turn))
    ax.plot(turns, slopes_by_turn, marker="o", linewidth=2, markersize=6)

    ax.set_xlabel("Turn Index")
    ax.set_ylabel("Reformulation Rate")
    ax.set_title("Reformulation Rate Over Conversation Turns")
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_slope_distribution(slopes: List[float], output_path: str):
    """
    Recommended: Slope distribution histogram.

    Args:
        slopes: List of slope values
        output_path: Output file path
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(slopes, bins=50, edgecolor="black", alpha=0.7)
    ax.axvline(x=0, color="red", linestyle="--", linewidth=2, label="Baseline (slope=0)")
    ax.axvline(x=np.mean(slopes), color="green", linestyle="--", linewidth=2, label=f"Mean={np.mean(slopes):.4f}")

    ax.set_xlabel("Slope Coefficient")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of Reformulation Slopes")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_diversity_scatter(query_diversity: List[float], response_diversity: List[float], output_path: str):
    """
    Recommended: Query vs response diversity scatter.

    Args:
        query_diversity: List of query diversity scores
        response_diversity: List of response diversity scores
        output_path: Output file path
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    ax.scatter(query_diversity, response_diversity, alpha=0.5, s=20)

    # Compute correlation
    correlation = np.corrcoef(query_diversity, response_diversity)[0, 1]

    ax.set_xlabel("Query Diversity (distinct-1)")
    ax.set_ylabel("Response Diversity (distinct-1)")
    ax.set_title(f"Query vs Response Diversity (r={correlation:.3f})")
    ax.grid(alpha=0.3)

    # Add trend line
    z = np.polyfit(query_diversity, response_diversity, 1)
    p = np.poly1d(z)
    ax.plot(query_diversity, p(query_diversity), "r--", linewidth=2, label="Trend")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def save_all_figures(
    slopes: List[float],
    query_diversity: List[float],
    response_diversity: List[float],
    figures_dir: str
):
    """
    Generate and save all figures.

    Args:
        slopes: List of reformulation slopes
        query_diversity: List of query diversity scores
        response_diversity: List of response diversity scores
        figures_dir: Output directory
    """
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    mean_slope = np.mean(slopes)
    target_slope = 0.0  # Target: negative slope

    print("\nGenerating figures...")

    # Required figure
    plot_gate_metrics(
        mean_slope,
        target_slope,
        f"{figures_dir}/gate_metrics.png"
    )
    print("  - gate_metrics.png")

    # Recommended figures
    plot_slope_distribution(slopes, f"{figures_dir}/slope_distribution.png")
    print("  - slope_distribution.png")

    plot_diversity_scatter(
        query_diversity,
        response_diversity,
        f"{figures_dir}/diversity_scatter.png"
    )
    print("  - diversity_scatter.png")

    print("Figures saved successfully.")
