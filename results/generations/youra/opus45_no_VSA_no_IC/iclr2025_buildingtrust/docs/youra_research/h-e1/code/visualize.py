"""Visualization suite for H-E1: correlation heatmap, scatter plots, gate metrics, diversity."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from config import FIGURES_DIR, CORR_UPPER_BOUND
import os


def plot_correlation_heatmap(corr_matrix: pd.DataFrame, out_path: str) -> None:
    """Generate annotated correlation heatmap."""
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={"label": "Spearman r"}
    )
    plt.title("Benchmark Correlation Matrix (Spearman)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_pairwise_scatter(scores: pd.DataFrame, benchmarks: list, out_dir: str) -> None:
    """Generate scatter plot with regression line for each benchmark pair."""
    os.makedirs(out_dir, exist_ok=True)

    for a, b in combinations(benchmarks, 2):
        plt.figure(figsize=(6, 5))
        sns.regplot(
            x=scores[a],
            y=scores[b],
            scatter_kws={"alpha": 0.6, "s": 40},
            line_kws={"color": "red", "lw": 2}
        )
        plt.xlabel(a.replace("_", " ").title())
        plt.ylabel(b.replace("_", " ").title())
        plt.title(f"{a} vs {b}")
        plt.tight_layout()

        out_path = os.path.join(out_dir, f"scatter_{a}_{b}.png")
        plt.savefig(out_path, dpi=150)
        plt.close()
        print(f"Saved: {out_path}")


def plot_gate_metrics(result: dict, out_path: str) -> None:
    """Bar chart: cross-benchmark r values vs baseline_r and upper threshold."""
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)

    correlations = result["correlations"]
    baseline_r = result["baseline_r"]
    threshold_upper = result["threshold_upper"]

    pairs = list(correlations.keys())
    values = [correlations[p] for p in pairs]

    # Determine colors based on gate condition
    colors = []
    for v in values:
        if baseline_r < v < threshold_upper:
            colors.append("green")
        else:
            colors.append("red")

    plt.figure(figsize=(10, 6))
    bars = plt.bar(pairs, values, color=colors, alpha=0.7, edgecolor="black")

    # Reference lines
    plt.axhline(y=baseline_r, color="blue", linestyle="--", linewidth=2, label=f"Baseline r = {baseline_r:.3f}")
    plt.axhline(y=threshold_upper, color="orange", linestyle="--", linewidth=2, label=f"Upper threshold = {threshold_upper}")

    # Shade acceptable region
    plt.fill_between(
        [-0.5, len(pairs) - 0.5],
        baseline_r, threshold_upper,
        alpha=0.1, color="green",
        label="Acceptable range"
    )

    plt.xlabel("Benchmark Pair")
    plt.ylabel("Spearman Correlation (r)")
    plt.title(f"Gate Metrics: Cross-Benchmark Correlations\n{'PASS' if result['passed'] else 'FAIL'}")
    plt.legend(loc="upper right")
    plt.ylim(0, 1)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_model_diversity(scores: pd.DataFrame, out_path: str) -> None:
    """3-panel histogram: arch, scale, variant distributions."""
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    diversity_cols = ["arch", "scale", "variant"]
    titles = ["Architecture", "Scale", "Variant"]

    for ax, col, title in zip(axes, diversity_cols, titles):
        if col in scores.columns:
            counts = scores[col].value_counts()
            ax.bar(counts.index, counts.values, color="steelblue", alpha=0.7, edgecolor="black")
            ax.set_xlabel(title)
            ax.set_ylabel("Count")
            ax.set_title(f"Model {title} Distribution")
            ax.tick_params(axis="x", rotation=45)
        else:
            ax.text(0.5, 0.5, f"No {col} data", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(f"Model {title} Distribution")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    from data import load_benchmark_scores
    from analyze import BenchmarkCorrelationAnalyzer

    scores = load_benchmark_scores()
    analyzer = BenchmarkCorrelationAnalyzer(scores)
    result = analyzer.evaluate_hypothesis()
    corr_matrix = analyzer.compute_correlation_matrix()

    plot_correlation_heatmap(corr_matrix, f"{FIGURES_DIR}heatmap.png")
    plot_pairwise_scatter(scores, analyzer.benchmarks, FIGURES_DIR)
    plot_gate_metrics(result, f"{FIGURES_DIR}gate_metrics.png")
    plot_model_diversity(scores, f"{FIGURES_DIR}diversity.png")
