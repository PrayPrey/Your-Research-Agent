"""Visualize: Generate figures for H-M4 layer-wise analysis."""

import os
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import config
from adapter_loader import AdapterRecord
from stats_analysis import CohensDResult


def setup_style():
    """Configure matplotlib/seaborn style."""
    sns.set_style(config.VIZ_CONFIG["style"])
    sns.set_context("paper", font_scale=config.VIZ_CONFIG["font_scale"])


def plot_cohens_d_by_layer_type(
    results: list[CohensDResult],
    output_path: str,
    threshold: float = 0.8,
) -> None:
    """
    Bar chart showing Cohen's d per layer type with CI error bars.

    Args:
        results: List of CohensDResult from analyze_all_layer_types
        output_path: Path to save figure
        threshold: Threshold line value (default 0.8)
    """
    setup_style()

    fig, ax = plt.subplots(figsize=config.VIZ_CONFIG["bar_chart_figsize"])

    # Sort by layer type order (attention then MLP)
    order = config.ALL_LAYER_TYPES
    sorted_results = sorted(results, key=lambda r: order.index(r["layer_type"]))

    layer_types = [r["layer_type"] for r in sorted_results]
    d_values = [r["cohens_d"] for r in sorted_results]
    ci_lows = [r["ci_low"] for r in sorted_results]
    ci_highs = [r["ci_high"] for r in sorted_results]

    # Error bars
    errors = [
        [d - ci_low for d, ci_low in zip(d_values, ci_lows)],
        [ci_high - d for d, ci_high in zip(d_values, ci_highs)]
    ]

    # Colors: attention vs MLP
    colors = [
        config.VIZ_CONFIG["attention_color"] if lt in config.ATTENTION_LAYER_TYPES
        else config.VIZ_CONFIG["mlp_color"]
        for lt in layer_types
    ]

    # Bar plot
    bars = ax.bar(layer_types, d_values, color=colors, edgecolor="black", linewidth=0.5)

    # Add error bars
    ax.errorbar(
        layer_types, d_values,
        yerr=errors,
        fmt='none',
        ecolor='black',
        capsize=3,
        capthick=1,
    )

    # Threshold line
    ax.axhline(
        y=threshold,
        color=config.VIZ_CONFIG["threshold_line_color"],
        linestyle='--',
        linewidth=2,
        label=f"Threshold (d = {threshold})"
    )

    # Labels and title
    ax.set_xlabel("Layer Type", fontsize=12)
    ax.set_ylabel("Cohen's d (within vs between)", fontsize=12)
    ax.set_title("Layer-wise Cohen's d: Task Category Clustering", fontsize=14)

    # Rotate x labels for readability
    plt.xticks(rotation=45, ha="right")

    # Legend for colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=config.VIZ_CONFIG["attention_color"], label="Attention"),
        Patch(facecolor=config.VIZ_CONFIG["mlp_color"], label="MLP"),
        plt.Line2D([0], [0], color=config.VIZ_CONFIG["threshold_line_color"],
                   linestyle='--', label=f"Threshold (d={threshold})")
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    # Add value annotations
    for bar, d_val in zip(bars, d_values):
        ax.annotate(
            f"{d_val:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 3),
            textcoords="offset points",
            ha='center',
            va='bottom',
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=config.VIZ_CONFIG["dpi"], format=config.VIZ_CONFIG["format"])
    plt.close()
    print(f"Saved: {output_path}")


def plot_layer_type_ranking(
    results: list[CohensDResult],
    output_path: str,
) -> None:
    """
    Horizontal bar chart sorted by Cohen's d descending.

    Args:
        results: List of CohensDResult (already sorted by cohens_d)
        output_path: Path to save figure
    """
    setup_style()

    fig, ax = plt.subplots(figsize=config.VIZ_CONFIG["ranking_figsize"])

    # Already sorted by Cohen's d descending
    layer_types = [r["layer_type"] for r in results]
    d_values = [r["cohens_d"] for r in results]
    ci_lows = [r["ci_low"] for r in results]
    ci_highs = [r["ci_high"] for r in results]

    # Error bars (horizontal)
    errors = [
        [d - ci_low for d, ci_low in zip(d_values, ci_lows)],
        [ci_high - d for d, ci_high in zip(d_values, ci_highs)]
    ]

    # Colors
    colors = [
        config.VIZ_CONFIG["attention_color"] if lt in config.ATTENTION_LAYER_TYPES
        else config.VIZ_CONFIG["mlp_color"]
        for lt in layer_types
    ]

    # Horizontal bar plot (reverse order for top-to-bottom ranking)
    y_pos = np.arange(len(layer_types))
    bars = ax.barh(y_pos, d_values, color=colors, edgecolor="black", linewidth=0.5)

    # Add error bars
    ax.errorbar(
        d_values, y_pos,
        xerr=errors,
        fmt='none',
        ecolor='black',
        capsize=3,
        capthick=1,
    )

    # Threshold line
    ax.axvline(
        x=config.ANALYSIS_CONFIG["cohens_d_threshold"],
        color=config.VIZ_CONFIG["threshold_line_color"],
        linestyle='--',
        linewidth=2,
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(layer_types)
    ax.invert_yaxis()  # Best at top
    ax.set_xlabel("Cohen's d", fontsize=12)
    ax.set_title("Layer Types Ranked by Cohen's d", fontsize=14)

    # Add value annotations
    for bar, d_val in zip(bars, d_values):
        ax.annotate(
            f"{d_val:.3f}",
            xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha='left',
            va='center',
            fontsize=10,
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=config.VIZ_CONFIG["dpi"], format=config.VIZ_CONFIG["format"])
    plt.close()
    print(f"Saved: {output_path}")


def plot_attention_vs_mlp(
    results: list[CohensDResult],
    group_stats: dict,
    output_path: str,
) -> None:
    """
    Box/violin plot comparing attention vs MLP group Cohen's d.

    Args:
        results: List of CohensDResult
        group_stats: Output from compute_group_statistics
        output_path: Path to save figure
    """
    setup_style()

    fig, ax = plt.subplots(figsize=config.VIZ_CONFIG["comparison_figsize"])

    # Prepare data for box plot
    attn_d = group_stats["attention_d_values"]
    mlp_d = group_stats["mlp_d_values"]

    data = [attn_d, mlp_d]
    labels = ["Attention\n(q/k/v/o)", "MLP\n(up/down/gate)"]
    colors = [config.VIZ_CONFIG["attention_color"], config.VIZ_CONFIG["mlp_color"]]

    # Box plot with swarm overlay
    bp = ax.boxplot(
        data,
        positions=[0, 1],
        widths=0.5,
        patch_artist=True,
        showmeans=True,
        meanprops=dict(marker='D', markerfacecolor='white', markeredgecolor='black'),
    )

    # Color boxes
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Add individual points
    for i, (d_vals, color) in enumerate(zip(data, colors)):
        x_jitter = np.random.uniform(-0.1, 0.1, len(d_vals))
        ax.scatter(
            [i] * len(d_vals) + x_jitter,
            d_vals,
            color=color,
            edgecolor="black",
            s=80,
            alpha=0.8,
            zorder=3,
        )

    ax.set_xticks([0, 1])
    ax.set_xticklabels(labels)
    ax.set_ylabel("Cohen's d", fontsize=12)
    ax.set_title("Attention vs MLP Layer Groups", fontsize=14)

    # Annotate with statistics
    p_val = group_stats["p_value"]
    diff = group_stats["group_difference"]
    annotation = f"Difference: {diff:.3f}\nMann-Whitney p = {p_val:.3f}" if p_val else ""
    ax.annotate(
        annotation,
        xy=(0.5, 0.95),
        xycoords="axes fraction",
        ha="center",
        va="top",
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    # Add mean annotations
    ax.annotate(f"mean={group_stats['attention_mean']:.3f}", xy=(0, group_stats['attention_mean']),
                xytext=(0.2, group_stats['attention_mean']), fontsize=9, ha="left")
    ax.annotate(f"mean={group_stats['mlp_mean']:.3f}", xy=(1, group_stats['mlp_mean']),
                xytext=(1.2, group_stats['mlp_mean']), fontsize=9, ha="left")

    plt.tight_layout()
    plt.savefig(output_path, dpi=config.VIZ_CONFIG["dpi"], format=config.VIZ_CONFIG["format"])
    plt.close()
    print(f"Saved: {output_path}")


def plot_best_layer_heatmap(
    distance_matrix: np.ndarray,
    records: list[AdapterRecord],
    best_layer_type: str,
    output_path: str,
) -> None:
    """
    8x8 task-level mean distance heatmap for highest-d layer type.

    Aggregates 40x40 -> 8x8 by averaging seeds per task pair.

    Args:
        distance_matrix: (40, 40) distance matrix for best layer type
        records: List of AdapterRecord
        best_layer_type: Name of best performing layer type
        output_path: Path to save figure
    """
    setup_style()

    fig, ax = plt.subplots(figsize=config.VIZ_CONFIG["heatmap_figsize"])

    # Aggregate to task level
    task_matrix = _aggregate_to_task_level(distance_matrix, records)

    # Plot heatmap
    sns.heatmap(
        task_matrix,
        annot=True,
        fmt=".3f",
        cmap="YlOrRd",
        xticklabels=config.TASKS,
        yticklabels=config.TASKS,
        ax=ax,
        square=True,
        cbar_kws={"label": "Mean Grassmann Distance"},
    )

    ax.set_title(f"Task-Level Distances ({best_layer_type})", fontsize=14)

    # Add category annotations
    for i, task in enumerate(config.TASKS):
        cat = config.TASK_CATEGORIES[task]
        color = config.VIZ_CONFIG["attention_color"] if cat == "reasoning" else config.VIZ_CONFIG["mlp_color"]
        ax.axhline(y=i, color=color, linewidth=0.5, alpha=0.3)
        ax.axvline(x=i, color=color, linewidth=0.5, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=config.VIZ_CONFIG["dpi"], format=config.VIZ_CONFIG["format"])
    plt.close()
    print(f"Saved: {output_path}")


def _aggregate_to_task_level(
    distance_matrix: np.ndarray,
    records: list[AdapterRecord],
) -> np.ndarray:
    """
    Aggregate 40x40 adapter distances to 8x8 task distances.

    Args:
        distance_matrix: (40, 40) pairwise adapter distances
        records: List of AdapterRecord

    Returns:
        (8, 8) task-level mean distances
    """
    n_tasks = len(config.TASKS)
    task_matrix = np.zeros((n_tasks, n_tasks))

    # Map task name to indices in records
    task_to_indices = {task: [] for task in config.TASKS}
    for i, record in enumerate(records):
        task_to_indices[record.task].append(i)

    # Compute mean distance between all pairs of tasks
    for i, task_i in enumerate(config.TASKS):
        for j, task_j in enumerate(config.TASKS):
            if i == j:
                # Within-task: mean of all seed pairs (excluding diagonal)
                indices = task_to_indices[task_i]
                dists = []
                for a in indices:
                    for b in indices:
                        if a != b:
                            dists.append(distance_matrix[a, b])
                task_matrix[i, j] = np.mean(dists) if dists else 0.0
            else:
                # Between-task: mean of all cross-seed pairs
                indices_i = task_to_indices[task_i]
                indices_j = task_to_indices[task_j]
                dists = []
                for a in indices_i:
                    for b in indices_j:
                        dists.append(distance_matrix[a, b])
                task_matrix[i, j] = np.mean(dists) if dists else 0.0

    return task_matrix


def generate_all_figures(
    results: list[CohensDResult],
    distances: dict[str, np.ndarray],
    records: list[AdapterRecord],
    group_stats: dict,
    figures_dir: str,
) -> list[str]:
    """
    Generate all 4 required figures.

    Args:
        results: List of CohensDResult
        distances: Dict of layer_type -> distance matrices
        records: List of AdapterRecord
        group_stats: Output from compute_group_statistics
        figures_dir: Directory to save figures

    Returns:
        List of generated figure paths
    """
    os.makedirs(figures_dir, exist_ok=True)
    generated = []

    # 1. Bar chart with CI
    path1 = os.path.join(figures_dir, "cohens_d_by_layer_type.png")
    plot_cohens_d_by_layer_type(results, path1)
    generated.append(path1)

    # 2. Ranking chart
    path2 = os.path.join(figures_dir, "layer_type_ranking.png")
    plot_layer_type_ranking(results, path2)
    generated.append(path2)

    # 3. Attention vs MLP comparison
    path3 = os.path.join(figures_dir, "attention_vs_mlp.png")
    plot_attention_vs_mlp(results, group_stats, path3)
    generated.append(path3)

    # 4. Best layer heatmap
    best_layer = results[0]["layer_type"]
    path4 = os.path.join(figures_dir, f"best_layer_heatmap_{best_layer}.png")
    plot_best_layer_heatmap(distances[best_layer], records, best_layer, path4)
    generated.append(path4)

    print(f"\nGenerated {len(generated)} figures in {figures_dir}")
    return generated
