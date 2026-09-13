"""
visualize.py — 5 required figures for H-M1 NLI distribution analysis
"""
import logging
import os
from typing import List

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


def plot_gate_metrics_comparison(
    results: List,
    config,
    output_path: str,
) -> None:
    """2-subplot: KL divergence bars + Wilcoxon p-values (log scale) with thresholds.

    subplot 1 = KL divergence bars per task with threshold line at config.kl_threshold
    subplot 2 = Wilcoxon p-values log-scale with alpha line at config.wilcoxon_alpha
    Bars colored pass=config.fig_bar_color_pass / fail=config.fig_bar_color_fail
    """
    task_names = [r.task_name for r in results]
    kl_values = [r.kl_divergence_from_uniform for r in results]
    pvalues = [r.wilcoxon_pvalue for r in results]
    kl_colors = [config.fig_bar_color_pass if r.kl_passes else config.fig_bar_color_fail for r in results]
    p_colors = [config.fig_bar_color_pass if r.wilcoxon_passes else config.fig_bar_color_fail for r in results]

    fig, axes = plt.subplots(1, 2, figsize=config.fig_gate_figsize, dpi=config.fig_dpi)

    # Subplot 1: KL divergence
    ax1 = axes[0]
    bars1 = ax1.bar(task_names, kl_values, color=kl_colors, alpha=0.85, edgecolor="white")
    ax1.axhline(y=config.kl_threshold, color=config.fig_threshold_color, linestyle="--",
                linewidth=2, label=f"Threshold ({config.kl_threshold})")
    ax1.set_title("KL Divergence from Uniform", fontsize=13, fontweight="bold")
    ax1.set_ylabel("KL Divergence (nats)", fontsize=11)
    ax1.set_xlabel("Task", fontsize=11)
    ax1.legend(fontsize=10)
    for bar, val in zip(bars1, kl_values):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                 f"{val:.4f}", ha="center", va="bottom", fontsize=9)

    # Subplot 2: Wilcoxon p-values (log scale)
    ax2 = axes[1]
    # Clip p-values to avoid log(0)
    pvalues_clipped = [max(p, 1e-300) for p in pvalues]
    bars2 = ax2.bar(task_names, pvalues_clipped, color=p_colors, alpha=0.85, edgecolor="white")
    ax2.axhline(y=config.wilcoxon_alpha, color=config.fig_threshold_color, linestyle="--",
                linewidth=2, label=f"α = {config.wilcoxon_alpha}")
    ax2.set_yscale("log")
    ax2.set_title("Wilcoxon Rank-Sum p-values", fontsize=13, fontweight="bold")
    ax2.set_ylabel("p-value (log scale)", fontsize=11)
    ax2.set_xlabel("Task", fontsize=11)
    ax2.legend(fontsize=10)

    plt.suptitle("H-M1 Gate Metrics: NLI Distribution Analysis", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved gate_metrics_comparison to: {output_path}")


def plot_score_distributions_violin(
    task_data_list: List,
    config,
    output_path: str,
) -> None:
    """Per-task violin plots: P(contra/neutral/entail) split by hallucinated vs correct.

    3-task violin plots, uniform ref line at 1/3
    """
    nli_labels = ["P(contra)", "P(neutral)", "P(entail)"]
    n_tasks = len(task_data_list)

    fig, axes = plt.subplots(1, n_tasks, figsize=config.fig_violin_figsize, dpi=config.fig_dpi)
    if n_tasks == 1:
        axes = [axes]

    for ax, td in zip(axes, task_data_list):
        scores = td.scores_nxt3
        labels = td.labels_n

        hal_scores = scores[labels == 1]   # hallucinated
        corr_scores = scores[labels == 0]  # correct

        # Build violin data: for each NLI class, two groups
        positions = []
        data_groups = []
        colors = []
        x_ticks = []
        x_labels = []

        for i, nli_cls in enumerate(nli_labels):
            pos_corr = i * 3 + 1
            pos_hall = i * 3 + 2

            positions.extend([pos_corr, pos_hall])
            data_groups.extend([corr_scores[:, i], hal_scores[:, i]])
            colors.extend([config.fig_violin_color_corr, config.fig_violin_color_hall])

            mid = (pos_corr + pos_hall) / 2
            x_ticks.append(mid)
            x_labels.append(nli_cls)

        vp = ax.violinplot(data_groups, positions=positions, showmedians=True)

        # Color each violin
        for body, color in zip(vp["bodies"], colors):
            body.set_facecolor(color)
            body.set_alpha(0.7)

        # Uniform reference line at 1/3
        ax.axhline(y=1/3, color=config.fig_uniform_ref_color, linestyle="--",
                   linewidth=1.5, label="Uniform (1/3)", alpha=0.8)

        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels, fontsize=9)
        ax.set_title(f"{td.task_name}", fontsize=12, fontweight="bold")
        ax.set_ylabel("Score" if ax == axes[0] else "", fontsize=10)
        ax.set_ylim([-0.05, 1.05])

        if ax == axes[0]:
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor=config.fig_violin_color_corr, label="Correct"),
                Patch(facecolor=config.fig_violin_color_hall, label="Hallucinated"),
            ]
            ax.legend(handles=legend_elements, fontsize=9, loc="upper right")

    plt.suptitle("H-M1: NLI Score Distributions by Hallucination Label", fontsize=13, fontweight="bold")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved score_distributions_violin to: {output_path}")


def plot_kl_divergence_summary(
    results: List,
    config,
    output_path: str,
    task_data_list: List = None,
) -> None:
    """3x3 bar chart: KL per task x per NLI class. Threshold at config.kl_threshold."""
    nli_labels = ["P(contra)", "P(neutral)", "P(entail)"]
    task_names = [r.task_name for r in results]
    n_tasks = len(task_names)

    # Compute per-class KL using class_means
    from scipy.stats import entropy as scipy_entropy

    fig, axes = plt.subplots(1, n_tasks, figsize=config.fig_kl_summary_figsize, dpi=config.fig_dpi)
    if n_tasks == 1:
        axes = [axes]

    for ax, r in zip(axes, results):
        class_means = np.array(r.class_means)
        uniform = np.array([1/3, 1/3, 1/3])

        # Per-class KL: treat each class as a 2-element distribution
        per_class_kl = []
        for i in range(3):
            p = np.array([class_means[i] + 1e-10, 1 - class_means[i] + 1e-10])
            q = np.array([1/3 + 1e-10, 2/3 + 1e-10])
            per_class_kl.append(float(scipy_entropy(p, q)))

        bar_colors = [
            config.fig_bar_color_pass if kl > config.kl_threshold else config.fig_bar_color_fail
            for kl in per_class_kl
        ]
        bars = ax.bar(nli_labels, per_class_kl, color=bar_colors, alpha=0.85, edgecolor="white")
        ax.axhline(y=config.kl_threshold, color=config.fig_threshold_color, linestyle="--",
                   linewidth=1.5, label=f"Threshold ({config.kl_threshold})")
        ax.set_title(f"{r.task_name}\nKL={r.kl_divergence_from_uniform:.4f}", fontsize=11, fontweight="bold")
        ax.set_ylabel("Per-class KL" if ax == axes[0] else "", fontsize=10)
        ax.set_xticklabels(nli_labels, fontsize=9)
        if ax == axes[0]:
            ax.legend(fontsize=9)

    plt.suptitle("H-M1: Per-Class KL Divergence from Uniform", fontsize=13, fontweight="bold")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved kl_divergence_summary to: {output_path}")


def plot_score_separation_boxplot(
    task_data_list: List,
    results: List,
    config,
    output_path: str,
) -> None:
    """Box plots: P(contradiction) hallu vs correct per task, annotated with p-values."""
    n_tasks = len(task_data_list)
    fig, axes = plt.subplots(1, n_tasks, figsize=config.fig_box_figsize, dpi=config.fig_dpi)
    if n_tasks == 1:
        axes = [axes]

    results_map = {r.task_name: r for r in results}

    for ax, td in zip(axes, task_data_list):
        scores = td.scores_nxt3[:, 0]  # P(contradiction)
        labels = td.labels_n
        corr_scores = scores[labels == 0]
        hal_scores = scores[labels == 1]

        bp = ax.boxplot(
            [corr_scores, hal_scores],
            labels=["Correct", "Hallucinated"],
            patch_artist=True,
            medianprops=dict(color="black", linewidth=2),
            whiskerprops=dict(linewidth=1.5),
            capprops=dict(linewidth=1.5),
        )
        bp["boxes"][0].set_facecolor(config.fig_box_color_corr)
        bp["boxes"][0].set_alpha(0.75)
        bp["boxes"][1].set_facecolor(config.fig_box_color_hall)
        bp["boxes"][1].set_alpha(0.75)

        # Annotate with Wilcoxon p-value
        r = results_map.get(td.task_name)
        if r:
            pval = r.wilcoxon_pvalue
            sig = "***" if pval < 0.001 else ("**" if pval < 0.01 else ("*" if pval < 0.05 else "ns"))
            y_max = max(np.percentile(hal_scores, 95), np.percentile(corr_scores, 95))
            ax.text(1.5, y_max * 1.05, f"p={pval:.2e}\n{sig}", ha="center", fontsize=9,
                    color="darkred" if pval < config.wilcoxon_alpha else "gray")

        ax.set_title(f"{td.task_name}", fontsize=12, fontweight="bold")
        ax.set_ylabel("P(contradiction)" if ax == axes[0] else "", fontsize=10)

    plt.suptitle("H-M1: P(Contradiction) Score Separation by Hallucination Label", fontsize=13, fontweight="bold")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved score_separation_boxplot to: {output_path}")


def plot_near_uniform_proportion(
    results: List,
    config,
    output_path: str,
) -> None:
    """Stacked bar: p_near_uniform per task with target < 5% line."""
    task_names = [r.task_name for r in results]
    p_near_uniform = [r.p_near_uniform for r in results]
    p_not_near_uniform = [1.0 - p for p in p_near_uniform]

    fig, ax = plt.subplots(figsize=config.fig_near_uniform_figsize, dpi=config.fig_dpi)

    x = np.arange(len(task_names))
    width = 0.5

    bars_near = ax.bar(x, p_near_uniform, width, label="Near-uniform", color="#9E9E9E", alpha=0.8)
    bars_not = ax.bar(x, p_not_near_uniform, width, bottom=p_near_uniform,
                      label="Not near-uniform", color=config.fig_bar_color_pass, alpha=0.8)

    ax.axhline(y=0.05, color=config.fig_near_uniform_target_color, linestyle="--",
               linewidth=2, label="Target < 5%")

    ax.set_xticks(x)
    ax.set_xticklabels(task_names, fontsize=11)
    ax.set_ylabel("Proportion", fontsize=11)
    ax.set_ylim([0, 1.05])
    ax.set_title("Near-Uniform Score Proportion per Task", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)

    for bar, val in zip(bars_near, p_near_uniform):
        if val > 0.01:
            ax.text(bar.get_x() + bar.get_width() / 2, val / 2,
                    f"{val:.3f}", ha="center", va="center", fontsize=9, color="white", fontweight="bold")

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved near_uniform_proportion to: {output_path}")


def generate_all_figures(
    task_data_list: List,
    results: List,
    config,
    figures_dir: str,
) -> None:
    """Generate and save all 5 required figures."""
    os.makedirs(figures_dir, exist_ok=True)

    plot_gate_metrics_comparison(
        results, config,
        os.path.join(figures_dir, "gate_metrics_comparison.png")
    )
    plot_score_distributions_violin(
        task_data_list, config,
        os.path.join(figures_dir, "score_distributions_violin.png")
    )
    plot_kl_divergence_summary(
        results, config,
        os.path.join(figures_dir, "kl_divergence_summary.png")
    )
    plot_score_separation_boxplot(
        task_data_list, results, config,
        os.path.join(figures_dir, "score_separation_boxplot.png")
    )
    plot_near_uniform_proportion(
        results, config,
        os.path.join(figures_dir, "near_uniform_proportion.png")
    )
    logger.info(f"All 5 figures generated in: {figures_dir}")
