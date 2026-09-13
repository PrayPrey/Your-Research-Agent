"""H-M3 Visualization: Gate comparison and ROC curve"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve


def plot_gate_comparison(achieved_auroc: float, threshold: float, out_path: str) -> None:
    """Bar chart comparing achieved AUROC vs gate threshold."""
    fig, ax = plt.subplots(figsize=(6, 4))

    labels = ["Achieved", "Threshold"]
    values = [achieved_auroc, threshold]
    colors = ["#2ecc71" if achieved_auroc >= threshold else "#e74c3c", "#3498db"]

    bars = ax.bar(labels, values, color=colors, edgecolor="black", width=0.5)

    ax.set_ylabel("AUROC")
    ax.set_title("H-M3 Gate: Linear Probe AUROC")
    ax.set_ylim(0, 1.0)
    ax.axhline(y=threshold, color="#3498db", linestyle="--", alpha=0.7, label=f"Gate = {threshold}")

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=11)

    status = "PASS" if achieved_auroc >= threshold else "FAIL"
    ax.text(0.95, 0.95, status, transform=ax.transAxes, fontsize=14, fontweight="bold",
            ha="right", va="top", color="green" if status == "PASS" else "red")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_roc_curve(y_val: np.ndarray, probs: np.ndarray, auroc: float, out_path: str) -> None:
    """ROC curve with AUC annotation."""
    fpr, tpr, _ = roc_curve(y_val, probs)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(fpr, tpr, color="#2980b9", lw=2, label=f"Linear Probe (AUC = {auroc:.3f})")
    ax.plot([0, 1], [0, 1], color="#bdc3c7", lw=1, linestyle="--", label="Random")

    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("H-M3 ROC Curve: Linear Correctness Probe")
    ax.legend(loc="lower right")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
