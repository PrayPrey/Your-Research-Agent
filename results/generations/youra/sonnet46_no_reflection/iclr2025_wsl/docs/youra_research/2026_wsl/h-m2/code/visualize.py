"""
Visualization for H-M2: generates 5 required figures for validation report.
Uses matplotlib to create publication-quality plots.
"""
import numpy as np
from pathlib import Path
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def plot_gate_bar_chart(
    results_cifar10: Dict,
    results_svhn: Dict,
    threshold: float,
    output_path: Path,
) -> None:
    """Mandatory gate figure: Var_perm/Var_GL bar chart with 0.60 threshold line."""
    fig, ax = plt.subplots(figsize=(8, 6))

    subsets = ["CIFAR-10-GS", "SVHN-GS"]
    ratios = [results_cifar10.get("ratio_mean", 0.0), results_svhn.get("ratio_mean", 0.0)]
    stds = [results_cifar10.get("ratio_std", 0.0), results_svhn.get("ratio_std", 0.0)]
    n_models = [results_cifar10.get("n_models", 0), results_svhn.get("n_models", 0)]

    colors = ["#2196F3" if r > threshold else "#F44336" for r in ratios]
    bars = ax.bar(subsets, ratios, color=colors, alpha=0.8, width=0.5,
                  yerr=stds, capsize=8, error_kw={"linewidth": 2})

    ax.axhline(y=threshold, color="red", linestyle="--", linewidth=2,
               label=f"Gate threshold ({threshold:.2f})")

    for bar, r, n in zip(bars, ratios, n_models):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{r:.3f}\n(n={n})", ha="center", va="bottom", fontsize=10)

    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Var_perm / (Var_perm + Var_GL)", fontsize=12)
    ax.set_title("H-M2: Permutation Orbit Variance Dominance\nVar_perm / (Var_perm + Var_GL) per Dataset",
                 fontsize=12)
    ax.legend(fontsize=10)
    ax.set_xlabel("CNN Zoo Dataset", fontsize=12)

    pass_patch = mpatches.Patch(color="#2196F3", label="PASS (> threshold)")
    fail_patch = mpatches.Patch(color="#F44336", label="FAIL (< threshold)")
    ax.legend(handles=[pass_patch, fail_patch,
                        plt.Line2D([0], [0], color="red", linestyle="--", linewidth=2,
                                   label=f"Threshold ({threshold:.2f})")],
              fontsize=9)

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Gate bar chart saved: {output_path}")


def plot_ratio_histogram(
    ratios_cifar10: List[float],
    ratios_svhn: List[float],
    output_path: Path,
    threshold: float = 0.60,
) -> None:
    """Histogram of per-model variance ratios for both datasets."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    for ax, ratios, name, color in zip(
        axes,
        [ratios_cifar10, ratios_svhn],
        ["CIFAR-10-GS", "SVHN-GS"],
        ["#2196F3", "#4CAF50"]
    ):
        ax.hist(ratios, bins=30, color=color, alpha=0.7, edgecolor="white")
        ax.axvline(x=threshold, color="red", linestyle="--", linewidth=2,
                   label=f"Threshold ({threshold:.2f})")
        if ratios:
            ax.axvline(x=np.mean(ratios), color="orange", linestyle="-", linewidth=2,
                       label=f"Mean ({np.mean(ratios):.3f})")
        ax.set_xlabel("Var_perm / (Var_perm + Var_GL)", fontsize=11)
        ax.set_ylabel("Count", fontsize=11)
        ax.set_title(f"{name}\n(n={len(ratios)})", fontsize=11)
        ax.legend(fontsize=9)
        ax.set_xlim(0, 1)

    fig.suptitle("H-M2: Per-Model Variance Ratio Distribution", fontsize=13)
    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Ratio histogram saved: {output_path}")


def plot_ratio_vs_epoch(
    epoch_ratios: List[List[float]],
    output_path: Path,
) -> None:
    """Line plot of variance ratio vs training epoch."""
    fig, ax = plt.subplots(figsize=(9, 5))

    if not epoch_ratios:
        ax.text(0.5, 0.5, "No epoch data available", transform=ax.transAxes,
                ha="center", va="center")
    else:
        # Truncate to min length for alignment
        min_len = min(len(r) for r in epoch_ratios)
        matrix = np.array([r[:min_len] for r in epoch_ratios])

        mean_ratio = matrix.mean(axis=0)
        std_ratio = matrix.std(axis=0)
        epochs = np.arange(min_len)

        ax.plot(epochs, mean_ratio, "b-", linewidth=2, label="Mean ratio")
        ax.fill_between(epochs, mean_ratio - std_ratio, mean_ratio + std_ratio,
                        alpha=0.2, color="blue", label="±1 std")
        ax.axhline(y=0.60, color="red", linestyle="--", linewidth=1.5,
                   label="Gate threshold (0.60)")

    ax.set_xlabel("Training Epoch Index", fontsize=11)
    ax.set_ylabel("Var_perm / (Var_perm + Var_GL)", fontsize=11)
    ax.set_title("H-M2: Variance Ratio Evolution During Training", fontsize=12)
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Ratio vs epoch saved: {output_path}")


def plot_layer_breakdown(layer_stats: Dict, output_path: Path) -> None:
    """Bar chart of Conv2d vs Linear contribution to Var_perm and Var_GL."""
    fig, ax = plt.subplots(figsize=(8, 5))

    if not layer_stats:
        ax.text(0.5, 0.5, "No layer breakdown data", transform=ax.transAxes,
                ha="center", va="center")
    else:
        layer_types = list(layer_stats.keys())
        ratios = [layer_stats[lt].get("ratio", 0.0) for lt in layer_types]
        x = np.arange(len(layer_types))
        width = 0.5

        colors = ["#2196F3" if r > 0.6 else "#F44336" for r in ratios]
        ax.bar(x, ratios, width, color=colors, alpha=0.8, edgecolor="white")
        ax.axhline(y=0.60, color="red", linestyle="--", linewidth=1.5, label="Threshold (0.60)")

        for i, (lt, r) in enumerate(zip(layer_types, ratios)):
            ax.text(i, r + 0.02, f"{r:.3f}", ha="center", va="bottom", fontsize=10)

        ax.set_xticks(x)
        ax.set_xticklabels(layer_types, fontsize=11)
        ax.set_ylabel("Var_perm / (Var_perm + Var_GL)", fontsize=11)
        ax.set_title("H-M2: Per-Layer-Type Variance Ratio Breakdown", fontsize=12)
        ax.legend(fontsize=9)
        ax.set_ylim(0, 1.1)

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Layer breakdown saved: {output_path}")


def plot_ratio_vs_accuracy(
    ratios: List[float],
    accuracies: List[float],
    output_path: Path,
) -> None:
    """Scatter plot: variance ratio vs final model accuracy."""
    fig, ax = plt.subplots(figsize=(8, 6))

    if ratios and accuracies:
        n = min(len(ratios), len(accuracies))
        ratios_arr = np.array(ratios[:n])
        acc_arr = np.array(accuracies[:n])

        scatter = ax.scatter(acc_arr, ratios_arr, alpha=0.5, c="#2196F3",
                             edgecolors="none", s=30)
        ax.axhline(y=0.60, color="red", linestyle="--", linewidth=1.5,
                   label="Gate threshold (0.60)")

        # Trend line
        if len(ratios_arr) > 2:
            z = np.polyfit(acc_arr, ratios_arr, 1)
            p = np.poly1d(z)
            x_line = np.linspace(acc_arr.min(), acc_arr.max(), 100)
            ax.plot(x_line, p(x_line), "orange", linewidth=1.5, label="Trend")

        corr = np.corrcoef(acc_arr, ratios_arr)[0, 1] if n > 2 else 0.0
        ax.set_title(f"H-M2: Variance Ratio vs Final Accuracy (r={corr:.3f})", fontsize=12)
    else:
        ax.text(0.5, 0.5, "No data available", transform=ax.transAxes,
                ha="center", va="center")
        ax.set_title("H-M2: Variance Ratio vs Final Accuracy", fontsize=12)

    ax.set_xlabel("Final Model Accuracy", fontsize=11)
    ax.set_ylabel("Var_perm / (Var_perm + Var_GL)", fontsize=11)
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Ratio vs accuracy saved: {output_path}")


def save_all_figures(results: Dict, figures_dir: Path) -> None:
    """Generate and save all 5 required figures."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    results_c = results.get("cifar10", {})
    results_s = results.get("svhn", {})
    threshold = results.get("gate_threshold", 0.60)

    print(f"\n📊 Generating figures in {figures_dir}/")

    # 1. Mandatory gate figure
    plot_gate_bar_chart(
        results_c, results_s, threshold,
        figures_dir / "gate_bar_chart.png"
    )

    # 2. Ratio histogram
    plot_ratio_histogram(
        results_c.get("ratios", []),
        results_s.get("ratios", []),
        figures_dir / "ratio_histogram.png",
        threshold=threshold,
    )

    # 3. Ratio vs epoch
    epoch_ratios = results_c.get("epoch_ratios", [])
    plot_ratio_vs_epoch(epoch_ratios, figures_dir / "ratio_vs_epoch.png")

    # 4. Layer breakdown
    layer_stats = results_c.get("layer_stats", {})
    plot_layer_breakdown(layer_stats, figures_dir / "layer_breakdown.png")

    # 5. Ratio vs accuracy (use CIFAR-10 data)
    ratios_c = results_c.get("ratios", [])
    accuracies = results.get("accuracies_cifar10", [0.0] * len(ratios_c))
    plot_ratio_vs_accuracy(ratios_c, accuracies, figures_dir / "ratio_vs_accuracy.png")

    print(f"✓ All 5 figures saved to {figures_dir}/")
