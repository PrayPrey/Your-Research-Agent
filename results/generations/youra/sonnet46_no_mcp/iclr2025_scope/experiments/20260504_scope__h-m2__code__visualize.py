import os
import logging
from typing import Dict, List

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import LONGBENCH_CATEGORIES, COLOR_MAP, LINE_STYLE_MAP, VIZ_CONFIG

logger = logging.getLogger(__name__)

BUDGET_RATIOS = [0.25, 0.50, 0.75]


def plot_gap_vs_budget(gap_matrices: Dict[str, object], output_path: str) -> None:
    """Line plot: x=budget ratio, y=mean gap, lines per model."""
    fig, ax = plt.subplots(figsize=VIZ_CONFIG["gap_vs_budget"]["figsize"])

    for model_name, gm in gap_matrices.items():
        mean_vals = [gm.mean_gaps.get(r, float("nan")) for r in BUDGET_RATIOS]
        std_vals = []
        for r in BUDGET_RATIOS:
            cat_vals = [v for v in gm.gaps.get(r, {}).values() if not np.isnan(v)]
            std_vals.append(float(np.std(cat_vals)) if cat_vals else 0.0)

        label = model_name.split("/")[-1] if "/" in model_name else model_name
        ls = LINE_STYLE_MAP.get(model_name, "-")
        ax.errorbar(
            BUDGET_RATIOS, mean_vals, yerr=std_vals,
            label=label, linestyle=ls, marker="o", capsize=4,
        )

    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, label="no gap")
    ax.set_xlabel("KV Budget Ratio (r)")
    ax.set_ylabel("Mean Accuracy Gap (eviction-aware - sequential)")
    ax.set_title("Accuracy Gap vs KV Budget Ratio")
    ax.set_xticks(BUDGET_RATIOS)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def plot_spearman_bar(
    spearman_results: List[object],
    threshold: float = -0.8,
    output_path: str = "",
) -> None:
    """Bar chart: Spearman rho per model, reference line at threshold."""
    if isinstance(spearman_results, dict):
        items = list(spearman_results.values())
    else:
        items = list(spearman_results)

    fig, ax = plt.subplots(figsize=VIZ_CONFIG["spearman_bar"]["figsize"])
    labels = [sr.model_name.split("/")[-1] if "/" in sr.model_name else sr.model_name for sr in items]
    rhos = [sr.rho if not np.isnan(sr.rho) else 0.0 for sr in items]
    colors = ["#4CAF50" if sr.gate_passed else "#F44336" for sr in items]

    bars = ax.bar(labels, rhos, color=colors, alpha=0.8)
    ax.axhline(threshold, color="red", linestyle="--", linewidth=1.5, label=f"gate threshold (ρ={threshold})")
    ax.set_ylim(-1.1, 1.1)
    ax.set_ylabel("Spearman ρ")
    ax.set_title("Spearman Correlation: Budget Ratio vs Accuracy Gap")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def plot_gap_heatmap(gap_matrices: Dict[str, object], output_path: str) -> None:
    """6-category x 3-budget-ratio heatmap, color=gap magnitude, per model."""
    categories = list(LONGBENCH_CATEGORIES.keys())
    n_models = len(gap_matrices)
    fig, axes = plt.subplots(1, max(n_models, 1), figsize=VIZ_CONFIG["gap_heatmap"]["figsize"])
    if n_models == 1:
        axes = [axes]

    for ax, (model_name, gm) in zip(axes, gap_matrices.items()):
        data = np.zeros((len(categories), len(BUDGET_RATIOS)))
        for ci, cat in enumerate(categories):
            for ri, r in enumerate(BUDGET_RATIOS):
                val = gm.gaps.get(r, {}).get(cat, float("nan"))
                data[ci, ri] = val if not np.isnan(val) else 0.0

        vmax = max(abs(data.max()), abs(data.min()), 0.01)
        im = ax.imshow(data, aspect="auto", cmap="RdBu", vmin=-vmax, vmax=vmax)
        ax.set_xticks(range(len(BUDGET_RATIOS)))
        ax.set_xticklabels([str(r) for r in BUDGET_RATIOS])
        ax.set_yticks(range(len(categories)))
        ax.set_yticklabels(categories)
        label = model_name.split("/")[-1] if "/" in model_name else model_name
        ax.set_title(label)
        ax.set_xlabel("KV Budget Ratio")
        plt.colorbar(im, ax=ax, label="Gap")

    plt.suptitle("Accuracy Gap Heatmap (eviction-aware - sequential)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def plot_absolute_accuracy_curves(results: List[object], output_path: str) -> None:
    """Per-model line plots of absolute accuracy (both adapter types at each r)."""
    from collections import defaultdict
    by_model = defaultdict(lambda: {"sequential": {}, "eviction-aware": {}})
    for r in results:
        mean_cat = float(np.nanmean(list(r.category_scores.values())))
        by_model[r.model_name][r.adapter_type][r.budget_ratio] = mean_cat

    n_models = len(by_model)
    fig, axes = plt.subplots(1, max(n_models, 1), figsize=VIZ_CONFIG["absolute_curves"]["figsize"])
    if n_models == 1:
        axes = [axes]

    for ax, (model_name, adapter_data) in zip(axes, by_model.items()):
        for adapter_type, scores_by_r in adapter_data.items():
            ratios = sorted(scores_by_r.keys())
            vals = [scores_by_r[r] for r in ratios]
            color = COLOR_MAP.get(adapter_type, "gray")
            ls = "-" if adapter_type == "eviction-aware" else "--"
            ax.plot(ratios, vals, color=color, linestyle=ls, marker="o", label=adapter_type)

        label = model_name.split("/")[-1] if "/" in model_name else model_name
        ax.set_title(label)
        ax.set_xlabel("KV Budget Ratio")
        ax.set_ylabel("Mean Category Accuracy")
        ax.set_xticks(BUDGET_RATIOS)
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.suptitle("Absolute Accuracy Curves by Adapter Type")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved: {output_path}")


def save_all_figures(analysis: dict, results: List[object], figures_dir: str) -> None:
    """Save all 4 mandatory figures to figures_dir."""
    os.makedirs(figures_dir, exist_ok=True)

    plot_gap_vs_budget(
        analysis["gap_matrices"],
        os.path.join(figures_dir, VIZ_CONFIG["gap_vs_budget"]["filename"]),
    )
    plot_spearman_bar(
        analysis["spearman_results"],
        threshold=-0.8,
        output_path=os.path.join(figures_dir, VIZ_CONFIG["spearman_bar"]["filename"]),
    )
    plot_gap_heatmap(
        analysis["gap_matrices"],
        os.path.join(figures_dir, VIZ_CONFIG["gap_heatmap"]["filename"]),
    )
    plot_absolute_accuracy_curves(
        results,
        os.path.join(figures_dir, VIZ_CONFIG["absolute_curves"]["filename"]),
    )
    logger.info(f"All figures saved to {figures_dir}")
