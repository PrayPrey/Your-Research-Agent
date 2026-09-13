"""Visualization for H-M2: consistency-based hallucination detection"""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import config


def plot_gate_metrics(auroc: float, auroc_target: float, p_value: float, out_path: str):
    """Bar chart showing AUROC vs target and p-value status."""
    fig, ax = plt.subplots(figsize=(6, 4))

    bars = ax.bar(['AUROC', 'Target'], [auroc, auroc_target], color=['#2196F3', '#9E9E9E'])
    ax.axhline(auroc_target, color='red', linestyle='--', label=f'Target: {auroc_target}')
    ax.set_ylabel('Score')
    ax.set_title(f'H-M2 Gate Metrics (p={p_value:.4f})')
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_consistency_distribution(consistencies: list[float], correctness: list[bool], out_path: str):
    """Overlaid histograms of consistency for correct vs incorrect."""
    consistencies = np.array(consistencies)
    correctness = np.array(correctness)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(consistencies[correctness], bins=20, alpha=0.6, label='Correct', color='green')
    ax.hist(consistencies[~correctness], bins=20, alpha=0.6, label='Incorrect', color='red')
    ax.set_xlabel('Consistency Score')
    ax.set_ylabel('Count')
    ax.set_title('H-M2: Consistency Distribution by Correctness')
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_curve(consistencies: list[float], correctness: list[bool], out_path: str):
    """ROC curve for consistency predicting correctness."""
    correctness = np.array(correctness).astype(int)
    fpr, tpr, _ = roc_curve(correctness, consistencies)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color='#2196F3', lw=2, label=f'ROC (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--')
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('H-M2: ROC Curve (Consistency)')
    ax.legend(loc='lower right')

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_entropy_vs_consistency(entropies: list[float], consistencies: list[float],
                                 correctness: list[bool], out_path: str):
    """Scatter plot: entropy (x) vs consistency (y), colored by correctness."""
    entropies = np.array(entropies)
    consistencies = np.array(consistencies)
    correctness = np.array(correctness)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(entropies[correctness], consistencies[correctness],
               c='green', alpha=0.6, label='Correct', s=40)
    ax.scatter(entropies[~correctness], consistencies[~correctness],
               c='red', alpha=0.6, label='Incorrect', s=40)
    ax.set_xlabel('Entropy')
    ax.set_ylabel('Consistency')
    ax.set_title('H-M2: Entropy vs Consistency (H-M3 Preview)')
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
