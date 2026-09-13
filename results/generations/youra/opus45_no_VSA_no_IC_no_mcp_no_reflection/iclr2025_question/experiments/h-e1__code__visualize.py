# visualize.py - ROC curves, score distributions, gate comparison
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve
from config import AUROC_THRESHOLD, FIGURES_DIR
import os


def plot_gate_comparison(metrics: dict, threshold: float = AUROC_THRESHOLD,
                         out_path: str = None) -> None:
    """Bar chart comparing AUROC across methods with threshold line."""
    methods = list(metrics.keys())
    aurocs = [metrics[m]["auroc"] for m in methods]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['green' if a > threshold else 'red' for a in aurocs]
    bars = ax.bar(methods, aurocs, color=colors, alpha=0.7, edgecolor='black')
    ax.axhline(y=threshold, color='black', linestyle='--', linewidth=2, label=f'Threshold ({threshold})')
    ax.set_ylabel('AUROC')
    ax.set_xlabel('UQ Method')
    ax.set_title('h-e1: AUROC Gate Comparison')
    ax.set_ylim(0, 1)
    ax.legend()

    for bar, auroc in zip(bars, aurocs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{auroc:.3f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_curves(y_true: list[int], scores: dict[str, list[float]],
                    out_path: str = None) -> None:
    """ROC curves for all methods."""
    fig, ax = plt.subplots(figsize=(8, 8))

    for method, method_scores in scores.items():
        fpr, tpr, _ = roc_curve(y_true, method_scores)
        ax.plot(fpr, tpr, label=method, linewidth=2)

    ax.plot([0, 1], [0, 1], 'k--', label='Random')
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('h-e1: ROC Curves')
    ax.legend(loc='lower right')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=150)
    plt.close()


def plot_score_distributions(y_true: list[int], scores: dict[str, list[float]],
                             out_dir: str = None) -> None:
    """Score distribution histograms per method."""
    y_true = np.array(y_true)

    for method, method_scores in scores.items():
        method_scores = np.array(method_scores)
        fig, ax = plt.subplots(figsize=(8, 5))

        ax.hist(method_scores[y_true == 0], bins=30, alpha=0.5, label='Correct (y=0)', color='green')
        ax.hist(method_scores[y_true == 1], bins=30, alpha=0.5, label='Hallucination (y=1)', color='red')
        ax.set_xlabel('Uncertainty Score')
        ax.set_ylabel('Count')
        ax.set_title(f'h-e1: {method} Score Distribution')
        ax.legend()

        plt.tight_layout()
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            plt.savefig(os.path.join(out_dir, f'{method}_dist.png'), dpi=150)
        plt.close()
