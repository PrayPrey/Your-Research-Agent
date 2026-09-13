"""H-M1 Visualization: Zero-Reward Basin Mechanism Analysis Figures."""

import os
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from config import HM1Config


def plot_gate_metrics(metrics: Dict, config: HM1Config) -> None:
    """Bar chart: target p=0.05 vs actual Fisher's exact p-value.

    Args:
        metrics: Analysis metrics with p_value and fisher_p_threshold
        config: H-M1 configuration

    Saves to: figures/gate_metrics.png
    """
    os.makedirs(config.figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4))

    x = ["Target\n(< 0.05)", "Actual"]
    y = [metrics["fisher_p_threshold"], metrics["p_value"]]
    colors = ["steelblue", "green" if metrics["gate_pass"] else "red"]

    bars = ax.bar(x, y, color=colors, edgecolor="black", linewidth=1.5)
    ax.axhline(y=metrics["fisher_p_threshold"], color="gray", linestyle="--", linewidth=2, label="Threshold")

    ax.set_ylabel("p-value (Fisher's exact, one-sided)", fontsize=12)
    ax.set_title(f"H-M1 MUST_WORK Gate: {'PASS' if metrics['gate_pass'] else 'FAIL'}", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(max(y) * 1.5, 0.1))

    # Add value labels
    for bar, val in zip(bars, y):
        height = bar.get_height()
        ax.annotate(f"{val:.4f}" if val < 0.01 else f"{val:.3f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.legend(loc="upper right")
    plt.tight_layout()

    output_path = os.path.join(config.figures_dir, "gate_metrics.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved gate metrics figure to {output_path}")


def plot_assertion_proportion(metrics: Dict, config: HM1Config) -> None:
    """Bar chart: P(assertion|failure) for RL vs DPO.

    Args:
        metrics: Analysis metrics with rl_assertion_prop and dpo_assertion_prop
        config: H-M1 configuration

    Saves to: figures/assertion_proportion.png
    """
    os.makedirs(config.figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4))

    x = ["RL (CodeRL)", "DPO (CodeLlama)"]
    y = [metrics["rl_assertion_prop"] * 100, metrics["dpo_assertion_prop"] * 100]
    colors = ["steelblue", "coral"]

    bars = ax.bar(x, y, color=colors, edgecolor="black", linewidth=1.5)

    ax.set_ylabel("P(assertion | failure) %", fontsize=12)
    ax.set_title("Assertion Error Proportion by Model\n(H-M1: Zero-Reward Basin Mechanism)", fontsize=12)
    ax.set_ylim(0, max(max(y) * 1.5, 5))

    # Add value labels and counts
    for bar, val, model in zip(bars, y, ["rl", "dpo"]):
        height = bar.get_height()
        count_key = f"{model}_assertion_count"
        total_key = f"{model}_total_failures"
        count = metrics.get(count_key, 0)
        total = metrics.get(total_key, 0)
        ax.annotate(f"{val:.2f}%\n({count}/{total})",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=11, fontweight="bold")

    # Add direction indicator
    if metrics.get("direction_matches", False):
        ax.annotate("✓ Direction: RL > DPO",
                    xy=(0.5, 0.95), xycoords="axes fraction",
                    ha="center", fontsize=10, color="green", fontweight="bold")

    plt.tight_layout()

    output_path = os.path.join(config.figures_dir, "assertion_proportion.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved assertion proportion figure to {output_path}")


def plot_error_distribution(
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
    config: HM1Config,
) -> None:
    """Stacked bar chart: syntax/runtime/assertion breakdown by model.

    Args:
        rl_counts: Error counts for RL model
        dpo_counts: Error counts for DPO model
        config: H-M1 configuration

    Saves to: figures/error_distribution.png
    """
    os.makedirs(config.figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))

    categories = ["syntax", "runtime", "assertion"]
    x = np.arange(2)  # RL and DPO
    width = 0.6

    # Get counts for each category
    rl_vals = [rl_counts.get(cat, 0) for cat in categories]
    dpo_vals = [dpo_counts.get(cat, 0) for cat in categories]

    # Stacked bar chart
    colors = ["#ff9999", "#ffcc99", "#99ccff"]  # syntax=red-ish, runtime=orange-ish, assertion=blue-ish

    bottom_rl = 0
    bottom_dpo = 0
    for i, (cat, color) in enumerate(zip(categories, colors)):
        ax.bar(0, rl_vals[i], width, bottom=bottom_rl, label=cat.capitalize() if i == 0 else "", color=color,
               edgecolor="black" if cat == "assertion" else "none", linewidth=2 if cat == "assertion" else 0)
        ax.bar(1, dpo_vals[i], width, bottom=bottom_dpo, color=color,
               edgecolor="black" if cat == "assertion" else "none", linewidth=2 if cat == "assertion" else 0)
        bottom_rl += rl_vals[i]
        bottom_dpo += dpo_vals[i]

    # Custom legend
    legend_patches = [plt.Rectangle((0, 0), 1, 1, facecolor=c, edgecolor="none") for c in colors]
    ax.legend(legend_patches, [cat.capitalize() for cat in categories], loc="upper right")

    ax.set_ylabel("Error Count", fontsize=12)
    ax.set_title("Error Type Distribution: RL vs DPO\n(Assertion errors highlighted)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(["RL (CodeRL)", "DPO (CodeLlama)"])

    # Add total and assertion counts
    ax.annotate(f"Total: {sum(rl_vals)}\nAssertion: {rl_vals[2]}",
                xy=(0, sum(rl_vals)), xytext=(0, 10), textcoords="offset points",
                ha="center", va="bottom", fontsize=10)
    ax.annotate(f"Total: {sum(dpo_vals)}\nAssertion: {dpo_vals[2]}",
                xy=(1, sum(dpo_vals)), xytext=(0, 10), textcoords="offset points",
                ha="center", va="bottom", fontsize=10)

    plt.tight_layout()

    output_path = os.path.join(config.figures_dir, "error_distribution.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved error distribution figure to {output_path}")


def plot_contingency_heatmap(contingency: list, config: HM1Config) -> None:
    """Heatmap of 2x2 Fisher's exact contingency table.

    Args:
        contingency: 2x2 list [[rl_assert, rl_non], [dpo_assert, dpo_non]]
        config: H-M1 configuration

    Saves to: figures/contingency_table.png
    """
    os.makedirs(config.figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4))

    contingency_arr = np.array(contingency)

    sns.heatmap(
        contingency_arr,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Assertion", "Non-Assertion"],
        yticklabels=["RL (CodeRL)", "DPO (CodeLlama)"],
        ax=ax,
        cbar_kws={"label": "Count"},
        annot_kws={"fontsize": 14, "fontweight": "bold"}
    )

    ax.set_title("2x2 Contingency Table for Fisher's Exact Test", fontsize=12)
    ax.set_xlabel("Error Type", fontsize=11)
    ax.set_ylabel("Model", fontsize=11)

    plt.tight_layout()

    output_path = os.path.join(config.figures_dir, "contingency_table.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved contingency heatmap to {output_path}")


def generate_all_figures(
    metrics: Dict,
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
    config: HM1Config,
) -> None:
    """Generate and save all required figures.

    Args:
        metrics: Complete analysis metrics
        rl_counts: Error counts for RL model
        dpo_counts: Error counts for DPO model
        config: H-M1 configuration
    """
    os.makedirs(config.figures_dir, exist_ok=True)

    plot_gate_metrics(metrics, config)
    plot_assertion_proportion(metrics, config)
    plot_error_distribution(rl_counts, dpo_counts, config)
    plot_contingency_heatmap(metrics.get("contingency_table", [[0, 0], [0, 0]]), config)

    print(f"Generated all figures in {config.figures_dir}/")
