"""Visualization for error distribution analysis."""

import os
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from config import ExperimentConfig
from analyze import ERROR_CATEGORIES


def plot_gate_metrics(metrics: Dict, output_path: str) -> None:
    """Bar chart: target vs actual p-value and Cramér's V. Saves PNG."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # P-value comparison
    ax1 = axes[0]
    x = ["Target\n(< 0.05)", "Actual"]
    y = [metrics["thresholds"]["chi2_p_threshold"], metrics["p_value"]]
    colors = ["blue", "green" if metrics["p_value"] < metrics["thresholds"]["chi2_p_threshold"] else "red"]
    ax1.bar(x, y, color=colors)
    ax1.axhline(y=metrics["thresholds"]["chi2_p_threshold"], color="gray", linestyle="--", label="Threshold")
    ax1.set_ylabel("p-value")
    ax1.set_title(f"Chi-square p-value\n{'PASS' if metrics['p_value'] < 0.05 else 'FAIL'}")
    ax1.set_ylim(0, max(y) * 1.2)

    # Cramér's V comparison
    ax2 = axes[1]
    x = ["Target\n(> 0.05)", "Actual"]
    y = [metrics["thresholds"]["cramers_v_threshold"], metrics["cramers_v"]]
    colors = ["blue", "green" if metrics["cramers_v"] > metrics["thresholds"]["cramers_v_threshold"] else "red"]
    ax2.bar(x, y, color=colors)
    ax2.axhline(y=metrics["thresholds"]["cramers_v_threshold"], color="gray", linestyle="--", label="Threshold")
    ax2.set_ylabel("Cramér's V")
    ax2.set_title(f"Effect Size (Cramér's V)\n{'PASS' if metrics['cramers_v'] > 0.05 else 'FAIL'}")
    ax2.set_ylim(0, max(y) * 1.2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved gate metrics figure to {output_path}")


def plot_error_distribution(metrics: Dict, output_path: str) -> None:
    """Grouped bar: P(type | failure) for RL vs DPO per error type. Saves PNG."""
    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.arange(len(ERROR_CATEGORIES))
    width = 0.35

    rl_vals = [metrics["rl_proportions"][cat] for cat in ERROR_CATEGORIES]
    dpo_vals = [metrics["dpo_proportions"][cat] for cat in ERROR_CATEGORIES]

    bars1 = ax.bar(x - width/2, rl_vals, width, label="RL (CodeRL)", color="steelblue")
    bars2 = ax.bar(x + width/2, dpo_vals, width, label="DPO (CodeLlama)", color="coral")

    ax.set_ylabel("P(error type | failure)")
    ax.set_title("Error Type Distribution: RL vs DPO")
    ax.set_xticks(x)
    ax.set_xticklabels([cat.capitalize() for cat in ERROR_CATEGORIES])
    ax.legend()

    # Add value labels on bars
    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate(f"{height:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved error distribution figure to {output_path}")


def plot_contingency_heatmap(contingency: np.ndarray, output_path: str) -> None:
    """2x3 seaborn heatmap with count annotations. Saves PNG."""
    fig, ax = plt.subplots(figsize=(8, 4))

    sns.heatmap(
        contingency,
        annot=True,
        fmt="d",
        cmap="YlOrRd",
        xticklabels=[cat.capitalize() for cat in ERROR_CATEGORIES],
        yticklabels=["RL (CodeRL)", "DPO (CodeLlama)"],
        ax=ax
    )
    ax.set_title("Error Type Contingency Table")
    ax.set_xlabel("Error Type")
    ax.set_ylabel("Model")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved contingency heatmap to {output_path}")


def plot_sample_sizes(
    rl_results: List[dict],
    dpo_results: List[dict],
    output_path: str,
) -> None:
    """Bar chart: failure counts per model (sanity check). Saves PNG."""
    fig, ax = plt.subplots(figsize=(6, 4))

    rl_pass = sum(1 for r in rl_results if r["status"] == "pass")
    rl_fail = sum(1 for r in rl_results if r["status"] == "fail")
    dpo_pass = sum(1 for r in dpo_results if r["status"] == "pass")
    dpo_fail = sum(1 for r in dpo_results if r["status"] == "fail")

    x = np.arange(2)
    width = 0.35

    pass_counts = [rl_pass, dpo_pass]
    fail_counts = [rl_fail, dpo_fail]

    bars1 = ax.bar(x - width/2, pass_counts, width, label="Pass", color="green")
    bars2 = ax.bar(x + width/2, fail_counts, width, label="Fail", color="red")

    ax.set_ylabel("Sample Count")
    ax.set_title("Pass/Fail Distribution by Model")
    ax.set_xticks(x)
    ax.set_xticklabels(["RL (CodeRL)", "DPO (CodeLlama)"])
    ax.legend()

    # Add value labels
    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate(f"{int(height)}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved sample sizes figure to {output_path}")


def generate_all_figures(
    metrics: Dict,
    contingency: np.ndarray,
    rl_results: List[dict],
    dpo_results: List[dict],
    config: ExperimentConfig,
) -> None:
    """Generate all 4 figures. Saves to config.figures_dir/."""
    os.makedirs(config.figures_dir, exist_ok=True)

    plot_gate_metrics(metrics, os.path.join(config.figures_dir, "gate_metrics.png"))
    plot_error_distribution(metrics, os.path.join(config.figures_dir, "error_distribution.png"))
    plot_contingency_heatmap(contingency, os.path.join(config.figures_dir, "contingency_heatmap.png"))
    plot_sample_sizes(rl_results, dpo_results, os.path.join(config.figures_dir, "sample_sizes.png"))

    print(f"Generated all figures in {config.figures_dir}/")
