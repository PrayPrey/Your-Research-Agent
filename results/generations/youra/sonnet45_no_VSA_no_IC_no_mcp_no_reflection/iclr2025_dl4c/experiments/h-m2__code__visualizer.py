"""Visualization for H-M2 results."""

import os
from typing import List
import matplotlib.pyplot as plt
from agent import FixResult


def plot_proportion_comparison(
    baseline: float,
    proposed: float,
    save_path: str
):
    """Bar chart comparing proportions."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    agents = ["Baseline\n(Sequential)", "Proposed\n(Prioritized)"]
    proportions = [baseline, proposed]
    colors = ["#e74c3c", "#2ecc71"]

    bars = ax.bar(agents, proportions, color=colors, alpha=0.8)

    ax.set_ylabel("Proportion of High-Impact Fixes", fontsize=12)
    ax.set_title("Fix-Impact Proportion Comparison", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 1.0)
    ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5)
    ax.grid(axis="y", alpha=0.3)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.3f}",
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_fix_impact_distribution(
    baseline_results: List[List[FixResult]],
    proposed_results: List[List[FixResult]],
    save_path: str
):
    """Histogram of delta_passing distribution."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Flatten deltas
    baseline_deltas = [
        fr.delta_passing
        for problem_results in baseline_results
        for fr in problem_results
    ]
    proposed_deltas = [
        fr.delta_passing
        for problem_results in proposed_results
        for fr in problem_results
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    bins = range(-1, 8)
    ax.hist(
        baseline_deltas,
        bins=bins,
        alpha=0.6,
        label="Baseline (Sequential)",
        color="#e74c3c",
        edgecolor="black"
    )
    ax.hist(
        proposed_deltas,
        bins=bins,
        alpha=0.6,
        label="Proposed (Prioritized)",
        color="#2ecc71",
        edgecolor="black"
    )

    ax.axvline(2, color="black", linestyle="--", linewidth=2, label="High-Impact Threshold")
    ax.set_xlabel("Δpassing_tests", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title("Distribution of Fix Impact", fontsize=14, fontweight="bold")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_cumulative_tests(
    baseline_results: List[List[FixResult]],
    proposed_results: List[List[FixResult]],
    save_path: str
):
    """Cumulative tests passed over iterations."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Average across problems
    max_iter = max(
        max(len(pr) for pr in baseline_results) if baseline_results else 0,
        max(len(pr) for pr in proposed_results) if proposed_results else 0
    )

    baseline_cumulative = []
    proposed_cumulative = []

    for i in range(max_iter):
        baseline_sum = sum(
            sum(fr.test_results_after) for pr in baseline_results if i < len(pr)
            for fr in [pr[i]]
        )
        baseline_count = sum(1 for pr in baseline_results if i < len(pr))
        baseline_cumulative.append(baseline_sum / baseline_count if baseline_count > 0 else 0)

        proposed_sum = sum(
            sum(fr.test_results_after) for pr in proposed_results if i < len(pr)
            for fr in [pr[i]]
        )
        proposed_count = sum(1 for pr in proposed_results if i < len(pr))
        proposed_cumulative.append(proposed_sum / proposed_count if proposed_count > 0 else 0)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        range(max_iter),
        baseline_cumulative,
        marker="o",
        label="Baseline (Sequential)",
        color="#e74c3c",
        linewidth=2
    )
    ax.plot(
        range(max_iter),
        proposed_cumulative,
        marker="s",
        label="Proposed (Prioritized)",
        color="#2ecc71",
        linewidth=2
    )

    ax.set_xlabel("Iteration", fontsize=12)
    ax.set_ylabel("Average Tests Passed", fontsize=12)
    ax.set_title("Cumulative Tests Passed Over Iterations", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_cluster_vs_impact(
    cluster_sizes: List[int],
    fix_impacts: List[int],
    save_path: str
):
    """Scatter plot of cluster size vs fix impact."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(cluster_sizes, fix_impacts, alpha=0.6, color="#3498db", s=100, edgecolor="black")

    ax.axhline(2, color="red", linestyle="--", linewidth=2, label="High-Impact Threshold")
    ax.set_xlabel("Cluster Size", fontsize=12)
    ax.set_ylabel("Fix Impact (Δpassing_tests)", fontsize=12)
    ax.set_title("Cluster Size vs Fix Impact", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
