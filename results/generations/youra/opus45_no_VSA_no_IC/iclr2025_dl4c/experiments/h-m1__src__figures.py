"""Figure generation for H-M1 experiment."""
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
from metrics import ScaleEvalResult


def plot_gate_metrics(results: ScaleEvalResult, out_path: str) -> None:
    """Bar chart: accuracy by scale tier (mandatory gate figure)."""
    scales = ["7B", "70B", "proprietary"]
    accuracies = [results["accuracies"][s] for s in scales]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(scales, accuracies, color=["#3498db", "#2ecc71", "#e74c3c"])

    ax.set_xlabel("Model Scale")
    ax.set_ylabel("Judge-Execution Agreement (Accuracy)")
    ax.set_title("H-M1: Scale vs Accuracy (MUST_WORK Gate)")
    ax.set_ylim(0, 1)

    for bar, acc in zip(bars, accuracies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{acc:.3f}", ha="center", va="bottom", fontsize=11)

    # Annotate ordering and diminishing returns
    status = "PASS" if results["ordering_satisfied"] and results["diminishing_returns"] else "FAIL"
    ax.text(0.02, 0.98, f"Ordering: {'✓' if results['ordering_satisfied'] else '✗'}\n"
                        f"Diminishing Returns: {'✓' if results['diminishing_returns'] else '✗'}\n"
                        f"p-value: {results['p_value']:.2e}\n"
                        f"Gate: {status}",
            transform=ax.transAxes, va="top", fontsize=10,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_diminishing_returns(results: ScaleEvalResult, out_path: str) -> None:
    """Line plot showing diminishing returns curve."""
    scales = ["7B", "70B", "proprietary"]
    scale_nums = [1, 2, 3]
    accuracies = [results["accuracies"][s] for s in scales]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(scale_nums, accuracies, "o-", markersize=12, linewidth=2, color="#2c3e50")

    # Annotate differences
    diff1 = results["diff_7b_70b"]
    diff2 = results["diff_70b_prop"]
    ax.annotate(f"Δ = {diff1:.3f}", xy=(1.5, (accuracies[0] + accuracies[1])/2),
                fontsize=10, ha="center")
    ax.annotate(f"Δ = {diff2:.3f}", xy=(2.5, (accuracies[1] + accuracies[2])/2),
                fontsize=10, ha="center")

    ax.set_xticks(scale_nums)
    ax.set_xticklabels(scales)
    ax.set_xlabel("Model Scale")
    ax.set_ylabel("Accuracy")
    ax.set_title(f"Diminishing Returns: {diff1:.3f} > {diff2:.3f}")
    ax.set_ylim(0.4, 0.85)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_confusion_matrices(confusion_matrices: Dict, out_path: str) -> None:
    """Per-scale confusion matrix visualization."""
    scales = ["7B", "70B", "proprietary"]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    for ax, scale in zip(axes, scales):
        cm = confusion_matrices[scale]
        matrix = np.array([[cm["TN"], cm["FP"]], [cm["FN"], cm["TP"]]])

        im = ax.imshow(matrix, cmap="Blues")
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Pred: Fail", "Pred: Pass"])
        ax.set_yticklabels(["GT: Fail", "GT: Pass"])
        ax.set_title(f"{scale}\nFPR={cm['FPR']:.2f}, FNR={cm['FNR']:.2f}")

        for i in range(2):
            for j in range(2):
                ax.text(j, i, matrix[i, j], ha="center", va="center", fontsize=14)

    plt.suptitle("Confusion Matrices by Scale")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_kappa_by_scale(results: ScaleEvalResult, out_path: str) -> None:
    """Bar chart: Cohen's Kappa per scale tier."""
    scales = ["7B", "70B", "proprietary"]
    kappas = [results["kappas"][s] for s in scales]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(scales, kappas, color=["#3498db", "#2ecc71", "#e74c3c"])

    ax.set_xlabel("Model Scale")
    ax.set_ylabel("Cohen's Kappa")
    ax.set_title("Agreement Quality (Cohen's Kappa) by Scale")
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.axhline(y=0.2, color="gray", linestyle="--", linewidth=0.5, label="Slight agreement")

    for bar, kappa in zip(bars, kappas):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{kappa:.3f}", ha="center", va="bottom", fontsize=11)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def generate_all_figures(results: ScaleEvalResult, figures_dir: str) -> None:
    """Generate all required figures."""
    import os
    os.makedirs(figures_dir, exist_ok=True)

    plot_gate_metrics(results, f"{figures_dir}/gate_metrics.png")
    plot_diminishing_returns(results, f"{figures_dir}/diminishing_returns.png")
    plot_confusion_matrices(results["confusion_matrices"], f"{figures_dir}/confusion_matrices.png")
    plot_kappa_by_scale(results, f"{figures_dir}/kappa_by_scale.png")
