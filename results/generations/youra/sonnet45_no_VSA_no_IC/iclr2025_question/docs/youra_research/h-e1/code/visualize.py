"""Visualization for UQ experiment results."""
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np


def plot_auroc_comparison(
    auroc_scores: Dict[str, float],
    threshold: float,
    save_path: str
):
    """
    Plot AUROC comparison bar chart.

    Args:
        auroc_scores: {method_name: auroc} dictionary
        threshold: AUROC threshold (0.70)
        save_path: Path to save figure
    """
    methods = list(auroc_scores.keys())
    scores = list(auroc_scores.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(methods, scores, color='skyblue')
    ax.axhline(threshold, color='red', linestyle='--', label=f'Threshold ({threshold})')
    ax.set_xlabel('UQ Method')
    ax.set_ylabel('AUROC')
    ax.set_title('AUROC Comparison Across UQ Methods')
    ax.set_ylim(0.5, 1.0)
    ax.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_uncertainty_distributions(
    test_data: List[Dict],
    uncertainties_by_method: Dict[str, List[float]],
    save_path: str
):
    """
    Plot uncertainty distributions for correct vs incorrect answers.

    Args:
        test_data: List of test question dicts with labels
        uncertainties_by_method: {method_name: [uncertainties]} dictionary
        save_path: Path to save figure
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    labels = [q.get("label", 0) for q in test_data]

    for idx, (method, uncertainties) in enumerate(uncertainties_by_method.items()):
        ax = axes[idx]

        correct = [u for u, l in zip(uncertainties, labels) if l == 0]
        incorrect = [u for u, l in zip(uncertainties, labels) if l == 1]

        ax.hist(correct, bins=30, alpha=0.6, label='Correct', color='blue')
        ax.hist(incorrect, bins=30, alpha=0.6, label='Incorrect', color='red')
        ax.set_xlabel('Uncertainty')
        ax.set_ylabel('Frequency')
        ax.set_title(f'{method}')
        ax.legend()

    plt.suptitle('Uncertainty Distributions: Correct vs Incorrect')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_roc_curves(fpr_tpr_by_method: Dict, save_path: str):
    """
    Plot ROC curves for all UQ methods.

    Args:
        fpr_tpr_by_method: {method_name: {fpr: [...], tpr: [...]}} dictionary
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    for method, data in fpr_tpr_by_method.items():
        ax.plot(data["fpr"], data["tpr"], label=method)

    ax.plot([0, 1], [0, 1], 'k--', label='Random')
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curves for Selective Prediction')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
