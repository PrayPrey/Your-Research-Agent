"""H-M1: Visualization module for coverage and pass@1 distribution figures."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend (match h-e1 pattern)
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)

# ─── Constants: Figure Configuration (C-A7-1) ─────────────────────────────────

FIG_DPI: int = 150
COVERAGE_THRESHOLD: float = 0.95

# Coverage heatmap colormap
HEATMAP_CMAP: str = "RdYlGn"
HEATMAP_VMIN: float = 0.0
HEATMAP_VMAX: float = 1.0

# Coverage bar chart threshold line
THRESHOLD_LINE_COLOR: str = "red"
THRESHOLD_LINE_STYLE: str = "--"
THRESHOLD_LINE_WIDTH: float = 1.5

# Subplot layout for 3-model histogram figure
HIST_FIGURE_SIZE: tuple = (15, 5)
HIST_N_COLS: int = 3
HIST_N_ROWS: int = 1

# ─── Constants: Histogram/CDF Parameters (C-A7-2) ─────────────────────────────

PASS_AT_1_BINS: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
PASS_AT_1_BIN_LABELS: list[str] = ["0.0", "0.2", "0.4", "0.6", "0.8", "1.0"]

# Side-by-side bar colors (HumanEval+ vs MBPP+)
BAR_COLOR_HE: str = "steelblue"
BAR_COLOR_MBPP: str = "darkorange"
BAR_WIDTH: float = 0.35

# CDF plot styling (3 models overlaid)
CDF_LINESTYLES: list[str] = ["-", "--", "-."]
CDF_ALPHA: float = 0.85
CDF_LEGEND_LOC: str = "lower right"

# Figure size for CDF
CDF_FIGURE_SIZE: tuple = (8, 5)


# ─── Helper: short model labels ───────────────────────────────────────────────

def _short_label(model_short: str) -> str:
    """Return concise label for plot axes."""
    labels = {
        "llama3_8b": "Llama3-8B",
        "codellama_7b": "CodeLlama-7B",
        "deepseek_6.7b": "DeepSeek-6.7B",
    }
    return labels.get(model_short, model_short)


# ─── Coverage rate bar chart ──────────────────────────────────────────────────

def plot_coverage_rates(
    coverage_data: dict,
    output_path: str,
) -> None:
    """Bar chart of coverage per model × benchmark with red dashed threshold line.

    Args:
        coverage_data: {model_short: {"humaneval": float, "mbpp": float, "combined": float}}
        output_path: path to save PNG
    """
    model_shorts = list(coverage_data.keys())
    n_models = len(model_shorts)
    benchmarks = ["humaneval", "mbpp", "combined"]
    colors = ["steelblue", "darkorange", "forestgreen"]

    x = np.arange(n_models)
    bar_w = 0.25

    fig, ax = plt.subplots(figsize=(10, 5), dpi=FIG_DPI)

    for i, (bench, color) in enumerate(zip(benchmarks, colors)):
        vals = [coverage_data[m].get(bench, 0.0) for m in model_shorts]
        ax.bar(x + i * bar_w, vals, bar_w, label=bench.capitalize(), color=color, alpha=0.8)

    # Red dashed threshold line at 0.95
    ax.axhline(
        COVERAGE_THRESHOLD,
        color=THRESHOLD_LINE_COLOR,
        linestyle=THRESHOLD_LINE_STYLE,
        linewidth=THRESHOLD_LINE_WIDTH,
        label=f"Gate ({COVERAGE_THRESHOLD:.0%})",
    )

    ax.set_xticks(x + bar_w)
    ax.set_xticklabels([_short_label(m) for m in model_shorts])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Coverage Rate")
    ax.set_title("H-M1: Pass@1 Coverage Rates per Model & Benchmark")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved coverage_rates.png → {output_path}")


# ─── Coverage heatmap ─────────────────────────────────────────────────────────

def plot_coverage_heatmap(
    coverage_data: dict,
    output_path: str,
) -> None:
    """3×2 heatmap (models × benchmarks) color-coded by coverage fraction.

    Args:
        coverage_data: {model_short: {"humaneval": float, "mbpp": float, "combined": float}}
        output_path: path to save PNG
    """
    model_shorts = list(coverage_data.keys())
    benchmarks = ["humaneval", "mbpp", "combined"]

    # Build 2D matrix: rows=models, cols=benchmarks
    matrix = np.array([
        [coverage_data[m].get(b, 0.0) for b in benchmarks]
        for m in model_shorts
    ])

    fig, ax = plt.subplots(figsize=(7, 4), dpi=FIG_DPI)
    im = ax.imshow(
        matrix,
        cmap=HEATMAP_CMAP,
        vmin=HEATMAP_VMIN,
        vmax=HEATMAP_VMAX,
        aspect="auto",
    )
    plt.colorbar(im, ax=ax, label="Coverage Rate")

    ax.set_xticks(range(len(benchmarks)))
    ax.set_xticklabels([b.capitalize() for b in benchmarks])
    ax.set_yticks(range(len(model_shorts)))
    ax.set_yticklabels([_short_label(m) for m in model_shorts])
    ax.set_title("H-M1: Coverage Rate Heatmap")

    # Annotate cells with values
    for i in range(len(model_shorts)):
        for j in range(len(benchmarks)):
            ax.text(j, i, f"{matrix[i, j]:.3f}", ha="center", va="center",
                    color="black", fontsize=9)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved coverage_heatmap.png → {output_path}")


# ─── Pass@1 histograms ────────────────────────────────────────────────────────

def plot_pass_at_1_histograms(
    pass_at_1_by_model: dict[str, dict],
    output_path: str,
) -> None:
    """3-subplot figure: 6-point histogram per model, HumanEval+ vs MBPP+ side-by-side.

    Args:
        pass_at_1_by_model: {model_short: {task_id: float}}
        output_path: path to save PNG
    """
    model_shorts = list(pass_at_1_by_model.keys())
    n_models = len(model_shorts)

    fig, axes = plt.subplots(
        HIST_N_ROWS, max(HIST_N_COLS, n_models), figsize=HIST_FIGURE_SIZE, dpi=FIG_DPI
    )
    if n_models == 1:
        axes = [axes]
    elif HIST_N_ROWS == 1:
        axes = list(axes)

    bin_positions = np.arange(len(PASS_AT_1_BINS))

    for idx, model_short in enumerate(model_shorts):
        ax = axes[idx]
        p1 = pass_at_1_by_model[model_short]

        # Split by benchmark
        he_vals = [v for k, v in p1.items() if k.startswith("HumanEval/")]
        mbpp_vals = [v for k, v in p1.items() if k.startswith("Mbpp/")]

        def count_bins(vals):
            arr = np.array(vals, dtype=float) if vals else np.array([], dtype=float)
            return [int(np.sum(np.isclose(arr, b))) for b in PASS_AT_1_BINS]

        he_counts = count_bins(he_vals)
        mbpp_counts = count_bins(mbpp_vals)

        ax.bar(bin_positions - BAR_WIDTH / 2, he_counts, BAR_WIDTH,
               label="HumanEval+", color=BAR_COLOR_HE, alpha=0.8)
        ax.bar(bin_positions + BAR_WIDTH / 2, mbpp_counts, BAR_WIDTH,
               label="MBPP+", color=BAR_COLOR_MBPP, alpha=0.8)

        ax.set_xticks(bin_positions)
        ax.set_xticklabels(PASS_AT_1_BIN_LABELS)
        ax.set_xlabel("Pass@1 Value")
        ax.set_ylabel("Problem Count")
        ax.set_title(f"{_short_label(model_short)}")
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)

    # Hide unused subplots
    for idx in range(n_models, len(axes)):
        axes[idx].set_visible(False)

    fig.suptitle("H-M1: Pass@1 Distribution (6-bin Histogram)", fontsize=12)
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved pass_at_1_histograms.png → {output_path}")


# ─── Pass@1 CDF ───────────────────────────────────────────────────────────────

def plot_pass_at_1_cdf(
    pass_at_1_by_model: dict[str, dict],
    output_path: str,
) -> None:
    """CDF per model × benchmark overlaid. Shows bimodal hard/easy structure.

    Args:
        pass_at_1_by_model: {model_short: {task_id: float}}
        output_path: path to save PNG
    """
    model_shorts = list(pass_at_1_by_model.keys())
    benchmarks = [("HumanEval/", "HE+"), ("Mbpp/", "MBPP+")]

    fig, ax = plt.subplots(figsize=CDF_FIGURE_SIZE, dpi=FIG_DPI)

    for model_idx, model_short in enumerate(model_shorts):
        p1 = pass_at_1_by_model[model_short]
        linestyle = CDF_LINESTYLES[model_idx % len(CDF_LINESTYLES)]
        label_base = _short_label(model_short)

        for prefix, bench_label in benchmarks:
            vals = sorted(v for k, v in p1.items() if k.startswith(prefix))
            if not vals:
                continue
            n = len(vals)
            x = vals
            y = np.arange(1, n + 1) / n
            ax.plot(x, y, linestyle=linestyle, alpha=CDF_ALPHA,
                    label=f"{label_base} ({bench_label})")

    ax.set_xlabel("Pass@1 Value")
    ax.set_ylabel("Cumulative Fraction")
    ax.set_title("H-M1: Pass@1 CDF per Model & Benchmark")
    ax.legend(loc=CDF_LEGEND_LOC, fontsize=7)
    ax.grid(alpha=0.3)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved pass_at_1_cdf.png → {output_path}")
