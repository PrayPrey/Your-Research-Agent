"""H-E1 figure generation."""

import json
import pathlib
from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class FigureConfig:
    figsize: tuple = (8, 5)
    dpi: int = 150
    gate_threshold: float = 0.10

    gate_metrics: str = "gate_metrics.png"
    error_type_dist: str = "error_type_dist.png"
    error_count_hist: str = "error_count_hist.png"
    seed_consistency: str = "seed_consistency.png"


FIG = FigureConfig()

FIGURES_DIR = pathlib.Path("docs/youra_research/h-e1/figures")


def _save(fig: plt.Figure, name: str, figures_dir: pathlib.Path = FIGURES_DIR) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    path = figures_dir / name
    fig.savefig(path, dpi=FIG.dpi, bbox_inches="tight")
    plt.close(fig)


def plot_gate_metrics(summary: dict, figures_dir: pathlib.Path = FIGURES_DIR) -> None:
    """Bar chart: type_error_fraction vs 0.10 threshold, std error bars."""
    benchmarks = list(summary.keys())
    means = [summary[bm]["type_error_fraction_mean"] for bm in benchmarks]
    stds = [summary[bm]["type_error_fraction_std"] for bm in benchmarks]

    fig, ax = plt.subplots(figsize=FIG.figsize)
    x = np.arange(len(benchmarks))
    bars = ax.bar(x, means, yerr=stds, capsize=5, color=["#4878d0", "#ee854a"], alpha=0.8)
    ax.axhline(y=FIG.gate_threshold, color="red", linestyle="--", linewidth=1.5, label=f"Gate threshold ({FIG.gate_threshold:.0%})")
    ax.set_xticks(x)
    ax.set_xticklabels([bm.upper() for bm in benchmarks])
    ax.set_ylabel("Type Error Fraction (among failing solutions)")
    ax.set_title("H-E1: mypy Type Error Fraction in Failing LLM Solutions")
    ax.legend()
    ax.set_ylim(0, max(max(means) + max(stds) + 0.05, FIG.gate_threshold + 0.1))

    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.005,
                f"{mean:.1%}", ha="center", va="bottom", fontsize=9)

    _save(fig, FIG.gate_metrics, figures_dir)


def plot_error_type_dist(results: list, figures_dir: pathlib.Path = FIGURES_DIR) -> None:
    """Bar chart of mypy error categories among solutions with errors."""
    error_solutions = [r for r in results if r.get("has_mypy_error")]
    if not error_solutions:
        return

    categories = ["name-error", "type-error", "return-value", "attribute-error"]
    counts = {cat: 0 for cat in categories}
    for r in error_solutions:
        for cat in categories:
            counts[cat] += r.get("error_categories", {}).get(cat, 0)

    fig, ax = plt.subplots(figsize=FIG.figsize)
    x = np.arange(len(categories))
    ax.bar(x, [counts[c] for c in categories], color="#4878d0", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=15)
    ax.set_ylabel("Count")
    ax.set_title("H-E1: mypy Error Type Distribution")
    _save(fig, FIG.error_type_dist, figures_dir)


def plot_error_count_hist(results: list, figures_dir: pathlib.Path = FIGURES_DIR) -> None:
    """Histogram of mypy error counts per failing solution."""
    counts = [r["error_count"] for r in results if r.get("has_mypy_error")]
    if not counts:
        return

    fig, ax = plt.subplots(figsize=FIG.figsize)
    ax.hist(counts, bins=range(0, max(counts) + 2), color="#4878d0", alpha=0.8, edgecolor="white")
    ax.set_xlabel("Number of mypy Errors")
    ax.set_ylabel("Count")
    ax.set_title("H-E1: mypy Error Count Distribution (per failing solution)")
    _save(fig, FIG.error_count_hist, figures_dir)


def plot_seed_consistency(summary: dict, figures_dir: pathlib.Path = FIGURES_DIR) -> None:
    """Box plot of type_error_fraction across 3 seeds."""
    benchmarks = list(summary.keys())
    data = []
    labels = []
    for bm in benchmarks:
        fractions = [v["fraction"] for v in summary[bm]["per_seed"].values()]
        if fractions:
            data.append(fractions)
            labels.append(bm.upper())

    if not data:
        return

    fig, ax = plt.subplots(figsize=FIG.figsize)
    ax.boxplot(data, labels=labels, patch_artist=True,
               boxprops=dict(facecolor="#4878d0", alpha=0.6))
    ax.axhline(y=FIG.gate_threshold, color="red", linestyle="--", linewidth=1.5,
               label=f"Gate threshold ({FIG.gate_threshold:.0%})")
    ax.set_ylabel("Type Error Fraction")
    ax.set_title("H-E1: Seed Consistency of Type Error Fraction")
    ax.legend()
    _save(fig, FIG.seed_consistency, figures_dir)


def generate_all_figures(results: list, summary: dict, figures_dir: pathlib.Path = FIGURES_DIR) -> None:
    """Generate all figures."""
    plot_gate_metrics(summary, figures_dir)
    plot_error_type_dist(results, figures_dir)
    plot_error_count_hist(results, figures_dir)
    plot_seed_consistency(summary, figures_dir)
