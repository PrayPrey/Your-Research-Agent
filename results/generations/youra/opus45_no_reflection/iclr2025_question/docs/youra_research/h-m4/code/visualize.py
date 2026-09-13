"""H-M4 Visualization: Gate comparison, ROC, distributions, scatter."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_gate_comparison(aurocs: dict, threshold: float, out_path: str) -> None:
    """Bar chart comparing AUROCs with threshold line."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    methods = ["Probe", "Token Entropy", "Seq NLL"]
    values = [aurocs["probe_auroc"], aurocs["entropy_auroc"], aurocs["nll_auroc"]]
    colors = ["#2ecc71", "#e74c3c", "#e74c3c"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(methods, values, color=colors, edgecolor="black")

    # Add delta annotations
    delta_e = aurocs["probe_auroc"] - aurocs["entropy_auroc"]
    delta_n = aurocs["probe_auroc"] - aurocs["nll_auroc"]
    ax.annotate(f"+{delta_e:.3f}", xy=(0.5, max(values) + 0.02), fontsize=10, ha='center')
    ax.annotate(f"+{delta_n:.3f}", xy=(1.5, max(values) + 0.02), fontsize=10, ha='center')

    ax.axhline(y=aurocs["probe_auroc"] - threshold, color='red', linestyle='--',
               label=f'Gate threshold (Probe - {threshold})')

    ax.set_ylabel("AUROC")
    ax.set_title("H-M4: Probe vs Output-Level Baselines")
    ax.set_ylim(0, 1.0)
    ax.legend()

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_overlay(curves: dict, out_path: str) -> None:
    """ROC curves for all methods."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 7))

    colors = {"probe": "#2ecc71", "entropy": "#3498db", "nll": "#e74c3c"}
    labels = {"probe": "Probe", "entropy": "Token Entropy", "nll": "Seq NLL"}

    for name, data in curves.items():
        ax.plot(data["fpr"], data["tpr"], color=colors[name], lw=2, label=labels[name])

    ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Random')
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves: Correctness Prediction")
    ax.legend(loc="lower right")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_confidence_distributions(labels: np.ndarray, probe_scores: np.ndarray,
                                   entropy_scores: np.ndarray, out_path: str) -> None:
    """Histogram of confidence scores by correctness."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    correct_mask = labels == 1
    incorrect_mask = labels == 0

    # Probe
    axes[0].hist(probe_scores[correct_mask], bins=30, alpha=0.7, label='Correct', color='#2ecc71')
    axes[0].hist(probe_scores[incorrect_mask], bins=30, alpha=0.7, label='Incorrect', color='#e74c3c')
    axes[0].set_xlabel("Probe Score")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Probe Confidence Distribution")
    axes[0].legend()

    # Entropy (negated, so higher = more confident)
    axes[1].hist(entropy_scores[correct_mask], bins=30, alpha=0.7, label='Correct', color='#2ecc71')
    axes[1].hist(entropy_scores[incorrect_mask], bins=30, alpha=0.7, label='Incorrect', color='#e74c3c')
    axes[1].set_xlabel("Neg. Token Entropy")
    axes[1].set_ylabel("Count")
    axes[1].set_title("Token Entropy Distribution")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_score_scatter(probe_scores: np.ndarray, entropy_scores: np.ndarray,
                       labels: np.ndarray, out_path: str) -> None:
    """Scatter plot of probe vs entropy, colored by correctness."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 7))

    correct_mask = labels == 1
    incorrect_mask = labels == 0

    ax.scatter(entropy_scores[incorrect_mask], probe_scores[incorrect_mask],
               c='#e74c3c', alpha=0.5, label='Incorrect', s=20)
    ax.scatter(entropy_scores[correct_mask], probe_scores[correct_mask],
               c='#2ecc71', alpha=0.5, label='Correct', s=20)

    ax.set_xlabel("Neg. Token Entropy")
    ax.set_ylabel("Probe Score")
    ax.set_title("Probe vs Token Entropy by Correctness")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
