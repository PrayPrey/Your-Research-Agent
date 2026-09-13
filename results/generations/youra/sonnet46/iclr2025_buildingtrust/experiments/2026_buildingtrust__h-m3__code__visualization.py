"""
visualization.py — H-M3 Mechanism Discrimination
Figure generation: 5 figures per FR-6 spec.
"""
import logging
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

logger = logging.getLogger(__name__)

COLORS: dict = {
    "ppo": "red",
    "dpo": "orange",
    "sft": "blue",
    "base": "gray",
}


def plot_spearman_rho_bar(
    spearman_results: dict,
    figures_dir: str,
    h1_threshold: float = 0.9,
    h2_threshold: float = 0.85,
    dpi: int = 150,
) -> str:
    """FR-6.1: Mean rho per alignment x size bar chart with H1/H2 thresholds."""
    os.makedirs(figures_dir, exist_ok=True)

    sizes = sorted(set(k.split("-")[0] for k in spearman_results))
    alignments = sorted(set(k.split("-")[1] for k in spearman_results))

    x = np.arange(len(sizes))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, alignment in enumerate(alignments):
        rhos = [
            spearman_results.get(f"{size}-{alignment}", {}).get("mean_rho", float("nan"))
            for size in sizes
        ]
        offset = (i - len(alignments) / 2 + 0.5) * width
        ax.bar(x + offset, rhos, width, label=alignment, color=COLORS.get(alignment, "black"), alpha=0.8)

    ax.axhline(h1_threshold, color="green", linestyle="--", linewidth=1.5, label=f"H1 threshold ({h1_threshold})")
    ax.axhline(h2_threshold, color="purple", linestyle=":", linewidth=1.5, label=f"H2 threshold ({h2_threshold})")
    ax.set_xticks(x)
    ax.set_xticklabels(sizes)
    ax.set_xlabel("Model Size")
    ax.set_ylabel("Mean Spearman rho")
    ax.set_title("Mean Spearman rho per Alignment x Size (MMLU)")
    ax.legend()
    ax.set_ylim(0, 1.05)

    out_path = os.path.join(figures_dir, "figure_01_spearman_rho.png")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved figure_01_spearman_rho.png")
    return out_path


def plot_rho_distribution(
    spearman_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """FR-6.2: Violin/histogram of per-item rho distributions."""
    os.makedirs(figures_dir, exist_ok=True)

    alignments = sorted(set(k.split("-")[1] for k in spearman_results))
    fig, axes = plt.subplots(1, len(alignments), figsize=(5 * len(alignments), 5), sharey=True)
    if len(alignments) == 1:
        axes = [axes]

    for ax, alignment in zip(axes, alignments):
        data = []
        labels = []
        for k, res in sorted(spearman_results.items()):
            if k.endswith(f"-{alignment}"):
                rho_arr = res.get("rho_per_item")
                if rho_arr is not None and len(rho_arr) > 0:
                    data.append(rho_arr)
                    labels.append(k.split("-")[0])
        if data:
            ax.violinplot(data, showmedians=True)
            ax.set_xticks(range(1, len(labels) + 1))
            ax.set_xticklabels(labels)
        ax.set_title(f"{alignment.upper()}")
        ax.set_ylabel("Per-item Spearman rho")
        ax.set_ylim(-1.05, 1.05)

    fig.suptitle("Per-item Spearman rho Distribution by Alignment")
    out_path = os.path.join(figures_dir, "figure_02_rho_distribution.png")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved figure_02_rho_distribution.png")
    return out_path


def plot_brier_partition(
    partition_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """FR-6.3: Grouped bar: shared vs changed-argmax Brier reliability."""
    os.makedirs(figures_dir, exist_ok=True)

    keys = sorted(partition_results.keys())
    n = len(keys)
    x = np.arange(n)
    width = 0.2

    shared_base = [partition_results[k]["rel_shared_base"] for k in keys]
    shared_aligned = [partition_results[k]["rel_shared_aligned"] for k in keys]
    changed_base = [partition_results[k]["rel_changed_base"] for k in keys]
    changed_aligned = [partition_results[k]["rel_changed_aligned"] for k in keys]

    fig, ax = plt.subplots(figsize=(max(10, n * 1.5), 6))
    ax.bar(x - 1.5 * width, shared_base, width, label="Shared-argmax Base", color="steelblue", alpha=0.7)
    ax.bar(x - 0.5 * width, shared_aligned, width, label="Shared-argmax Aligned", color="steelblue", alpha=1.0)
    ax.bar(x + 0.5 * width, changed_base, width, label="Changed-argmax Base", color="firebrick", alpha=0.7)
    ax.bar(x + 1.5 * width, changed_aligned, width, label="Changed-argmax Aligned", color="firebrick", alpha=1.0)

    ax.set_xticks(x)
    ax.set_xticklabels(keys, rotation=45, ha="right")
    ax.set_xlabel("Model Pair")
    ax.set_ylabel("Brier Reliability")
    ax.set_title("Brier Reliability: Shared vs Changed-argmax Subsets")
    ax.legend()

    # Annotate Cohen's d
    for i, k in enumerate(keys):
        d = partition_results[k].get("cohens_d_shared", float("nan"))
        if not (isinstance(d, float) and np.isnan(d)):
            ax.annotate(f"d={d:.2f}", xy=(x[i], max(shared_aligned[i], changed_aligned[i]) + 0.005),
                        ha="center", fontsize=7)

    out_path = os.path.join(figures_dir, "figure_03_brier_partition.png")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved figure_03_brier_partition.png")
    return out_path


def plot_argmax_proportion(
    partition_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """FR-6.4: Stacked bar: % shared vs changed-argmax per model."""
    os.makedirs(figures_dir, exist_ok=True)

    keys = sorted(partition_results.keys())
    n_shared = [partition_results[k]["n_shared"] for k in keys]
    n_changed = [partition_results[k]["n_changed"] for k in keys]
    totals = [s + c for s, c in zip(n_shared, n_changed)]
    pct_shared = [100 * s / t if t > 0 else 0 for s, t in zip(n_shared, totals)]
    pct_changed = [100 * c / t if t > 0 else 0 for c, t in zip(n_changed, totals)]

    x = np.arange(len(keys))
    fig, ax = plt.subplots(figsize=(max(8, len(keys) * 1.2), 5))
    ax.bar(x, pct_shared, label="Shared argmax", color="steelblue")
    ax.bar(x, pct_changed, bottom=pct_shared, label="Changed argmax", color="firebrick")
    ax.set_xticks(x)
    ax.set_xticklabels(keys, rotation=45, ha="right")
    ax.set_xlabel("Model Pair")
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Argmax Proportion: Shared vs Changed")
    ax.legend()

    out_path = os.path.join(figures_dir, "figure_04_argmax_proportion.png")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved figure_04_argmax_proportion.png")
    return out_path


def plot_truthfulqa_ece(
    tqa_ece_results: dict,
    mmlu_ece_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """FR-6.5: TruthfulQA MC1 ECE vs MMLU ECE side-by-side."""
    os.makedirs(figures_dir, exist_ok=True)

    model_keys = sorted(set(list(tqa_ece_results.keys()) + list(mmlu_ece_results.keys())))
    tqa_eces = [tqa_ece_results.get(k, {}).get("ece", float("nan")) for k in model_keys]
    mmlu_eces = [mmlu_ece_results.get(k, float("nan")) if isinstance(mmlu_ece_results.get(k), float)
                 else mmlu_ece_results.get(k, {}).get("ece", float("nan"))
                 for k in model_keys]

    x = np.arange(len(model_keys))
    width = 0.35
    fig, ax = plt.subplots(figsize=(max(10, len(model_keys) * 0.9), 5))
    ax.bar(x - width / 2, tqa_eces, width, label="TruthfulQA MC1 ECE", color="coral", alpha=0.9)
    ax.bar(x + width / 2, mmlu_eces, width, label="MMLU ECE", color="steelblue", alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(model_keys, rotation=45, ha="right", fontsize=8)
    ax.set_xlabel("Model")
    ax.set_ylabel("ECE")
    ax.set_title("TruthfulQA MC1 vs MMLU ECE Comparison")
    ax.legend()

    out_path = os.path.join(figures_dir, "figure_05_truthfulqa_ece.png")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved figure_05_truthfulqa_ece.png")
    return out_path


def generate_all_figures(
    spearman_results: dict,
    partition_results: dict,
    tqa_ece_results: dict,
    mmlu_ece_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> list:
    """Generate all 5 figures; return list of saved paths."""
    paths = []
    paths.append(plot_spearman_rho_bar(spearman_results, figures_dir, dpi=dpi))
    paths.append(plot_rho_distribution(spearman_results, figures_dir, dpi=dpi))
    paths.append(plot_brier_partition(partition_results, figures_dir, dpi=dpi))
    paths.append(plot_argmax_proportion(partition_results, figures_dir, dpi=dpi))
    paths.append(plot_truthfulqa_ece(tqa_ece_results, mmlu_ece_results, figures_dir, dpi=dpi))
    logger.info("Generated %d figures in %s", len(paths), figures_dir)
    return paths
