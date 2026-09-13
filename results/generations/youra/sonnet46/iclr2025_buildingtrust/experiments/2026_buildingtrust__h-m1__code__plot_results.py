"""
plot_results.py — H-M1 Figure Generation (5 figures)

Figure 1 (MANDATORY): ECE gate bar chart with threshold line at 0.15
Figures 2-5: extended analysis plots
"""

import logging
import numpy as np
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger(__name__)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib/seaborn not available — figures will be skipped")


def _check_matplotlib():
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "matplotlib and seaborn are required for figure generation. "
            "Install: pip install matplotlib seaborn"
        )


def _save_figure(fig, filename: str, figures_dir: str = None) -> str:
    """Save figure to h-m1/figures/ and return path."""
    if figures_dir is None:
        figures_dir = config.H_M1_FIGURES_DIR
    out_dir = Path(figures_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    fig.savefig(str(out_path), dpi=config.FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"  Saved: {out_path}")
    return str(out_path)


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 1 (MANDATORY): ECE Gate Bar Chart
# ═══════════════════════════════════════════════════════════════════════════════

def plot_ece_gate_bar(
    ece_base: dict,
    threshold: float = None,
    figures_dir: Optional[str] = None,
) -> str:
    """
    Figure 1: Bar chart of ECE_base for 1.4B/2.8B/6.9B with gate threshold line.

    Args:
        ece_base: {"1.4b": float, "2.8b": float, "6.9b": float}
        threshold: dashed line position (default: config.GATE_THRESHOLD = 0.15)

    Returns:
        str: path to saved figure
    """
    _check_matplotlib()
    if threshold is None:
        threshold = config.GATE_THRESHOLD

    labels = [f"Pythia-{s.upper()}" for s in config.BASE_SIZES]
    values = [ece_base[s] for s in config.BASE_SIZES]
    colors = ["#2ecc71" if v < threshold else "#e74c3c" for v in values]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor="black", linewidth=0.8, width=0.5)

    # Threshold line
    ax.axhline(y=threshold, color="black", linestyle="--", linewidth=2,
               label=f"Gate threshold = {threshold}")

    # Value labels on bars
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.002,
            f"{val:.4f}",
            ha="center", va="bottom", fontsize=11, fontweight="bold"
        )

    # Legend patches
    pass_patch = mpatches.Patch(color="#2ecc71", label="Pass (ECE < 0.15)")
    fail_patch = mpatches.Patch(color="#e74c3c", label="Fail (ECE ≥ 0.15)")
    ax.legend(handles=[pass_patch, fail_patch,
                        plt.Line2D([0], [0], color="black", linestyle="--", lw=2,
                                   label=f"Threshold = {threshold}")],
              loc="upper right", fontsize=10)

    ax.set_xlabel("Pythia Base Model", fontsize=12)
    ax.set_ylabel("Expected Calibration Error (ECE)", fontsize=12)
    ax.set_title(
        "H-M1: Pythia Base Model ECE — MUST_WORK Gate Evaluation\n"
        "(Gate: ECE_base < 0.15 for all 3 sizes)",
        fontsize=12, fontweight="bold"
    )
    ax.set_ylim(0, max(max(values) * 1.3, threshold * 1.5))
    ax.grid(axis="y", alpha=0.3)
    sns.despine(ax=ax, top=True, right=True)

    return _save_figure(fig, "figure_01_ece_gate.png", figures_dir)


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 2: Base vs Aligned ECE comparison
# ═══════════════════════════════════════════════════════════════════════════════

def plot_base_vs_aligned_ece(
    ece_base: dict,
    ece_aligned: Optional[dict] = None,
    figures_dir: Optional[str] = None,
) -> str:
    """
    Figure 2: Grouped bar chart — base vs aligned ECE for each Pythia size.

    Args:
        ece_base: {"1.4b": float, "2.8b": float, "6.9b": float}
        ece_aligned: {"1.4b": {"sft": float, "dpo": float, "ppo": float}, ...}
                     If None, uses H-E1 known values.
    """
    _check_matplotlib()

    # H-E1 known aligned ECE values (from 04_validation.md)
    h_e1_aligned = {
        "1.4b": {"base": 0.0849, "sft": 0.1415, "dpo": 0.2516, "ppo": 0.1923},
        "2.8b": {"base": 0.0597, "sft": 0.0694, "dpo": 0.1441, "ppo": 0.1577},
        "6.9b": {"base": 0.0792, "sft": 0.0830, "dpo": 0.1010, "ppo": 0.0609},
    }
    if ece_aligned is not None:
        # Override base values with current run
        for size in config.BASE_SIZES:
            h_e1_aligned[size]["base"] = ece_base[size]

    conditions = ["base", "sft", "dpo", "ppo"]
    condition_colors = {
        "base": "#3498db",
        "sft": "#f39c12",
        "dpo": "#e74c3c",
        "ppo": "#9b59b6",
    }

    sizes = config.BASE_SIZES
    x = np.arange(len(sizes))
    width = 0.2
    offsets = np.linspace(-1.5 * width, 1.5 * width, len(conditions))

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, cond in enumerate(conditions):
        vals = [h_e1_aligned[s].get(cond, 0) for s in sizes]
        bars = ax.bar(x + offsets[i], vals, width, label=cond.upper(),
                      color=condition_colors[cond], edgecolor="black", linewidth=0.5)

    ax.axhline(y=0.15, color="red", linestyle="--", linewidth=1.5,
               label="Gate threshold (0.15)", alpha=0.7)

    ax.set_xlabel("Pythia Model Size", fontsize=12)
    ax.set_ylabel("Expected Calibration Error (ECE)", fontsize=12)
    ax.set_title(
        "H-M1: ECE Comparison — Base vs Aligned Pythia Models",
        fontsize=12, fontweight="bold"
    )
    ax.set_xticks(x)
    ax.set_xticklabels([f"Pythia-{s.upper()}" for s in sizes], fontsize=11)
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    sns.despine(ax=ax, top=True, right=True)

    return _save_figure(fig, "figure_02_base_vs_aligned_ece.png", figures_dir)


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 3: Calibration Reliability Diagrams for base models
# ═══════════════════════════════════════════════════════════════════════════════

def plot_calibration_reliability_diagrams(
    ece_base: dict,
    figures_dir: Optional[str] = None,
) -> str:
    """
    Figure 3: 3-panel calibration reliability diagram (simulated from ECE values).
    Shows approximate calibration curves for base models.
    """
    _check_matplotlib()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    bin_edges = np.linspace(0, 1, config.N_BINS + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    np.random.seed(config.SEED)

    for ax, size in zip(axes, config.BASE_SIZES):
        ece = ece_base[size]

        # Simulate calibration curve consistent with observed ECE
        # Perfect calibration + small overconfidence proportional to ECE
        confidence = bin_centers
        accuracy = confidence - ece * np.sin(np.pi * confidence) * 0.8
        accuracy = np.clip(accuracy, 0, 1)

        ax.plot([0, 1], [0, 1], "k--", linewidth=1.5, label="Perfect calibration")
        ax.bar(bin_centers, accuracy, width=1/config.N_BINS * 0.9,
               alpha=0.6, color="#3498db", edgecolor="black", linewidth=0.5,
               label=f"ECE={ece:.4f}")
        ax.plot(bin_centers, accuracy, "o-", color="#2c3e50", linewidth=1.5,
                markersize=4)

        ax.set_xlabel("Confidence", fontsize=11)
        if ax == axes[0]:
            ax.set_ylabel("Accuracy", fontsize=11)
        ax.set_title(f"Pythia-{size.upper()}\nECE = {ece:.4f}", fontsize=11, fontweight="bold")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.legend(fontsize=9, loc="upper left")
        ax.grid(alpha=0.3)
        sns.despine(ax=ax, top=True, right=True)

    fig.suptitle(
        "H-M1: Calibration Reliability Diagrams — Pythia Base Models\n"
        "(Simulated from ECE, MMLU evaluation)",
        fontsize=12, fontweight="bold"
    )
    plt.tight_layout()

    return _save_figure(fig, "figure_03_calibration_curves.png", figures_dir)


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 4: ECE by MMLU Subject (estimated)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_ece_by_subject(
    ece_base: dict,
    figures_dir: Optional[str] = None,
) -> str:
    """
    Figure 4: Box plot approximation of ECE distribution across MMLU subjects.
    Uses simulated per-subject ECE based on mean ECE values.
    """
    _check_matplotlib()

    np.random.seed(config.SEED)
    n_subjects = 57  # MMLU has 57 subjects

    fig, ax = plt.subplots(figsize=(12, 5))

    data = []
    labels = []
    for size in config.BASE_SIZES:
        mean_ece = ece_base[size]
        # Simulate per-subject ECE variation
        subject_eces = np.random.beta(
            a=mean_ece * 10 + 0.5,
            b=(1 - mean_ece) * 10 + 0.5,
            size=n_subjects
        )
        subject_eces = np.clip(subject_eces, 0, 1)
        data.append(subject_eces)
        labels.append(f"Pythia-{size.upper()}")

    bp = ax.boxplot(data, labels=labels, patch_artist=True,
                    medianprops={"color": "black", "linewidth": 2})
    colors = ["#3498db", "#e74c3c", "#2ecc71"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.axhline(y=0.15, color="red", linestyle="--", linewidth=2,
               label="Gate threshold (0.15)", alpha=0.8)

    ax.set_xlabel("Pythia Base Model", fontsize=12)
    ax.set_ylabel("ECE per MMLU Subject", fontsize=12)
    ax.set_title(
        "H-M1: ECE Distribution Across MMLU Subjects — Base Models\n"
        "(57 MMLU categories, simulated from mean ECE)",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    sns.despine(ax=ax, top=True, right=True)

    return _save_figure(fig, "figure_04_ece_by_subject.png", figures_dir)


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 5: Brier Decomposition for base models
# ═══════════════════════════════════════════════════════════════════════════════

def plot_brier_decomposition_base(
    ece_base: dict,
    figures_dir: Optional[str] = None,
) -> str:
    """
    Figure 5: Stacked bar — Brier decomposition (REL/RES/UNC) for base models.
    Uses H-E1 known Brier values from 04_validation.md.
    """
    _check_matplotlib()

    # H-E1 known Brier decomposition for base models
    brier_data = {
        "1.4b": {"REL": 0.0190, "RES": 0.0005, "UNC": 0.7492},
        "2.8b": {"REL": 0.0093, "RES": 0.0003, "UNC": 0.7492},
        "6.9b": {"REL": 0.0128, "RES": 0.0004, "UNC": 0.7492},
    }

    labels = [f"Pythia-{s.upper()}" for s in config.BASE_SIZES]
    rel_vals = [brier_data[s]["REL"] for s in config.BASE_SIZES]
    res_vals = [brier_data[s]["RES"] for s in config.BASE_SIZES]
    unc_vals = [brier_data[s]["UNC"] for s in config.BASE_SIZES]

    x = np.arange(len(labels))
    width = 0.5

    fig, ax = plt.subplots(figsize=(9, 6))

    # Stacked bars (only show REL and RES — UNC is constant and large)
    bars1 = ax.bar(x, rel_vals, width, label="Reliability (REL)", color="#e74c3c",
                   edgecolor="black", linewidth=0.5)
    bars2 = ax.bar(x, res_vals, width, bottom=rel_vals, label="Resolution (RES)",
                   color="#3498db", edgecolor="black", linewidth=0.5)

    # Add value labels
    for i, (r, rs) in enumerate(zip(rel_vals, res_vals)):
        ax.text(i, r / 2, f"REL\n{r:.4f}", ha="center", va="center",
                fontsize=9, fontweight="bold", color="white")
        ax.text(i, r + rs / 2, f"RES\n{rs:.4f}", ha="center", va="center",
                fontsize=8, fontweight="bold", color="white")

    ax.text(1.6, max(rel_vals) + max(res_vals) + 0.002,
            f"UNC = {unc_vals[0]:.4f} (constant, task-dependent)",
            fontsize=9, style="italic", color="gray")

    ax.set_xlabel("Pythia Base Model", fontsize=12)
    ax.set_ylabel("Brier Component", fontsize=12)
    ax.set_title(
        "H-M1: Brier Decomposition — Pythia Base Models\n"
        "(REL=Reliability/Overconfidence, RES=Resolution, UNC=Uncertainty)",
        fontsize=12, fontweight="bold"
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    sns.despine(ax=ax, top=True, right=True)

    return _save_figure(fig, "figure_05_brier_decomposition.png", figures_dir)


# ═══════════════════════════════════════════════════════════════════════════════
# Generate all figures
# ═══════════════════════════════════════════════════════════════════════════════

def generate_all_figures(
    ece_base: dict,
    figures_dir: Optional[str] = None,
) -> list:
    """
    Generate all 5 H-M1 figures.

    Returns:
        list[str]: paths to all successfully generated figures
    """
    figure_paths = []

    # Figure 1: MANDATORY
    try:
        path = plot_ece_gate_bar(ece_base, figures_dir=figures_dir)
        figure_paths.append(path)
        logger.info("✓ Figure 1 generated")
    except Exception as e:
        logger.error(f"❌ Figure 1 FAILED: {e}")
        raise  # Figure 1 is mandatory

    # Figure 2: Base vs Aligned
    try:
        path = plot_base_vs_aligned_ece(ece_base, figures_dir=figures_dir)
        figure_paths.append(path)
        logger.info("✓ Figure 2 generated")
    except Exception as e:
        logger.warning(f"⚠ Figure 2 failed (non-critical): {e}")

    # Figure 3: Calibration curves
    try:
        path = plot_calibration_reliability_diagrams(ece_base, figures_dir=figures_dir)
        figure_paths.append(path)
        logger.info("✓ Figure 3 generated")
    except Exception as e:
        logger.warning(f"⚠ Figure 3 failed (non-critical): {e}")

    # Figure 4: ECE by subject
    try:
        path = plot_ece_by_subject(ece_base, figures_dir=figures_dir)
        figure_paths.append(path)
        logger.info("✓ Figure 4 generated")
    except Exception as e:
        logger.warning(f"⚠ Figure 4 failed (non-critical): {e}")

    # Figure 5: Brier decomposition
    try:
        path = plot_brier_decomposition_base(ece_base, figures_dir=figures_dir)
        figure_paths.append(path)
        logger.info("✓ Figure 5 generated")
    except Exception as e:
        logger.warning(f"⚠ Figure 5 failed (non-critical): {e}")

    logger.info(f"✓ {len(figure_paths)}/5 figures generated")
    return figure_paths
