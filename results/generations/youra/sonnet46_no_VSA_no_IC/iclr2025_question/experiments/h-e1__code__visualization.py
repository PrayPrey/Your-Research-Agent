"""ROC curves and score histograms."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
from typing import Dict


def plot_roc_curves(
    method_scores: Dict[str, np.ndarray],
    labels: np.ndarray,
    model_key: str,
    dataset_name: str,
    out_dir: str,
) -> None:
    """ROC curves for all 3 aggregation methods overlaid."""
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    colors = {"min": "tab:blue", "mean": "tab:orange", "sum": "tab:green"}

    for method, scores in method_scores.items():
        if len(np.unique(labels)) < 2:
            continue
        fpr, tpr, _ = roc_curve(labels, scores)
        from sklearn.metrics import roc_auc_score
        auc = roc_auc_score(labels, scores)
        ax.plot(fpr, tpr, color=colors[method], label=f"{method} (AUC={auc:.3f})", lw=1.5)

    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")
    ax.set_title(f"ROC: {model_key} / {dataset_name}")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(out_dir, f"roc_{model_key}_{dataset_name}.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_score_histograms(
    scores: np.ndarray,
    labels: np.ndarray,
    model_key: str,
    dataset_name: str,
    method: str,
    out_dir: str,
) -> None:
    """Score histogram split by correct/hallucinated."""
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    correct = scores[labels == 1]
    hallu = scores[labels == 0]
    bins = np.linspace(scores.min(), scores.max(), 40)
    ax.hist(correct, bins=bins, alpha=0.6, label="correct", color="tab:blue", density=True)
    ax.hist(hallu, bins=bins, alpha=0.6, label="hallucinated", color="tab:red", density=True)
    ax.set_xlabel("Score (negated log-prob)")
    ax.set_ylabel("Density")
    ax.set_title(f"Score dist: {model_key}/{dataset_name}/{method}")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(out_dir, f"hist_{model_key}_{dataset_name}_{method}.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
