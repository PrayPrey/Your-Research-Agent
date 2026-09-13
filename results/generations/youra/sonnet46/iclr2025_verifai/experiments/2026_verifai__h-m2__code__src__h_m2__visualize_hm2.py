"""H-M2: Visualization module — 5 figure generators."""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from h_m2.stratify import MODEL_IDS, MODEL_SHORT_NAMES, HIST_BINS, HE_PREFIX
from h_m2.analyze import HIST_BINS as ANALYZE_HIST_BINS

logger = logging.getLogger(__name__)

# ─── Configuration ────────────────────────────────────────────────────────────

FIG_DPI: int = 150
TIER_COLORS: dict[str, str] = {"hard": "red", "medium": "gray", "easy": "green"}
JACCARD_THRESHOLD_COLOR: str = "red"
JACCARD_THRESHOLD_STYLE: str = "--"
JACCARD_HEATMAP_CMAP: str = "Blues"
HIST_FIGURE_SIZE: tuple[int, int] = (18, 8)

FIG_FILENAMES: dict[str, str] = {
    "jaccard_bars": "jaccard_similarity_bars.png",
    "histograms": "pass_at_1_histograms.png",
    "tier_summary": "tier_size_summary.png",
    "heatmap": "jaccard_heatmap.png",
    "consensus_pie": "consensus_hard_pie.png",
}

SHORT_LABELS = {
    "NousResearch/Meta-Llama-3-8B": "Llama3-8B",
    "codellama/CodeLlama-7b-hf": "CodeLlama-7B",
    "deepseek-ai/deepseek-coder-6.7b-base": "DeepSeek-6.7B",
}


def _pair_label(a: str, b: str) -> str:
    return f"{SHORT_LABELS.get(a, a)}\nvs\n{SHORT_LABELS.get(b, b)}"


def plot_jaccard_bars(
    jaccard_results: dict[tuple[str, str], float],
    output_path: str | Path,
    threshold: float = 0.3,
) -> None:
    """Bar chart: 3 model pairs × Jaccard score + dashed threshold line."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pairs = sorted(jaccard_results.keys())
    labels = [_pair_label(a, b) for (a, b) in pairs]
    values = [jaccard_results[(a, b)] for (a, b) in pairs]
    colors = ["steelblue" if v > threshold else "salmon" for v in values]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=FIG_DPI)
    bars = ax.bar(range(len(pairs)), values, color=colors, edgecolor="black", linewidth=0.8)
    ax.axhline(y=threshold, color=JACCARD_THRESHOLD_COLOR,
               linestyle=JACCARD_THRESHOLD_STYLE, linewidth=2,
               label=f"Gate threshold ({threshold})")
    ax.set_xticks(range(len(pairs)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Jaccard Similarity")
    ax.set_title("Cross-Model Jaccard Similarity (Hard Tier)")
    ax.set_ylim(0, max(1.0, max(values) * 1.2))
    ax.legend()

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)
    logger.info("Saved jaccard bars figure: %s", output_path)


def plot_pass_at_1_histograms(
    pass_at_1_data: dict[str, dict[str, float]],
    output_path: str | Path,
) -> None:
    """3×2 subplot grid: 3 models × 2 benchmarks, 6-point bins, tier-colored bars."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model_ids = MODEL_IDS
    benchmarks = ["humaneval", "mbpp"]
    bench_labels = {"humaneval": "HumanEval+", "mbpp": "MBPP+"}

    fig, axes = plt.subplots(len(model_ids), len(benchmarks),
                              figsize=HIST_FIGURE_SIZE, dpi=FIG_DPI)

    for i, model_id in enumerate(model_ids):
        task_scores = pass_at_1_data.get(model_id, {})
        he_scores: dict[str, float] = {}
        mbpp_scores: dict[str, float] = {}
        for tid, v in task_scores.items():
            if tid.startswith(HE_PREFIX):
                he_scores[tid] = v
            else:
                mbpp_scores[tid] = v

        split_data = {"humaneval": he_scores, "mbpp": mbpp_scores}

        for j, bench in enumerate(benchmarks):
            ax = axes[i][j]
            scores = list(split_data[bench].values())
            arr = np.array(scores, dtype=float)

            bin_counts = [int(np.sum(np.isclose(arr, b))) for b in HIST_BINS]
            bar_colors = []
            for b in HIST_BINS:
                if b == 0.0:
                    bar_colors.append(TIER_COLORS["hard"])
                elif b >= 0.6:
                    bar_colors.append(TIER_COLORS["easy"])
                else:
                    bar_colors.append(TIER_COLORS["medium"])

            ax.bar([str(b) for b in HIST_BINS], bin_counts,
                   color=bar_colors, edgecolor="black", linewidth=0.5)
            ax.set_title(f"{SHORT_LABELS.get(model_id, model_id)}\n{bench_labels[bench]}",
                         fontsize=8)
            ax.set_xlabel("pass@1")
            ax.set_ylabel("Count")
            ax.tick_params(axis="x", labelsize=7)

    plt.suptitle("Pass@1 Histograms by Model and Benchmark", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)
    logger.info("Saved histogram figure: %s", output_path)


def plot_tier_size_summary(
    per_benchmark_tiers: dict[str, dict[str, dict[str, set]]],
    output_path: str | Path,
) -> None:
    """Stacked bar chart: hard/medium/easy counts per model per benchmark."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model_ids = MODEL_IDS
    benchmarks = ["humaneval", "mbpp"]
    labels = [f"{SHORT_LABELS.get(m, m)}\n{b}" for m in model_ids for b in benchmarks]
    hard_counts, medium_counts, easy_counts = [], [], []

    for model_id in model_ids:
        for bench in benchmarks:
            t = per_benchmark_tiers.get(model_id, {}).get(bench, {})
            hard_counts.append(len(t.get("hard", set())))
            medium_counts.append(len(t.get("medium", set())))
            easy_counts.append(len(t.get("easy", set())))

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(12, 5), dpi=FIG_DPI)

    b1 = ax.bar(x, hard_counts, label="Hard", color=TIER_COLORS["hard"], edgecolor="black")
    b2 = ax.bar(x, medium_counts, bottom=hard_counts, label="Medium",
                color=TIER_COLORS["medium"], edgecolor="black")
    b3 = ax.bar(x, easy_counts,
                bottom=[h + m for h, m in zip(hard_counts, medium_counts)],
                label="Easy", color=TIER_COLORS["easy"], edgecolor="black")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("Problem Count")
    ax.set_title("Tier Size Summary per Model per Benchmark")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)
    logger.info("Saved tier summary figure: %s", output_path)


def plot_jaccard_heatmap(
    jaccard_results: dict[tuple[str, str], float],
    output_path: str | Path,
) -> None:
    """3×3 symmetric Jaccard matrix heatmap (Blues colormap)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model_ids = sorted(set(m for pair in jaccard_results for m in pair))
    n = len(model_ids)
    idx = {m: i for i, m in enumerate(model_ids)}

    matrix = np.zeros((n, n))
    for i in range(n):
        matrix[i][i] = 1.0  # diagonal
    for (a, b), j in jaccard_results.items():
        i, k = idx[a], idx[b]
        matrix[i][k] = j
        matrix[k][i] = j

    short_labels = [SHORT_LABELS.get(m, m) for m in model_ids]

    fig, ax = plt.subplots(figsize=(6, 5), dpi=FIG_DPI)
    im = ax.imshow(matrix, cmap=JACCARD_HEATMAP_CMAP, vmin=0, vmax=1)
    plt.colorbar(im, ax=ax)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(short_labels, fontsize=7, rotation=15, ha="right")
    ax.set_yticklabels(short_labels, fontsize=7)
    ax.set_title("Jaccard Similarity Heatmap (Hard Tier)")

    for i in range(n):
        for k in range(n):
            ax.text(k, i, f"{matrix[i][k]:.2f}", ha="center", va="center", fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)
    logger.info("Saved heatmap figure: %s", output_path)


def plot_consensus_hard_pie(
    overlap_counts: dict[int, int],
    output_path: str | Path,
) -> None:
    """Pie chart: problems hard for 1/3, 2/3, 3/3 models."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    labels = ["1/3 models", "2/3 models", "3/3 models"]
    sizes = [overlap_counts.get(1, 0), overlap_counts.get(2, 0), overlap_counts.get(3, 0)]
    colors = ["#ffcccc", "#ff6666", "#cc0000"]

    # Filter zero-size slices
    non_zero = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
    if not non_zero:
        logger.warning("No overlap data to plot for consensus pie")
        return

    labels, sizes, colors = zip(*non_zero)

    fig, ax = plt.subplots(figsize=(6, 5), dpi=FIG_DPI)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=90
    )
    ax.set_title("Problems Hard for N/3 Models (Hard Tier Consensus)")

    plt.tight_layout()
    plt.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)
    logger.info("Saved consensus pie figure: %s", output_path)
