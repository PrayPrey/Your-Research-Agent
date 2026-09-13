"""Figures module: generate experiment visualizations."""
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
from config import DEDUP_LEVELS

def dose_response_curve(aggregated: Dict, out_path: str):
    """Generate dose-response curve: ensemble score vs deduplication level."""
    levels_order = [cfg.level for cfg in DEDUP_LEVELS]
    x_labels = []
    means = []
    stds = []

    for level in levels_order:
        if level in aggregated:
            x_labels.append(level.replace("_", "\n"))
            means.append(aggregated[level]["ensemble_mean"])
            stds.append(aggregated[level]["ensemble_std"])

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(x_labels))
    ax.bar(x, means, yerr=stds, capsize=5, color='steelblue', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=10)
    ax.set_xlabel("Deduplication Level", fontsize=12)
    ax.set_ylabel("Ensemble Score", fontsize=12)
    ax.set_title("H-M2: Deduplication Stringency vs Benchmark Performance", fontsize=14)
    ax.grid(axis='y', alpha=0.3)

    # Mark best
    if means:
        best_idx = np.argmax(means)
        ax.bar(best_idx, means[best_idx], color='green', alpha=0.8, label='Best')
        ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved dose-response curve to {out_path}")

def benchmark_breakdown(aggregated: Dict, out_path: str):
    """Generate per-benchmark grouped bar chart."""
    levels_order = [cfg.level for cfg in DEDUP_LEVELS]
    tasks = ["hellaswag", "arc_easy", "piqa", "winogrande"]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    x_labels = [l.replace("_", "\n") for l in levels_order if l in aggregated]
    x = np.arange(len(x_labels))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, task in enumerate(tasks):
        values = [aggregated[l]["mean_scores"].get(task, 0) for l in levels_order if l in aggregated]
        ax.bar(x + i * width - 1.5 * width, values, width, label=task, color=colors[i])

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=10)
    ax.set_xlabel("Deduplication Level", fontsize=12)
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_title("Per-Benchmark Scores Across Deduplication Levels", fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved benchmark breakdown to {out_path}")

def data_stats_figure(dedup_stats: Dict, out_path: str):
    """Generate data statistics figure."""
    levels_order = [cfg.level for cfg in DEDUP_LEVELS]
    x_labels = []
    original = []
    deduplicated = []

    for level in levels_order:
        if level in dedup_stats:
            x_labels.append(level.replace("_", "\n"))
            original.append(dedup_stats[level]["original"])
            deduplicated.append(dedup_stats[level]["deduplicated"])

    if not x_labels:
        print("No dedup stats available for figure")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(x_labels))
    width = 0.35

    ax.bar(x - width/2, original, width, label='Original', color='lightgray')
    ax.bar(x + width/2, deduplicated, width, label='After Dedup', color='steelblue')

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=10)
    ax.set_xlabel("Deduplication Level", fontsize=12)
    ax.set_ylabel("Document Count", fontsize=12)
    ax.set_title("Document Counts Before/After Deduplication", fontsize=14)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved data stats figure to {out_path}")

def loss_curves_figure(results: Dict, out_path: str):
    """Generate training loss curves."""
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0, 1, 5))

    levels_order = [cfg.level for cfg in DEDUP_LEVELS]

    for i, level in enumerate(levels_order):
        if level not in results:
            continue
        for seed, data in results[level].items():
            if "final_loss" in data and data["final_loss"]:
                # Just plot final loss as point (full curves would need loss history)
                ax.scatter([int(seed)], [data["final_loss"]], color=colors[i], s=100, label=f"{level}" if seed == "0" else "")

    ax.set_xlabel("Seed", fontsize=12)
    ax.set_ylabel("Final Loss", fontsize=12)
    ax.set_title("Final Training Loss by Deduplication Level", fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved loss curves figure to {out_path}")

def generate_all_figures(results: Dict, aggregated: Dict, dedup_stats: Dict, figures_dir: str):
    """Generate all required figures."""
    os.makedirs(figures_dir, exist_ok=True)

    dose_response_curve(aggregated, os.path.join(figures_dir, "dose_response.png"))
    benchmark_breakdown(aggregated, os.path.join(figures_dir, "benchmark_breakdown.png"))
    if dedup_stats:
        data_stats_figure(dedup_stats, os.path.join(figures_dir, "data_stats.png"))
    loss_curves_figure(results, os.path.join(figures_dir, "loss_curves.png"))

    print(f"\nAll figures saved to {figures_dir}")
