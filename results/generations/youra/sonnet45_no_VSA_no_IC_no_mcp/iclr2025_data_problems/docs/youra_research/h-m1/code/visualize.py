"""
Visualization for h-m1 Threshold Transfer Experiment
4 required plots per 03_architecture.md
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def plot_gate_metrics(
    results: Dict,
    output_path: str,
    max_delta: float = 0.10
):
    """Gate metrics comparison: target vs actual delta"""
    fig, ax = plt.subplots(figsize=(8, 5))

    deltas = [
        results["transfer_deltas"]["pretrain_to_finetune"],
        results["transfer_deltas"]["finetune_to_pretrain"],
    ]
    labels = ["Pretrain→Finetune", "Finetune→Pretrain"]

    x = np.arange(len(labels))
    bars = ax.bar(x, deltas, color=['#2E86AB', '#A23B72'])
    ax.axhline(y=max_delta, color='red', linestyle='--', label=f'Gate threshold ({max_delta*100}%)')

    ax.set_ylabel("Performance Delta")
    ax.set_xlabel("Transfer Direction")
    ax.set_title("Gate Metrics: Transfer Delta vs Threshold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved gate metrics plot: {output_path}")


def plot_threshold_heatmap(
    sweep_results: Dict[Tuple[float, int], Tuple[List[Dict], Dict]],
    metric: str = "final_count",
    output_path: str = None
):
    """Threshold sensitivity heatmap"""
    dedup_vals = sorted(set(k[0] for k in sweep_results.keys()))
    ppl_vals = sorted(set(k[1] for k in sweep_results.keys()))

    # Build matrix
    matrix = np.zeros((len(ppl_vals), len(dedup_vals)))
    for i, ppl in enumerate(ppl_vals):
        for j, dedup in enumerate(dedup_vals):
            stats = sweep_results[(dedup, ppl)][1]
            matrix[i, j] = stats[metric]

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        matrix,
        xticklabels=[f"{d:.1f}" for d in dedup_vals],
        yticklabels=ppl_vals,
        annot=True,
        fmt='.0f',
        cmap='YlGnBu',
        ax=ax
    )
    ax.set_xlabel("Deduplication Threshold")
    ax.set_ylabel("Perplexity Cutoff")
    ax.set_title(f"Threshold Sensitivity: {metric}")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved threshold heatmap: {output_path}")


def plot_transfer_delta(
    transfer_results: Dict[str, float],
    output_path: str
):
    """Transfer delta bar chart"""
    fig, ax = plt.subplots(figsize=(8, 5))

    directions = [
        "Pretrain→Finetune",
        "Finetune→Pretrain",
    ]
    deltas = [
        transfer_results["pretrain_to_finetune"],
        transfer_results["finetune_to_pretrain"],
    ]

    x = np.arange(len(directions))
    bars = ax.bar(x, deltas, color=['#F18F01', '#C73E1D'])

    ax.set_ylabel("Performance Delta")
    ax.set_xlabel("Transfer Direction")
    ax.set_title("Cross-Stage Threshold Transfer Delta")
    ax.set_xticks(x)
    ax.set_xticklabels(directions)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved transfer delta plot: {output_path}")


def plot_curation_impact(
    sweep_results: Dict[Tuple[float, int], Tuple[List[Dict], Dict]],
    output_path: str
):
    """Curation impact: samples filtered per threshold"""
    configs = list(sweep_results.keys())
    configs_str = [f"D={d:.1f}, P={p}" for d, p in configs]
    removed_counts = [sweep_results[c][1]["removed_total"] for c in configs]
    final_counts = [sweep_results[c][1]["final_count"] for c in configs]

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(configs))
    ax.bar(x, final_counts, label="Retained", color='#06A77D')
    ax.bar(x, removed_counts, bottom=final_counts, label="Filtered", color='#D62828')

    ax.set_ylabel("Sample Count")
    ax.set_xlabel("Threshold Configuration")
    ax.set_title("Curation Impact: Samples Retained vs Filtered")
    ax.set_xticks(x)
    ax.set_xticklabels(configs_str, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved curation impact plot: {output_path}")


def generate_all_figures(
    results: Dict,
    pretrain_sweep: Dict,
    finetune_sweep: Dict,
    figures_dir: str
):
    """Generate all 4 required figures"""
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    # 1. Gate metrics
    plot_gate_metrics(
        results,
        f"{figures_dir}/gate_metrics_comparison.png",
        max_delta=results.get("max_delta_threshold", 0.10)
    )

    # 2. Threshold heatmap (use pretrain sweep)
    plot_threshold_heatmap(
        pretrain_sweep,
        metric="final_count",
        output_path=f"{figures_dir}/threshold_sensitivity_heatmap.png"
    )

    # 3. Transfer delta
    plot_transfer_delta(
        results["transfer_deltas"],
        f"{figures_dir}/transfer_delta_barchart.png"
    )

    # 4. Curation impact (use finetune sweep)
    plot_curation_impact(
        finetune_sweep,
        f"{figures_dir}/curation_impact_chart.png"
    )

    logger.info(f"All figures saved to {figures_dir}")
