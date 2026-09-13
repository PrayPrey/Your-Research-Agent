"""Visualization for H-M3 fusion analysis."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc


def plot_gate_metrics(auroc_entropy: float, auroc_consistency: float, auroc_combined: float, out_path: str):
    """Bar chart of 3 AUROC values."""
    fig, ax = plt.subplots(figsize=(8, 5))
    names = ["Entropy-only", "Consistency-only", "Combined"]
    values = [auroc_entropy, auroc_consistency, auroc_combined]
    colors = ["#4a90d9", "#50c878", "#ff6b6b"]

    bars = ax.bar(names, values, color=colors, edgecolor="black")
    ax.set_ylabel("AUROC")
    ax.set_title("H-M3 Gate Metrics: Fusion vs Single Metrics")
    ax.set_ylim(0, 1)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", fontsize=11)

    ax.axhline(0.5, color="gray", linestyle="--", label="Random")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_overlay(labels: np.ndarray, entropy_scores: np.ndarray,
                     consistency_scores: np.ndarray, combined_scores: np.ndarray, out_path: str):
    """Overlay ROC curves for 3 scoring methods."""
    fig, ax = plt.subplots(figsize=(8, 8))

    for scores, name, color in [
        (entropy_scores, "Entropy-only", "#4a90d9"),
        (consistency_scores, "Consistency-only", "#50c878"),
        (combined_scores, "Combined", "#ff6b6b"),
    ]:
        fpr, tpr, _ = roc_curve(labels, scores)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=color, lw=2, label=f"{name} (AUC={roc_auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("H-M3: ROC Curves Comparison")
    ax.legend(loc="lower right")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_weight_heatmap(alpha_range: list, beta_range: list, auroc_grid: np.ndarray, out_path: str):
    """Heatmap of AUROC as f(alpha, beta)."""
    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(auroc_grid, origin="lower", cmap="RdYlGn", aspect="auto",
                   extent=[beta_range[0]-0.05, beta_range[-1]+0.05,
                           alpha_range[0]-0.05, alpha_range[-1]+0.05])

    ax.set_xlabel("Beta (consistency weight)")
    ax.set_ylabel("Alpha (confidence weight)")
    ax.set_title("H-M3: AUROC Heatmap over Weight Grid")

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("AUROC")

    # Mark best
    best_idx = np.unravel_index(np.argmax(auroc_grid), auroc_grid.shape)
    best_alpha = alpha_range[best_idx[0]]
    best_beta = beta_range[best_idx[1]]
    ax.scatter([best_beta], [best_alpha], marker="*", s=200, c="black", zorder=10)
    ax.annotate(f"Best: α={best_alpha}, β={best_beta}",
                (best_beta, best_alpha), xytext=(10, 10), textcoords="offset points",
                fontsize=10, color="black")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_entropy_vs_consistency(entropies: np.ndarray, consistencies: np.ndarray,
                                correctness: np.ndarray, out_path: str):
    """Scatter plot: entropy vs consistency, colored by correctness."""
    fig, ax = plt.subplots(figsize=(8, 6))

    correct_mask = correctness.astype(bool)
    ax.scatter(entropies[correct_mask], consistencies[correct_mask],
               c="#50c878", label="Correct", alpha=0.7, s=60, edgecolors="black")
    ax.scatter(entropies[~correct_mask], consistencies[~correct_mask],
               c="#ff6b6b", label="Incorrect", alpha=0.7, s=60, edgecolors="black")

    ax.set_xlabel("Entropy")
    ax.set_ylabel("Consistency")
    ax.set_title("H-M3: Entropy vs Consistency by Correctness")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
