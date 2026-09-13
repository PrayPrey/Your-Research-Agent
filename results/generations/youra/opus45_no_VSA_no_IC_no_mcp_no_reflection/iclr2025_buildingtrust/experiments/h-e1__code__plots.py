import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve

def plot_gate_comparison(results: dict, threshold: float, out_path: str) -> None:
    methods = ["semantic_entropy", "self_consistency"]
    datasets = list(results.keys())
    x = np.arange(len(datasets))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, method in enumerate(methods):
        vals = [results[d][method]["auroc"] for d in datasets]
        ax.bar(x + i * width, vals, width, label=method.replace("_", " ").title())
    ax.axhline(y=threshold, color="r", linestyle="--", label=f"Gate threshold ({threshold})")
    ax.set_ylabel("AUROC")
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(datasets)
    ax.legend()
    ax.set_title("Gate Comparison: AUROC by Method and Dataset")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_roc_curves(results: dict, all_labels: dict, all_scores: dict, out_path: str) -> None:
    fig, axes = plt.subplots(1, len(results), figsize=(6 * len(results), 5))
    if len(results) == 1:
        axes = [axes]
    for ax, dataset in zip(axes, results.keys()):
        for method in ["semantic_entropy", "self_consistency"]:
            y_true = all_labels[dataset]
            scores = all_scores[dataset][method]
            fpr, tpr, _ = roc_curve(y_true, scores)
            auroc = results[dataset][method]["auroc"]
            ax.plot(fpr, tpr, label=f"{method.replace('_', ' ').title()} (AUROC={auroc:.3f})")
        ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
        ax.set_xlabel("FPR")
        ax.set_ylabel("TPR")
        ax.set_title(dataset)
        ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_score_distributions(all_scores: dict, all_labels: dict, out_path: str) -> None:
    fig, axes = plt.subplots(2, len(all_scores), figsize=(6 * len(all_scores), 8))
    if len(all_scores) == 1:
        axes = axes.reshape(-1, 1)
    methods = ["semantic_entropy", "self_consistency"]
    for j, dataset in enumerate(all_scores.keys()):
        labels = all_labels[dataset]
        for i, method in enumerate(methods):
            ax = axes[i, j]
            scores = all_scores[dataset][method]
            ax.hist(scores[labels == 0], bins=30, alpha=0.6, label="Truthful", density=True)
            ax.hist(scores[labels == 1], bins=30, alpha=0.6, label="Hallucinated", density=True)
            ax.set_title(f"{dataset} - {method.replace('_', ' ').title()}")
            ax.set_xlabel("Score")
            ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
