"""Visualization for H-M3: Multi-granularity error taxonomy plots."""

import os
from collections import Counter
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

from config import ExperimentConfig, COARSE_CATEGORIES, LLMFIX_TAXONOMY


def plot_gate_metrics(metrics: dict, config: ExperimentConfig) -> None:
    """Plot Cramer's V at coarse vs fine granularity with threshold lines.

    Args:
        metrics: Analysis metrics dict
        config: Experiment configuration
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    v_coarse = metrics["coarse"]["cramers_v"]
    v_fine = metrics["fine"]["cramers_v"]
    gate_pass = metrics["gate_result"]["gate_pass"]

    x = [0, 1]
    heights = [v_coarse, v_fine]
    labels = ["Coarse (3-tier)", "Fine (19-cause)"]
    colors = ["#2ecc71" if h > config.cramers_v_threshold_fine else "#e74c3c" for h in heights]

    bars = ax.bar(x, heights, color=colors, alpha=0.8, width=0.6)

    # Threshold lines
    ax.axhline(y=config.cramers_v_threshold_fine, color="red", linestyle="--",
               linewidth=2, label=f"Fine Threshold (V={config.cramers_v_threshold_fine})")
    ax.axhline(y=config.cramers_v_threshold_coarse, color="orange", linestyle=":",
               linewidth=2, label=f"Coarse Threshold (V={config.cramers_v_threshold_coarse})")

    # Labels
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylabel("Cramer's V", fontsize=12)
    ax.set_title(f"H-M3 Gate Metrics: Cramer's V Comparison\n(Gate: {'PASS' if gate_pass else 'FAIL'})", fontsize=14)
    ax.legend(loc="upper right")

    # Value annotations
    for i, (bar, val) in enumerate(zip(bars, heights)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{val:.4f}", ha="center", va="bottom", fontsize=11)

    ax.set_ylim(0, max(heights) * 1.2)

    os.makedirs(config.figures_dir, exist_ok=True)
    fig_path = os.path.join(config.figures_dir, "gate_metrics.png")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()
    print(f"Saved gate metrics figure to {fig_path}")


def plot_error_heatmap(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    cause_labels: List[str],
    config: ExperimentConfig,
) -> None:
    """Plot 2xK heatmap showing error distribution by fine cause.

    Args:
        rl_classified: RL failures with classification
        dpo_classified: DPO failures with classification
        cause_labels: Fine-grained cause labels
        config: Experiment configuration
    """
    # Count fine causes
    rl_counts = Counter(r["fine_cause"] for r in rl_classified)
    dpo_counts = Counter(r["fine_cause"] for r in dpo_classified)

    # Build matrix (proportions within each model)
    rl_total = len(rl_classified) if rl_classified else 1
    dpo_total = len(dpo_classified) if dpo_classified else 1

    # Use only causes that appear
    active_causes = [c for c in cause_labels if rl_counts.get(c, 0) + dpo_counts.get(c, 0) > 0]

    if not active_causes:
        print("No active causes for heatmap")
        return

    matrix = np.array([
        [rl_counts.get(c, 0) / rl_total for c in active_causes],
        [dpo_counts.get(c, 0) / dpo_total for c in active_causes],
    ])

    # Counts for annotation
    count_matrix = np.array([
        [rl_counts.get(c, 0) for c in active_causes],
        [dpo_counts.get(c, 0) for c in active_causes],
    ])

    # Create annotations with both proportion and count
    annot = np.array([
        [f"{matrix[i, j]:.2%}\n({int(count_matrix[i, j])})"
         for j in range(len(active_causes))]
        for i in range(2)
    ])

    fig, ax = plt.subplots(figsize=(max(12, len(active_causes) * 0.8), 5))

    sns.heatmap(matrix, annot=annot, fmt="", cmap="YlOrRd",
                xticklabels=active_causes, yticklabels=["RL", "DPO"],
                ax=ax, cbar_kws={"label": "Proportion"})

    ax.set_title("H-M3: Error Distribution Heatmap (Fine-Grained)", fontsize=14)
    ax.set_xlabel("Fine-Grained Error Cause", fontsize=12)
    ax.set_ylabel("Model", fontsize=12)

    plt.xticks(rotation=45, ha="right")

    os.makedirs(config.figures_dir, exist_ok=True)
    fig_path = os.path.join(config.figures_dir, "error_heatmap.png")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()
    print(f"Saved error heatmap to {fig_path}")


def plot_cramers_v_persistence(metrics: dict, config: ExperimentConfig) -> None:
    """Plot Cramer's V values showing effect persistence across granularity.

    Args:
        metrics: Analysis metrics dict
        config: Experiment configuration
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    granularities = ["3-tier (Coarse)", "19-cause (Fine)"]
    v_values = [metrics["coarse"]["cramers_v"], metrics["fine"]["cramers_v"]]
    p_values = [metrics["coarse"]["p_value"], metrics["fine"]["p_value"]]

    x = np.arange(len(granularities))
    width = 0.6

    colors = ["#3498db", "#9b59b6"]
    bars = ax.bar(x, v_values, width, color=colors, alpha=0.8)

    # Threshold line
    ax.axhline(y=config.cramers_v_threshold_fine, color="red", linestyle="--",
               linewidth=2, label=f"Gate Threshold (V={config.cramers_v_threshold_fine})")

    # Annotations with p-value
    for i, (bar, v, p) in enumerate(zip(bars, v_values, p_values)):
        sig = "*" if p < 0.05 else ""
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"V={v:.4f}{sig}\np={p:.2e}", ha="center", va="bottom", fontsize=10)

    ax.set_xticks(x)
    ax.set_xticklabels(granularities, fontsize=12)
    ax.set_ylabel("Cramer's V", fontsize=12)
    ax.set_title("H-M3: Effect Persistence Across Taxonomy Granularity", fontsize=14)
    ax.legend(loc="upper right")
    ax.set_ylim(0, max(v_values) * 1.3)

    os.makedirs(config.figures_dir, exist_ok=True)
    fig_path = os.path.join(config.figures_dir, "cramers_v_persistence.png")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()
    print(f"Saved Cramer's V persistence figure to {fig_path}")


def plot_error_proportions(metrics: dict, config: ExperimentConfig) -> None:
    """Plot grouped bar chart comparing RL vs DPO error proportions.

    Args:
        metrics: Analysis metrics dict
        config: Experiment configuration
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    rl_props = metrics["descriptive"]["rl"]["coarse_props"]
    dpo_props = metrics["descriptive"]["dpo"]["coarse_props"]

    categories = COARSE_CATEGORIES + ["syntax+runtime"]
    rl_values = [rl_props.get(c, 0) for c in COARSE_CATEGORIES]
    rl_values.append(rl_props.get("syntax", 0) + rl_props.get("runtime", 0))

    dpo_values = [dpo_props.get(c, 0) for c in COARSE_CATEGORIES]
    dpo_values.append(dpo_props.get("syntax", 0) + dpo_props.get("runtime", 0))

    x = np.arange(len(categories))
    width = 0.35

    bars_rl = ax.bar(x - width/2, rl_values, width, label="RL", color="#3498db", alpha=0.8)
    bars_dpo = ax.bar(x + width/2, dpo_values, width, label="DPO", color="#e74c3c", alpha=0.8)

    # Annotations
    for bars in [bars_rl, bars_dpo]:
        for bar in bars:
            height = bar.get_height()
            if height > 0.01:
                ax.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                        f"{height:.1%}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylabel("Proportion of Failures", fontsize=12)
    ax.set_title("H-M3: Error Type Proportions by Model", fontsize=14)
    ax.legend()
    ax.set_ylim(0, 1.1)

    # Direction indicator
    direction = metrics["direction"]["direction_satisfied"]
    dir_text = "DPO > RL" if direction else "RL > DPO"
    ax.annotate(f"Syntax+Runtime: {dir_text}",
                xy=(3, max(rl_values[-1], dpo_values[-1]) + 0.1),
                fontsize=11, ha="center",
                color="green" if direction else "red")

    os.makedirs(config.figures_dir, exist_ok=True)
    fig_path = os.path.join(config.figures_dir, "error_proportions.png")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()
    print(f"Saved error proportions figure to {fig_path}")


def plot_finegrained_distribution(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    config: ExperimentConfig,
) -> None:
    """Plot stacked bar chart showing 19-cause distribution grouped by coarse category.

    Args:
        rl_classified: RL failures with classification
        dpo_classified: DPO failures with classification
        config: Experiment configuration
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for idx, (coarse_cat, fine_causes) in enumerate(LLMFIX_TAXONOMY.items()):
        ax = axes[idx]

        # Filter by coarse category
        rl_filtered = [r for r in rl_classified if r["coarse_category"] == coarse_cat]
        dpo_filtered = [r for r in dpo_classified if r["coarse_category"] == coarse_cat]

        rl_counts = Counter(r["fine_cause"] for r in rl_filtered)
        dpo_counts = Counter(r["fine_cause"] for r in dpo_filtered)

        # Proportions
        rl_total = len(rl_filtered) if rl_filtered else 1
        dpo_total = len(dpo_filtered) if dpo_filtered else 1

        rl_props = [rl_counts.get(c, 0) / rl_total for c in fine_causes]
        dpo_props = [dpo_counts.get(c, 0) / dpo_total for c in fine_causes]

        x = np.arange(len(fine_causes))
        width = 0.35

        ax.bar(x - width/2, rl_props, width, label="RL", color="#3498db", alpha=0.8)
        ax.bar(x + width/2, dpo_props, width, label="DPO", color="#e74c3c", alpha=0.8)

        ax.set_xticks(x)
        ax.set_xticklabels([c.replace("_", "\n") for c in fine_causes], fontsize=8, rotation=45, ha="right")
        ax.set_ylabel("Proportion" if idx == 0 else "")
        ax.set_title(f"{coarse_cat.capitalize()} Errors\n(RL: {len(rl_filtered)}, DPO: {len(dpo_filtered)})")
        ax.legend(loc="upper right", fontsize=8)
        ax.set_ylim(0, 1.05)

    plt.suptitle("H-M3: Fine-Grained Error Distribution by Coarse Category", fontsize=14)

    os.makedirs(config.figures_dir, exist_ok=True)
    fig_path = os.path.join(config.figures_dir, "finegrained_distribution.png")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()
    print(f"Saved fine-grained distribution figure to {fig_path}")


def generate_all_figures(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    metrics: dict,
    cause_labels: List[str],
    config: ExperimentConfig,
) -> None:
    """Generate all visualization figures.

    Args:
        rl_classified: RL failures with classification
        dpo_classified: DPO failures with classification
        metrics: Analysis metrics dict
        cause_labels: Fine-grained cause labels
        config: Experiment configuration
    """
    print("\n=== Generating Figures ===")

    # 1. Gate metrics (mandatory P0 figure)
    plot_gate_metrics(metrics, config)

    # 2. Error heatmap
    plot_error_heatmap(rl_classified, dpo_classified, cause_labels, config)

    # 3. Cramer's V persistence
    plot_cramers_v_persistence(metrics, config)

    # 4. Error proportions
    plot_error_proportions(metrics, config)

    # 5. Fine-grained distribution
    plot_finegrained_distribution(rl_classified, dpo_classified, config)

    print("=== All figures generated ===\n")
