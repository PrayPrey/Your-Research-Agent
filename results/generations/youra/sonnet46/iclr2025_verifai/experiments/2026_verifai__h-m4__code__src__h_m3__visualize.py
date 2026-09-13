"""visualize.py — 5 figures for h-m3 P(True) confidence analysis."""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from h_m3.config import FigureConfig, STD_GATE_THRESHOLD

logger = logging.getLogger(__name__)


def plot_gate_check(
    gate_metrics: dict[str, dict],
    threshold: float,
    out_path: Path,
) -> None:
    """Fig 1: Bar chart std(c) per model vs. threshold line."""
    cfg = FigureConfig()
    models = list(gate_metrics.keys())
    stds = [gate_metrics[m]["std_c"] for m in models]
    colors = ["green" if gate_metrics[m]["gate_pass"] else "red" for m in models]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(models, stds, color=colors, alpha=0.75, edgecolor="black")
    ax.axhline(y=threshold, color="black", linestyle="--", linewidth=2, label=f"Threshold={threshold}")
    ax.set_xlabel("Model")
    ax.set_ylabel("std(c)")
    ax.set_title("P(True) Non-Degeneracy Gate Check: std(c) per Model")
    ax.legend()

    # Add value labels
    for bar, std in zip(bars, stds):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.002,
            f"{std:.4f}",
            ha="center", va="bottom", fontsize=9,
        )

    # Add PASS/FAIL labels
    for bar, m in zip(bars, models):
        label = "PASS" if gate_metrics[m]["gate_pass"] else "FAIL"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            0.005,
            label,
            ha="center", va="bottom", fontsize=8, fontweight="bold",
            color="white",
        )

    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.dpi)
    plt.close(fig)
    logger.info(f"Fig 1 saved: {out_path}")


def plot_c_histograms(
    confidence_scores_by_model: dict[str, list[float]],
    out_path: Path,
) -> None:
    """Fig 2: 3-subplot histogram (20 bins) per model."""
    cfg = FigureConfig()
    models = list(confidence_scores_by_model.keys())
    n = len(models)

    fig, axes = plt.subplots(1, n, figsize=(6 * n, 5), sharey=False)
    if n == 1:
        axes = [axes]

    for ax, model_short in zip(axes, models):
        scores = confidence_scores_by_model[model_short]
        ax.hist(scores, bins=cfg.histogram_bins, range=(0, 1), color="steelblue", edgecolor="white", alpha=0.8)
        ax.set_xlabel("Confidence c")
        ax.set_ylabel("Count")
        ax.set_title(f"{model_short}\nstd={np.std(scores):.4f}, mean={np.mean(scores):.4f}")
        ax.axvline(x=0.5, color="red", linestyle="--", alpha=0.5, label="c=0.5")

    fig.suptitle("P(True) Confidence Score Distributions", fontsize=12)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.dpi)
    plt.close(fig)
    logger.info(f"Fig 2 saved: {out_path}")


def plot_c_vs_pass_at_1(
    confidence_scores_by_model: dict[str, list[float]],
    correctness_by_model: dict[str, list[int]],
    out_path: Path,
) -> None:
    """Fig 3: Scatter c vs. correctness label (0/1) per model."""
    cfg = FigureConfig()
    models = list(confidence_scores_by_model.keys())
    n = len(models)

    fig, axes = plt.subplots(1, n, figsize=(6 * n, 5))
    if n == 1:
        axes = [axes]

    for ax, model_short in zip(axes, models):
        scores = confidence_scores_by_model[model_short]
        correctness = correctness_by_model.get(model_short, [0] * len(scores))
        ax.scatter(scores, correctness, alpha=0.1, s=10, color="steelblue")
        ax.set_xlabel("Confidence c")
        ax.set_ylabel("Correctness (0/1)")
        ax.set_title(f"{model_short}")
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["Incorrect", "Correct"])

    fig.suptitle("P(True) Confidence vs. Correctness", fontsize=12)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.dpi)
    plt.close(fig)
    logger.info(f"Fig 3 saved: {out_path}")


def plot_c_by_tier(
    confidence_by_model_tier: dict[str, dict[str, list[float]]],
    out_path: Path,
) -> None:
    """Fig 4: Box plots c by model × tier (hard vs. easy side-by-side)."""
    cfg = FigureConfig()
    models = list(confidence_by_model_tier.keys())
    n = len(models)

    fig, axes = plt.subplots(1, n, figsize=(6 * n, 5))
    if n == 1:
        axes = [axes]

    for ax, model_short in zip(axes, models):
        tier_data = confidence_by_model_tier[model_short]
        hard_scores = tier_data.get("hard", [])
        easy_scores = tier_data.get("easy", [])

        data = []
        labels = []
        if hard_scores:
            data.append(hard_scores)
            labels.append(f"Hard\n(n={len(hard_scores)})")
        if easy_scores:
            data.append(easy_scores)
            labels.append(f"Easy\n(n={len(easy_scores)})")

        if data:
            bp = ax.boxplot(data, labels=labels, patch_artist=True)
            colors_tier = ["tomato", "cornflowerblue"][:len(data)]
            for patch, color in zip(bp["boxes"], colors_tier):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

        ax.set_ylabel("Confidence c")
        ax.set_title(f"{model_short}")
        ax.set_ylim(0, 1)

    fig.suptitle("P(True) Confidence by Difficulty Tier", fontsize=12)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.dpi)
    plt.close(fig)
    logger.info(f"Fig 4 saved: {out_path}")


def plot_c_cdf(
    confidence_scores_by_model: dict[str, list[float]],
    out_path: Path,
) -> None:
    """Fig 5: CDF per model."""
    cfg = FigureConfig()
    fig, ax = plt.subplots(figsize=(8, 5))

    colors = ["steelblue", "darkorange", "green"]
    for (model_short, scores), color in zip(confidence_scores_by_model.items(), colors):
        sorted_scores = np.sort(scores)
        cdf = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores)
        ax.plot(sorted_scores, cdf, label=model_short, color=color, linewidth=2)

    ax.set_xlabel("Confidence c")
    ax.set_ylabel("CDF")
    ax.set_title("P(True) Confidence CDF per Model")
    ax.legend()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axvline(x=0.5, color="gray", linestyle="--", alpha=0.5)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.dpi)
    plt.close(fig)
    logger.info(f"Fig 5 saved: {out_path}")
