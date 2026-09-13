"""Visualizer: Generate figures for H-M3 correlation analysis."""

import os
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

import config
from correlation import CorrelationResult, P3ControlResult


def plot_gate_metrics_bar(
    corr: CorrelationResult,
    out_dir: str,
) -> None:
    """
    Bar chart: Spearman rho vs threshold 0.3 with p-value + CI annotation.

    Args:
        corr: CorrelationResult object
        out_dir: Output directory for figure
    """
    sns.set_style(config.VIZ_CONFIG["style"])
    sns.set_context("paper", font_scale=config.VIZ_CONFIG["font_scale"])

    fig, ax = plt.subplots(figsize=config.VIZ_CONFIG["bar_chart_figsize"])

    # Bar for observed rho
    rho = corr.spearman_rho
    threshold = config.ANALYSIS_CONFIG["spearman_rho_threshold"]

    bar_color = config.VIZ_CONFIG["reasoning_color"] if rho > threshold else "#d62728"
    ax.bar(["Spearman ρ"], [rho], color=bar_color, alpha=0.8, width=0.5)

    # Error bars for CI
    yerr = [[rho - corr.ci_low], [corr.ci_high - rho]]
    ax.errorbar(["Spearman ρ"], [rho], yerr=yerr, fmt='none', color='black', capsize=5)

    # Threshold line
    ax.axhline(y=threshold, color=config.VIZ_CONFIG["threshold_line_color"],
               linestyle='--', linewidth=2, label=f'Threshold = {threshold}')

    # Annotations
    status = "PASS" if corr.gate_passed else "FAIL"
    ax.text(0, rho + 0.05, f'ρ = {rho:.4f}\np = {corr.p_value:.2e}\n95% CI: [{corr.ci_low:.4f}, {corr.ci_high:.4f}]',
            ha='center', va='bottom', fontsize=10)

    ax.set_ylabel("Spearman Correlation Coefficient")
    ax.set_title(f"H-M3 Gate Metrics: Spearman Correlation ({status})")
    ax.set_ylim(0, max(1.0, rho + 0.2))
    ax.legend(loc='upper right')

    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "gate_metrics_bar.png")
    plt.savefig(out_path, dpi=config.VIZ_CONFIG["dpi"])
    plt.close()


def plot_scatter_regression(
    grassmann_flat: np.ndarray,
    taxonomy_flat: np.ndarray,
    corr: CorrelationResult,
    out_dir: str,
) -> None:
    """
    Scatter plot of Grassmann vs taxonomy distances with regression line.

    Args:
        grassmann_flat: Flattened Grassmann distances (upper triangle)
        taxonomy_flat: Flattened taxonomy distances (upper triangle)
        corr: CorrelationResult object
        out_dir: Output directory for figure
    """
    sns.set_style(config.VIZ_CONFIG["style"])
    sns.set_context("paper", font_scale=config.VIZ_CONFIG["font_scale"])

    fig, ax = plt.subplots(figsize=config.VIZ_CONFIG["scatter_figsize"])

    # Jitter taxonomy values for better visualization (they're 0 or 1)
    jitter = np.random.default_rng(42).uniform(-0.05, 0.05, len(taxonomy_flat))
    taxonomy_jittered = taxonomy_flat + jitter

    # Scatter with color by category
    colors = [config.VIZ_CONFIG["reasoning_color"] if t == 0 else config.VIZ_CONFIG["nlu_color"]
              for t in taxonomy_flat]
    ax.scatter(taxonomy_jittered, grassmann_flat, c=colors, alpha=0.5, s=20)

    # Regression line
    slope, intercept, r_value, p_value, std_err = stats.linregress(taxonomy_flat, grassmann_flat)
    x_line = np.array([0, 1])
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, color=config.VIZ_CONFIG["regression_line_color"],
            linewidth=2, label=f'Regression (slope={slope:.4f})')

    # Add category means
    same_cat_mean = np.mean(grassmann_flat[taxonomy_flat == 0])
    diff_cat_mean = np.mean(grassmann_flat[taxonomy_flat == 1])
    ax.scatter([0, 1], [same_cat_mean, diff_cat_mean], marker='D', s=100,
               c=['green', 'red'], edgecolor='black', zorder=5,
               label=f'Category means')

    # Annotations
    ax.annotate(f'Spearman ρ = {corr.spearman_rho:.4f}\np = {corr.p_value:.2e}',
                xy=(0.05, 0.95), xycoords='axes fraction',
                fontsize=10, va='top', ha='left',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel("Taxonomy Distance (0=same category, 1=different)")
    ax.set_ylabel("Grassmann Distance")
    ax.set_title("Grassmann Distance vs FLAN Taxonomy Distance")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Same Category", "Different Category"])
    ax.legend(loc='lower right')

    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "scatter_regression.png")
    plt.savefig(out_path, dpi=config.VIZ_CONFIG["dpi"])
    plt.close()


def plot_correlation_heatmap(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],
    out_dir: str,
) -> None:
    """
    Task-level mean distance heatmap (8x8), sorted by FLAN category.

    Args:
        grassmann_matrix: (40, 40) Grassmann distance matrix
        adapter_meta: List of adapter metadata dicts
        out_dir: Output directory for figure
    """
    sns.set_style(config.VIZ_CONFIG["style"])
    sns.set_context("paper", font_scale=config.VIZ_CONFIG["font_scale"])

    # Group adapters by task and compute mean distances
    tasks = config.TASKS
    n_tasks = len(tasks)
    task_mean_matrix = np.zeros((n_tasks, n_tasks))

    # Create task to adapter indices mapping
    task_to_indices = defaultdict(list)
    for i, meta in enumerate(adapter_meta):
        task_to_indices[meta['task']].append(i)

    # Compute task-level mean distances
    for i, task_i in enumerate(tasks):
        for j, task_j in enumerate(tasks):
            indices_i = task_to_indices[task_i]
            indices_j = task_to_indices[task_j]
            distances = []
            for idx_i in indices_i:
                for idx_j in indices_j:
                    if idx_i != idx_j:
                        distances.append(grassmann_matrix[idx_i, idx_j])
            task_mean_matrix[i, j] = np.mean(distances) if distances else 0

    # Sort by category (reasoning first, then nlu)
    category_order = ['reasoning', 'nlu']
    sorted_tasks = []
    for cat in category_order:
        sorted_tasks.extend([t for t in tasks if config.FLAN_CATEGORIES[t] == cat])

    # Reorder matrix
    task_to_idx = {t: i for i, t in enumerate(tasks)}
    new_order = [task_to_idx[t] for t in sorted_tasks]
    sorted_matrix = task_mean_matrix[np.ix_(new_order, new_order)]

    # Plot heatmap
    fig, ax = plt.subplots(figsize=config.VIZ_CONFIG["heatmap_figsize"])

    sns.heatmap(sorted_matrix, annot=True, fmt='.3f', cmap='RdYlBu_r',
                xticklabels=sorted_tasks, yticklabels=sorted_tasks,
                ax=ax, cbar_kws={'label': 'Mean Grassmann Distance'})

    # Add category boundary lines
    n_reasoning = len([t for t in sorted_tasks if config.FLAN_CATEGORIES[t] == 'reasoning'])
    ax.axhline(y=n_reasoning, color='black', linewidth=2)
    ax.axvline(x=n_reasoning, color='black', linewidth=2)

    ax.set_title("Task-Level Mean Grassmann Distances\n(sorted by FLAN category)")
    ax.set_xlabel("Task")
    ax.set_ylabel("Task")

    # Rotate labels
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "correlation_heatmap.png")
    plt.savefig(out_path, dpi=config.VIZ_CONFIG["dpi"])
    plt.close()


def plot_p3_control_distributions(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],
    p3: P3ControlResult,
    out_dir: str,
) -> None:
    """
    KDE/box: within-task vs within-cluster distance distributions.

    Args:
        grassmann_matrix: (40, 40) Grassmann distance matrix
        adapter_meta: List of adapter metadata dicts
        p3: P3ControlResult object
        out_dir: Output directory for figure
    """
    from correlation import _extract_within_task_distances, _extract_within_cluster_distances

    sns.set_style(config.VIZ_CONFIG["style"])
    sns.set_context("paper", font_scale=config.VIZ_CONFIG["font_scale"])

    # Extract distances
    within_task = _extract_within_task_distances(grassmann_matrix, adapter_meta)
    within_cluster = _extract_within_cluster_distances(grassmann_matrix, adapter_meta)

    fig, axes = plt.subplots(1, 2, figsize=config.VIZ_CONFIG["distribution_figsize"])

    # Left: KDE plots
    ax1 = axes[0]
    sns.kdeplot(within_task, ax=ax1, label=f'Within-Task (n={len(within_task)})',
                color=config.VIZ_CONFIG["reasoning_color"], fill=True, alpha=0.3)
    sns.kdeplot(within_cluster, ax=ax1, label=f'Within-Cluster (n={len(within_cluster)})',
                color=config.VIZ_CONFIG["nlu_color"], fill=True, alpha=0.3)

    # Add mean lines
    ax1.axvline(p3.within_task_mean, color=config.VIZ_CONFIG["reasoning_color"],
                linestyle='--', linewidth=2, label=f'Task Mean: {p3.within_task_mean:.4f}')
    ax1.axvline(p3.within_cluster_mean, color=config.VIZ_CONFIG["nlu_color"],
                linestyle='--', linewidth=2, label=f'Cluster Mean: {p3.within_cluster_mean:.4f}')

    ax1.set_xlabel("Grassmann Distance")
    ax1.set_ylabel("Density")
    ax1.set_title("Distance Distributions (KDE)")
    ax1.legend(loc='upper right', fontsize=8)

    # Right: Box plots
    ax2 = axes[1]
    data = [within_task, within_cluster]
    labels = ['Within-Task', 'Within-Cluster']
    colors = [config.VIZ_CONFIG["reasoning_color"], config.VIZ_CONFIG["nlu_color"]]

    bp = ax2.boxplot(data, labels=labels, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    # Add P3 control annotation
    status = "PASS" if p3.control_passed else "FAIL"
    threshold = config.ANALYSIS_CONFIG["p3_ratio_threshold"]
    ax2.annotate(f'P3 Control: {status}\nRatio: {p3.ratio:.4f}\nThreshold: {threshold}',
                 xy=(0.5, 0.95), xycoords='axes fraction',
                 fontsize=10, va='top', ha='center',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax2.set_ylabel("Grassmann Distance")
    ax2.set_title("Distance Distributions (Box)")

    plt.suptitle("P3 Control Analysis: Within-Task vs Within-Cluster Distances")
    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "p3_control.png")
    plt.savefig(out_path, dpi=config.VIZ_CONFIG["dpi"])
    plt.close()


def generate_all_figures(
    hypothesis_folder: str,
    grassmann_matrix: np.ndarray,
    taxonomy_matrix: np.ndarray,
    adapter_meta: list[dict],
    corr: CorrelationResult,
    p3: P3ControlResult,
) -> None:
    """
    Generate and save all 4 figures to {hypothesis_folder}/figures/.

    Args:
        hypothesis_folder: Path to hypothesis folder
        grassmann_matrix: (40, 40) Grassmann distance matrix
        taxonomy_matrix: (40, 40) taxonomy distance matrix
        adapter_meta: List of adapter metadata dicts
        corr: CorrelationResult object
        p3: P3ControlResult object
    """
    figures_dir = os.path.join(hypothesis_folder, "figures")
    os.makedirs(figures_dir, exist_ok=True)

    # Flatten matrices for scatter plot
    from correlation import _flatten_upper_triangle
    grassmann_flat = _flatten_upper_triangle(grassmann_matrix)
    taxonomy_flat = _flatten_upper_triangle(taxonomy_matrix)

    print("Generating figures...")

    # 1. Gate metrics bar chart
    print("  - gate_metrics_bar.png")
    plot_gate_metrics_bar(corr, figures_dir)

    # 2. Scatter + regression plot
    print("  - scatter_regression.png")
    plot_scatter_regression(grassmann_flat, taxonomy_flat, corr, figures_dir)

    # 3. Correlation heatmap
    print("  - correlation_heatmap.png")
    plot_correlation_heatmap(grassmann_matrix, adapter_meta, figures_dir)

    # 4. P3 control distributions
    print("  - p3_control.png")
    plot_p3_control_distributions(grassmann_matrix, adapter_meta, p3, figures_dir)

    print(f"All figures saved to: {figures_dir}")
