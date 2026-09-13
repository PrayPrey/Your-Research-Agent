"""Visualization functions for H-E1 audit results."""
from pathlib import Path
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from .config import FIGURES_DIR, N_COMMON_GATE


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def plot_gate_metrics(pair_counts: dict[str, int], out_path: Path | None = None) -> None:
    """MANDATORY: bar chart N_BBQ/N_GLUE/N_ANLI, dashed line at 10, PASS/FAIL annotations."""
    if out_path is None:
        out_path = FIGURES_DIR / "gate_metrics.png"
    _ensure_dir(out_path)

    labels = list(pair_counts.keys())
    values = list(pair_counts.values())
    colors = ["#2ecc71" if v >= N_COMMON_GATE else "#e74c3c" for v in values]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor="black", linewidth=0.8)
    ax.axhline(N_COMMON_GATE, color="black", linestyle="--", linewidth=1.5, label=f"Gate N={N_COMMON_GATE}")

    for bar, val in zip(bars, values):
        label = f"PASS (N={val})" if val >= N_COMMON_GATE else f"FAIL (N={val})"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            label,
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_ylabel("Number of models with both scores")
    ax.set_title("H-E1 Gate Metrics: Model Coverage per Benchmark Pair")
    ax.legend()
    ax.set_ylim(0, max(max(values, default=0) + 4, N_COMMON_GATE + 4))
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    logging.info(f"Saved gate_metrics.png to {out_path}")


def plot_coverage_heatmap(matrix: pd.DataFrame, out_path: Path | None = None) -> None:
    """Model × 7-benchmark heatmap; score color, white=NaN."""
    if out_path is None:
        out_path = FIGURES_DIR / "coverage_heatmap.png"
    _ensure_dir(out_path)

    try:
        import seaborn as sns
    except ImportError:
        logging.warning("seaborn not available; skipping coverage heatmap")
        return

    fig, ax = plt.subplots(figsize=(12, max(6, len(matrix) * 0.4 + 2)))
    mask = matrix.isna()
    sns.heatmap(
        matrix.astype(float),
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="YlOrRd",
        vmin=0.0,
        vmax=1.0,
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Score (0-1)"},
    )
    ax.set_title("Model × Benchmark Score Coverage")
    ax.set_xlabel("Benchmark")
    ax.set_ylabel("Model")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logging.info(f"Saved coverage_heatmap.png to {out_path}")


def plot_source_attribution(attribution: pd.DataFrame, out_path: Path | None = None) -> None:
    """Stacked bar: fraction of cells per source per benchmark column."""
    if out_path is None:
        out_path = FIGURES_DIR / "source_attribution.png"
    _ensure_dir(out_path)

    sources = ["TrustLLM", "DecodingTrust", "GLUE-X", "OOD_NLP", "HF"]
    colors = ["#3498db", "#9b59b6", "#e67e22", "#1abc9c", "#e74c3c"]
    cols = attribution.columns.tolist()

    fractions = {src: [] for src in sources}
    fractions["Missing"] = []
    colors.append("#bdc3c7")

    for col in cols:
        col_data = attribution[col]
        total = len(col_data)
        for src in sources:
            fractions[src].append((col_data == src).sum() / total)
        fractions["Missing"].append(col_data.isna().sum() / total)

    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = np.zeros(len(cols))
    for src, color in zip(list(fractions.keys()), colors):
        vals = np.array(fractions[src])
        ax.bar(cols, vals, bottom=bottom, label=src, color=color)
        bottom += vals

    ax.set_ylabel("Fraction of cells")
    ax.set_title("Score Source Attribution per Benchmark")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    logging.info(f"Saved source_attribution.png to {out_path}")


def plot_protocol_consistency(
    score_dicts: dict,
    warnings: list[dict],
    out_path: Path | None = None,
) -> None:
    """Scatter: source-A score vs source-B score for shared model-benchmark pairs."""
    if out_path is None:
        out_path = FIGURES_DIR / "protocol_consistency.png"
    _ensure_dir(out_path)

    # Collect all cross-source pairs
    points = []
    sources = list(score_dicts.keys())
    for i, src_a in enumerate(sources):
        for src_b in sources[i + 1 :]:
            models_a = set(score_dicts[src_a].keys())
            models_b = set(score_dicts[src_b].keys())
            for model in models_a & models_b:
                benchmarks_a = set(score_dicts[src_a][model].keys())
                benchmarks_b = set(score_dicts[src_b][model].keys())
                for bench in benchmarks_a & benchmarks_b:
                    va = score_dicts[src_a][model][bench]
                    vb = score_dicts[src_b][model][bench]
                    points.append((va, vb, f"{src_a} vs {src_b}", bench))

    if not points:
        # No cross-source pairs; save placeholder
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.text(0.5, 0.5, "No cross-source pairs to compare", ha="center", va="center",
                transform=ax.transAxes, fontsize=12, color="gray")
        ax.set_title("Protocol Consistency (no data)")
        plt.tight_layout()
        plt.savefig(out_path, dpi=150)
        plt.close(fig)
        logging.info(f"Saved protocol_consistency.png (no data) to {out_path}")
        return

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    warn_set = {(w["model"], w["benchmark"]) for w in warnings}

    fig, ax = plt.subplots(figsize=(7, 6))
    colors = ["#e74c3c" if (p[3],) in [(w["benchmark"],) for w in warnings] else "#3498db" for p in points]
    ax.scatter(xs, ys, c=colors, alpha=0.7, edgecolors="black", linewidths=0.4)

    lim_min = min(min(xs), min(ys)) - 0.05
    lim_max = max(max(xs), max(ys)) + 0.05
    ax.plot([lim_min, lim_max], [lim_min, lim_max], "k--", linewidth=1, label="y=x (perfect agreement)")
    ax.set_xlabel("Source A score")
    ax.set_ylabel("Source B score")
    ax.set_title("Protocol Consistency: Cross-Source Score Comparison")
    ax.legend(fontsize=8)
    red_patch = mpatches.Patch(color="#e74c3c", label=f"Flagged (>5pp delta, n={len(warnings)})")
    blue_patch = mpatches.Patch(color="#3498db", label="Within threshold")
    ax.legend(handles=[red_patch, blue_patch], fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    logging.info(f"Saved protocol_consistency.png to {out_path}")
