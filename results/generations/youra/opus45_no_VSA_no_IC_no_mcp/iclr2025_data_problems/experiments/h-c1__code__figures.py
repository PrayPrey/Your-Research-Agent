"""Visualization for H-C1 comparison."""

import os
import numpy as np
import matplotlib.pyplot as plt


def plot_ensemble_comparison(results: dict, out_path: str) -> None:
    """Bar chart: CPDR vs RP ensemble scores with error bars."""
    cpdr = results["cpdr_per_seed"]
    rp = results["rp_per_seed"]

    fig, ax = plt.subplots(figsize=(8, 6))
    x = [0, 1]
    means = [np.mean(cpdr), np.mean(rp)]
    stds = [np.std(cpdr), np.std(rp)]
    colors = ["#2ecc71", "#e74c3c"]

    bars = ax.bar(x, means, yerr=stds, capsize=5, color=colors, edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels(["CPDR (p50/fuzzy_0.85)", "RedPajama (p30/exact)"])
    ax.set_ylabel("Ensemble Score (mean accuracy)")
    ax.set_title("H-C1: CPDR vs RedPajama Defaults Comparison")

    improvement = results.get("gate", {}).get("improvement", 0)
    passed = results.get("gate", {}).get("passed", False)
    status = "PASS" if passed else "FAIL"
    ax.text(0.5, max(means) + max(stds) + 0.02, f"Δ = {improvement:.3f} ({status})",
            ha="center", fontsize=12, fontweight="bold")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_per_benchmark_breakdown(raw: dict, tasks: list, out_path: str) -> None:
    """Grouped bar chart per benchmark."""
    per_seed = raw["per_seed"]
    if not per_seed:
        return

    cpdr_means = {t: np.mean([s["cpdr"][t] for s in per_seed]) for t in tasks}
    rp_means = {t: np.mean([s["redpajama"][t] for s in per_seed]) for t in tasks}

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(tasks))
    width = 0.35

    ax.bar(x - width/2, [cpdr_means[t] for t in tasks], width, label="CPDR", color="#2ecc71")
    ax.bar(x + width/2, [rp_means[t] for t in tasks], width, label="RedPajama", color="#e74c3c")

    ax.set_xticks(x)
    ax.set_xticklabels(tasks, rotation=15)
    ax.set_ylabel("Accuracy")
    ax.set_title("Per-Benchmark Comparison")
    ax.legend()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_improvement_waterfall(raw: dict, tasks: list, out_path: str) -> None:
    """Waterfall chart showing per-task improvement."""
    per_seed = raw["per_seed"]
    if not per_seed:
        return

    improvements = {}
    for t in tasks:
        cpdr_mean = np.mean([s["cpdr"][t] for s in per_seed])
        rp_mean = np.mean([s["redpajama"][t] for s in per_seed])
        improvements[t] = cpdr_mean - rp_mean

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2ecc71" if v > 0 else "#e74c3c" for v in improvements.values()]
    ax.bar(tasks, list(improvements.values()), color=colors, edgecolor="black")
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.set_ylabel("CPDR - RedPajama")
    ax.set_title("Per-Task Improvement")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
