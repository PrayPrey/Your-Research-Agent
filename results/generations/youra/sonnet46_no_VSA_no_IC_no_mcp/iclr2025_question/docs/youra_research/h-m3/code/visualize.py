import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class FigureConfig:
    dpi: int = 150
    font_size: int = 11
    title_size: int = 13
    label_size: int = 11
    tick_size: int = 9
    legend_size: int = 9
    bar_figsize: Tuple[float, float] = (6.0, 4.5)
    bar_width: float = 0.5
    ci_cap_size: float = 4.0
    dist_figsize: Tuple[float, float] = (7.0, 4.5)
    dist_bins: int = 30
    scatter_figsize: Tuple[float, float] = (5.5, 5.5)
    roc_figsize: Tuple[float, float] = (6.0, 5.5)


METHOD_COLORS = {
    "SCG": "#2196F3",
    "SE": "#FF9800",
    "TE": "#4CAF50",
}

CORRECTNESS_COLORS = {
    "correct": "#4CAF50",
    "incorrect": "#F44336",
}

BAR_STYLE = {
    "alpha": 0.85,
    "edgecolor": "white",
    "linewidth": 0.8,
    "error_kw": {"elinewidth": 1.5, "ecolor": "black", "capthick": 1.5},
}

DIST_STYLE = {
    "hist_alpha": 0.35,
    "kde_linewidth": 2.0,
}

SCATTER_STYLE = {
    "marker": "o",
    "s": 30,
    "alpha": 0.55,
    "edgecolors": "none",
}

ROC_STYLE = {
    "SCG": {"linewidth": 2.0, "linestyle": "-"},
    "SE": {"linewidth": 2.0, "linestyle": "--"},
    "TE": {"linewidth": 2.0, "linestyle": "-."},
    "chance": {"linewidth": 1.0, "linestyle": ":", "color": "grey", "alpha": 0.7},
}


def plot_auroc_comparison(results: dict, out_path: str) -> None:
    fig_cfg = FigureConfig()
    fig, ax = plt.subplots(figsize=fig_cfg.bar_figsize)
    methods = ["SCG", "SE", "TE"]
    aurocs = [results["auroc_scg"], results["auroc_se"], results["auroc_te"]]
    cis = [results["ci_scg"], results["ci_se"], results["ci_te"]]
    yerr = [[a - ci[0] for a, ci in zip(aurocs, cis)],
            [ci[1] - a for a, ci in zip(aurocs, cis)]]
    colors = [METHOD_COLORS[m] for m in methods]
    xs = range(len(methods))
    bars = ax.bar(xs, aurocs, width=fig_cfg.bar_width, color=colors,
                  capsize=fig_cfg.ci_cap_size, **BAR_STYLE)
    ax.errorbar(xs, aurocs, yerr=yerr, fmt="none", **BAR_STYLE["error_kw"])
    ax.set_xticks(list(xs))
    ax.set_xticklabels(methods, fontsize=fig_cfg.tick_size)
    ax.set_ylabel("AUROC", fontsize=fig_cfg.label_size)
    ax.set_title("AUROC Comparison: SCG vs SE vs TE", fontsize=fig_cfg.title_size)
    ax.axhline(0.5, linestyle=":", color="grey", alpha=0.6, linewidth=1.0)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(out_path, dpi=fig_cfg.dpi)
    plt.close()


def plot_scg_score_distribution(scg_scores: dict, em_labels: dict, out_path: str) -> None:
    fig_cfg = FigureConfig()
    fig, ax = plt.subplots(figsize=fig_cfg.dist_figsize)
    correct_scores = [v for q, v in scg_scores.items() if em_labels[q] == 1]
    incorrect_scores = [v for q, v in scg_scores.items() if em_labels[q] == 0]
    bins = np.linspace(0, 1, fig_cfg.dist_bins + 1)
    ax.hist(correct_scores, bins=bins, alpha=DIST_STYLE["hist_alpha"],
            color=CORRECTNESS_COLORS["correct"], label="Correct")
    ax.hist(incorrect_scores, bins=bins, alpha=DIST_STYLE["hist_alpha"],
            color=CORRECTNESS_COLORS["incorrect"], label="Incorrect")
    ax.set_xlabel("SCG Score (higher = more uncertain)", fontsize=fig_cfg.label_size)
    ax.set_ylabel("Count", fontsize=fig_cfg.label_size)
    ax.set_title("SCG Score Distribution by Correctness", fontsize=fig_cfg.title_size)
    ax.legend(fontsize=fig_cfg.legend_size)
    plt.tight_layout()
    plt.savefig(out_path, dpi=fig_cfg.dpi)
    plt.close()


def plot_scg_vs_se_scatter(scg_scores: dict, se_scores: dict, out_path: str) -> None:
    fig_cfg = FigureConfig()
    fig, ax = plt.subplots(figsize=fig_cfg.scatter_figsize)
    qids = list(scg_scores.keys())
    x = [se_scores[q] for q in qids]
    y = [scg_scores[q] for q in qids]
    ax.scatter(x, y, color=METHOD_COLORS["SCG"], **SCATTER_STYLE)
    ax.set_xlabel("SE Score", fontsize=fig_cfg.label_size)
    ax.set_ylabel("SCG Score", fontsize=fig_cfg.label_size)
    ax.set_title("SCG vs SE Score per Question", fontsize=fig_cfg.title_size)
    corr = float(np.corrcoef(x, y)[0, 1])
    ax.text(0.05, 0.95, f"r={corr:.3f}", transform=ax.transAxes,
            fontsize=fig_cfg.legend_size, va="top")
    plt.tight_layout()
    plt.savefig(out_path, dpi=fig_cfg.dpi)
    plt.close()


def plot_roc_curves(
    scg_scores: dict,
    se_scores: dict,
    te_scores: dict,
    em_labels: dict,
    out_path: str,
) -> None:
    fig_cfg = FigureConfig()
    fig, ax = plt.subplots(figsize=fig_cfg.roc_figsize)
    qids = list(scg_scores.keys())
    labels = np.array([em_labels[q] for q in qids])

    for name, scores_dict in [("SCG", scg_scores), ("SE", se_scores), ("TE", te_scores)]:
        scores = np.array([scores_dict[q] for q in qids])
        fpr, tpr, _ = roc_curve(labels, scores)
        style = ROC_STYLE[name]
        ax.plot(fpr, tpr, color=METHOD_COLORS[name], label=name, **style)

    ax.plot([0, 1], [0, 1], **ROC_STYLE["chance"])
    ax.set_xlabel("FPR", fontsize=fig_cfg.label_size)
    ax.set_ylabel("TPR", fontsize=fig_cfg.label_size)
    ax.set_title("ROC Curves: SCG vs SE vs TE", fontsize=fig_cfg.title_size)
    ax.legend(fontsize=fig_cfg.legend_size)
    plt.tight_layout()
    plt.savefig(out_path, dpi=fig_cfg.dpi)
    plt.close()


def generate_all_figures(
    scg_scores: dict,
    se_scores: dict,
    te_scores: dict,
    em_labels: dict,
    results: dict,
    figures_dir: str,
) -> None:
    os.makedirs(figures_dir, exist_ok=True)
    plot_auroc_comparison(results, os.path.join(figures_dir, "auroc_comparison.png"))
    plot_scg_score_distribution(scg_scores, em_labels, os.path.join(figures_dir, "scg_score_distribution.png"))
    plot_scg_vs_se_scatter(scg_scores, se_scores, os.path.join(figures_dir, "scg_vs_se_scatter.png"))
    plot_roc_curves(scg_scores, se_scores, te_scores, em_labels, os.path.join(figures_dir, "roc_curves.png"))
    print(f"[Figures] Saved 4 figures to {figures_dir}")
