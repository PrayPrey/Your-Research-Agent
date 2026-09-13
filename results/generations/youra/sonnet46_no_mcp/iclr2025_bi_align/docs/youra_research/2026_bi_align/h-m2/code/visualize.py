"""H-M2 visualization: 6 figures for coefficient comparison and gate metrics."""
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from config import (
    CI_BAR_CAPSIZE,
    CI_BAR_LINEWIDTH,
    COLOR_EARLY,
    COLOR_LATE,
    FIGURES_DPI,
    FIGURE_SIZE_BOOT,
    FIGURE_SIZE_COEF,
    FIGURE_SIZE_GATE,
    FIGURE_SIZE_SCATTER,
    FIGURE_SIZE_STABILITY,
    FIGURE_SIZE_TOPIC,
    NON_OVERLAP_COLOR,
)
from coefficient_comparison import ComparisonResult, RoundModel

log = logging.getLogger(__name__)

FEAT_NAMES = ["β_L", "β_H", "β_S"]


def plot_coefficient_comparison(result: ComparisonResult, save_path: Path) -> None:
    """Side-by-side bar chart [β_L, β_H, β_S, β_Q] with 95% CI error bars."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_COEF)
    x = np.arange(3)
    width = 0.35

    early_err = np.array([
        result.early_coefs - result.early_ci[0],
        result.early_ci[1] - result.early_coefs,
    ])
    late_err = np.array([
        result.late_coefs - result.late_ci[0],
        result.late_ci[1] - result.late_coefs,
    ])

    bars_e = ax.bar(x - width / 2, result.early_coefs, width, label="Early (round 1)",
                    color=COLOR_EARLY, alpha=0.8,
                    yerr=early_err, capsize=CI_BAR_CAPSIZE,
                    error_kw={"elinewidth": CI_BAR_LINEWIDTH})
    bars_l = ax.bar(x + width / 2, result.late_coefs, width, label="Late (round 3)",
                    color=COLOR_LATE, alpha=0.8,
                    yerr=late_err, capsize=CI_BAR_CAPSIZE,
                    error_kw={"elinewidth": CI_BAR_LINEWIDTH})

    # Highlight non-overlapping pairs in green
    for j in range(3):
        if result.early_ci[1, j] < result.late_ci[0, j]:
            ax.axvspan(j - width, j + width, alpha=0.12, color=NON_OVERLAP_COLOR, zorder=0)

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(FEAT_NAMES)
    ax.set_ylabel("Coefficient value")
    ax.set_title("H-M2: Early vs. Late Round Stylistic Coefficients (95% Bootstrap CI)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURES_DPI, bbox_inches="tight")
    plt.close(fig)
    log.info("Figure saved: %s", save_path)


def plot_bootstrap_distributions(result: ComparisonResult, save_path: Path) -> None:
    """Overlapping histograms of bootstrap coefficient distributions."""
    fig, axes = plt.subplots(1, 3, figsize=FIGURE_SIZE_BOOT)
    for j, (ax, name) in enumerate(zip(axes, FEAT_NAMES)):
        ax.hist(result.boot_early[:, j], bins=40, alpha=0.5, color=COLOR_EARLY,
                label="Early", density=True)
        ax.hist(result.boot_late[:, j], bins=40, alpha=0.5, color=COLOR_LATE,
                label="Late", density=True)
        ax.axvline(result.early_coefs[j], color=COLOR_EARLY, linestyle="--", linewidth=1.5)
        ax.axvline(result.late_coefs[j], color=COLOR_LATE, linestyle="--", linewidth=1.5)
        ax.set_title(name)
        ax.legend(fontsize=8)
    fig.suptitle("H-M2: Bootstrap Coefficient Distributions (Early vs. Late)")
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURES_DPI, bbox_inches="tight")
    plt.close(fig)
    log.info("Figure saved: %s", save_path)


def plot_feature_stability(
    early_model: RoundModel,
    mid_model: RoundModel,
    late_model: RoundModel,
    save_path: Path,
) -> None:
    """Coefficient magnitudes across rounds 1→2→3."""
    rounds = [1, 2, 3]
    coefs_by_round = np.vstack([early_model.coefs, mid_model.coefs, late_model.coefs])  # (3, 3)

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_STABILITY)
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    for j, name in enumerate(FEAT_NAMES):
        ax.plot(rounds, coefs_by_round[:, j], marker="o", label=name, color=colors[j], linewidth=2)

    ax.axhline(0, color="black", linewidth=0.5, linestyle="--")
    ax.set_xticks(rounds)
    ax.set_xticklabels(["Round 1\n(Early)", "Round 2\n(Mid)", "Round 3\n(Late)"])
    ax.set_ylabel("Coefficient value")
    ax.set_title("H-M2: Feature Coefficient Stability Across Annotation Rounds")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURES_DPI, bbox_inches="tight")
    plt.close(fig)
    log.info("Figure saved: %s", save_path)


def plot_cross_round_scatter(
    early_scores: np.ndarray,
    late_scores: np.ndarray,
    save_path: Path,
) -> None:
    """Scatter of early vs. late model preference scores on held-out set."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SCATTER)
    ax.scatter(early_scores, late_scores, alpha=0.3, s=8, color="#555555")
    lims = [
        min(early_scores.min(), late_scores.min()) - 0.02,
        max(early_scores.max(), late_scores.max()) + 0.02,
    ]
    ax.plot(lims, lims, "r--", linewidth=1.5, label="y = x (no shift)")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Early model preference score")
    ax.set_ylabel("Late model preference score")
    ax.set_title("H-M2: Cross-Round Preference Score Comparison (Held-Out Set)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURES_DPI, bbox_inches="tight")
    plt.close(fig)
    log.info("Figure saved: %s", save_path)


def plot_topic_balance(
    chi2_residuals: np.ndarray,
    topic_labels: list,
    pvalue: float,
    save_path: Path,
) -> None:
    """Chi-square residual bar chart for early vs. late topic distribution balance."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_TOPIC)
    x = np.arange(len(topic_labels))
    colors = [NON_OVERLAP_COLOR if abs(r) < 2 else "#E74C3C" for r in chi2_residuals]
    ax.bar(x, chi2_residuals, color=colors, alpha=0.8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axhline(2, color="red", linewidth=0.8, linestyle="--", label="|residual|=2 threshold")
    ax.axhline(-2, color="red", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(topic_labels, rotation=30, ha="right")
    ax.set_ylabel("Pearson residual (late − early)")
    balance_str = "balanced" if pvalue > 0.05 else f"IMBALANCED (p={pvalue:.3f})"
    ax.set_title(f"H-M2: Topic Distribution Balance — {balance_str}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURES_DPI, bbox_inches="tight")
    plt.close(fig)
    log.info("Figure saved: %s", save_path)


def plot_gate_metrics(
    result: ComparisonResult,
    gate_status: str,
    save_path: Path,
) -> None:
    """Gate metrics summary: n_directional, β deltas vs. thresholds."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_GATE)
    x = np.arange(3)
    deltas = result.deltas
    non_overlap = [result.early_ci[1, j] < result.late_ci[0, j] for j in range(3)]
    bar_colors = [NON_OVERLAP_COLOR if no else "#E74C3C" for no in non_overlap]

    bars = ax.bar(x, deltas, color=bar_colors, alpha=0.85)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

    for bar, no in zip(bars, non_overlap):
        label = "✓ non-overlap" if no else "✗ overlap"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                label, ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(FEAT_NAMES)
    ax.set_ylabel("Coefficient delta (late − early)")
    color_map = {"PASS": NON_OVERLAP_COLOR, "PARTIAL": "#FF9800", "FAIL": "#E74C3C"}
    title_color = color_map.get(gate_status, "black")
    ax.set_title(
        f"H-M2 Gate: {gate_status} (n_directional={result.n_directional}/3, need ≥2)",
        color=title_color,
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURES_DPI, bbox_inches="tight")
    plt.close(fig)
    log.info("Figure saved: %s", save_path)
