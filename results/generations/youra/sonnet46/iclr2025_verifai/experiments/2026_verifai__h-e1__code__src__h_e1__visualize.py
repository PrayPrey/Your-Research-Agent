"""Visualization for H-E1: 4 required figures."""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import numpy as np

# Figure settings
FIG_DPI = 150
FIG_SIZE_BAR = (10, 5)
FIG_SIZE_HIST = (12, 4)
FIG_SIZE_HEATMAP = (8, 4)
COLOR_HARD = "#d62728"
COLOR_EASY = "#2ca02c"
COLOR_MEDIUM = "#aec7e8"
COLOR_THRESHOLD = "#ff7f0e"
COLOR_COVERAGE = "#1f77b4"
CMAP_HEATMAP = "YlOrRd"
MIN_N_LINE = 20
FIGURES_DIR = "h-e1/figures"


def plot_tier_sizes_bar(
    tier_stats: list[dict],
    min_n: int = 20,
    output_path: str = "h-e1/figures/tier_sizes_bar.png",
) -> None:
    """Bar chart: n_hard and n_easy per (model, benchmark) vs threshold n=20."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    labels = [f"{s['model']}\n{s['benchmark']}" for s in tier_stats]
    n_hard = [s["n_hard"] for s in tier_stats]
    n_easy = [s["n_easy"] for s in tier_stats]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=FIG_SIZE_BAR)
    ax.bar(x - width / 2, n_hard, width, label="Hard tier", color=COLOR_HARD, alpha=0.8)
    ax.bar(x + width / 2, n_easy, width, label="Easy tier", color=COLOR_EASY, alpha=0.8)
    ax.axhline(y=min_n, color=COLOR_THRESHOLD, linestyle="--", linewidth=2, label=f"Min N={min_n}")

    ax.set_xlabel("Model × Benchmark")
    ax.set_ylabel("Count")
    ax.set_title("Tier Sizes per Model and Benchmark")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)


def plot_pass_at_1_distribution(
    pass_at_1_per_model: dict,
    output_path: str = "h-e1/figures/pass_at_1_distribution.png",
) -> None:
    """6-point histogram per model per benchmark."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    model_ids = list(pass_at_1_per_model.keys())
    n_models = len(model_ids)

    fig, axes = plt.subplots(1, n_models, figsize=(max(FIG_SIZE_HIST[0], n_models * 4), FIG_SIZE_HIST[1]))
    if n_models == 1:
        axes = [axes]

    for ax, model_id in zip(axes, model_ids):
        model_data = pass_at_1_per_model[model_id]
        # Collect all pass@1 values across benchmarks
        all_values = []
        for benchmark, p1_dict in model_data.items():
            all_values.extend(p1_dict.values())

        ax.hist(all_values, bins=[-0.1, 0.1, 0.3, 0.5, 0.7, 0.9, 1.1], color=COLOR_HARD, alpha=0.7, edgecolor="black")
        ax.set_xlabel("pass@1")
        ax.set_ylabel("Count")
        ax.set_title(f"{model_id}")
        ax.set_xticks(bins)
        ax.grid(alpha=0.3)

    plt.suptitle("pass@1 Distribution per Model")
    plt.tight_layout()
    plt.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)


def plot_tier_size_heatmap(
    tier_stats: list[dict],
    output_path: str = "h-e1/figures/tier_size_heatmap.png",
) -> None:
    """Matrix (model × benchmark) → (n_hard, n_easy) heatmap."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    models = list(dict.fromkeys(s["model"] for s in tier_stats))
    benchmarks = list(dict.fromkeys(s["benchmark"] for s in tier_stats))

    hard_matrix = np.zeros((len(models), len(benchmarks)))
    easy_matrix = np.zeros((len(models), len(benchmarks)))

    for s in tier_stats:
        i = models.index(s["model"])
        j = benchmarks.index(s["benchmark"])
        hard_matrix[i, j] = s.get("n_hard", 0)
        easy_matrix[i, j] = s.get("n_easy", 0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIG_SIZE_HEATMAP)

    im1 = ax1.imshow(hard_matrix, cmap=CMAP_HEATMAP, aspect="auto")
    ax1.set_xticks(range(len(benchmarks)))
    ax1.set_xticklabels(benchmarks)
    ax1.set_yticks(range(len(models)))
    ax1.set_yticklabels(models)
    ax1.set_title("n_hard per (model, benchmark)")
    plt.colorbar(im1, ax=ax1)

    im2 = ax2.imshow(easy_matrix, cmap=CMAP_HEATMAP, aspect="auto")
    ax2.set_xticks(range(len(benchmarks)))
    ax2.set_xticklabels(benchmarks)
    ax2.set_yticks(range(len(models)))
    ax2.set_yticklabels(models)
    ax2.set_title("n_easy per (model, benchmark)")
    plt.colorbar(im2, ax=ax2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)


def plot_coverage_rate(
    coverage_per_model: dict,
    output_path: str = "h-e1/figures/coverage_rate.png",
) -> None:
    """Bar chart: coverage fraction per model."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    models = list(coverage_per_model.keys())
    rates = [coverage_per_model[m] for m in models]

    fig, ax = plt.subplots(figsize=(max(6, len(models) * 2), 4))
    bars = ax.bar(models, rates, color=COLOR_COVERAGE, alpha=0.8)
    ax.axhline(y=0.95, color=COLOR_THRESHOLD, linestyle="--", linewidth=2, label="Min 0.95")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Model")
    ax.set_ylabel("Coverage Rate")
    ax.set_title("EvalPlus Coverage Rate per Model")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{rate:.3f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)


def main(args=None) -> None:
    """Entry point: generate all 4 figures."""
    import argparse
    import json
    import csv
    parser = argparse.ArgumentParser(description="Generate H-E1 figures")
    parser.add_argument("--results_dir", type=str, default="results")
    parser.add_argument("--figures_dir", type=str, default="figures")
    if args is None:
        args = parser.parse_args()

    os.makedirs(args.figures_dir, exist_ok=True)

    # Load tier statistics
    csv_path = os.path.join(args.results_dir, "tier_statistics.csv")
    tier_stats = []
    if os.path.exists(csv_path):
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["n_hard"] = int(row["n_hard"])
                row["n_easy"] = int(row["n_easy"])
                tier_stats.append(row)

    if tier_stats:
        plot_tier_sizes_bar(tier_stats, output_path=os.path.join(args.figures_dir, "tier_sizes_bar.png"))
        plot_tier_size_heatmap(tier_stats, output_path=os.path.join(args.figures_dir, "tier_size_heatmap.png"))
        print(f"✓ Generated tier_sizes_bar.png and tier_size_heatmap.png")

    # Load pass@1 for distribution plot
    model_short_names = ["llama3_8b", "codellama_7b", "deepseek_6.7b"]
    pass_at_1_per_model: dict = {}
    coverage_per_model: dict = {}

    from evalplus.data import get_human_eval_plus, get_mbpp_plus
    problems_he = get_human_eval_plus()
    problems_mbpp = get_mbpp_plus()
    total_problems = len(problems_he) + len(problems_mbpp)

    for model_short in model_short_names:
        p1_path = os.path.join(args.results_dir, f"pass_at_1_{model_short}.json")
        corr_path = os.path.join(args.results_dir, f"correctness_{model_short}.json")
        if os.path.exists(p1_path):
            with open(p1_path) as f:
                p1 = json.load(f)
            # Split by benchmark
            he_p1 = {tid: v for tid, v in p1.items() if tid in problems_he}
            mbpp_p1 = {tid: v for tid, v in p1.items() if tid in problems_mbpp}
            pass_at_1_per_model[model_short] = {"humaneval": he_p1, "mbpp": mbpp_p1}

        if os.path.exists(corr_path):
            with open(corr_path) as f:
                corr = json.load(f)
            coverage_per_model[model_short] = len(corr) / total_problems

    if pass_at_1_per_model:
        plot_pass_at_1_distribution(
            pass_at_1_per_model,
            output_path=os.path.join(args.figures_dir, "pass_at_1_distribution.png")
        )
        print(f"✓ Generated pass_at_1_distribution.png")

    if coverage_per_model:
        plot_coverage_rate(
            coverage_per_model,
            output_path=os.path.join(args.figures_dir, "coverage_rate.png")
        )
        print(f"✓ Generated coverage_rate.png")


if __name__ == "__main__":
    main()
