"""Visualization: gate metrics, entropy distribution, ROC curve"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc
import os


def plot_gate_metrics(auroc: float, auroc_target: float, p_value: float, out_path: str):
    """Bar chart comparing actual vs target metrics."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = [0, 1]
    labels = ['AUROC', 'p-value (log scale)']
    targets = [auroc_target, 0.05]
    actuals = [auroc, p_value]

    width = 0.35
    ax.bar([i - width/2 for i in x], targets, width, label='Target', alpha=0.7)
    ax.bar([i + width/2 for i in x], actuals, width, label='Actual', alpha=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Value')
    ax.set_title('Gate Metrics: Target vs Actual')
    ax.legend()

    # Add pass/fail annotations
    auroc_pass = auroc > auroc_target
    pval_pass = p_value < 0.05
    ax.annotate('PASS' if auroc_pass else 'FAIL', (0, max(auroc, auroc_target) + 0.02),
                ha='center', color='green' if auroc_pass else 'red')
    ax.annotate('PASS' if pval_pass else 'FAIL', (1, max(p_value, 0.05) + 0.02),
                ha='center', color='green' if pval_pass else 'red')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_entropy_distribution(entropies: list[float], correctness: list[bool], out_path: str):
    """Overlapping histograms of entropy by correctness."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    entropies = np.array(entropies)
    correctness = np.array(correctness)

    correct_e = entropies[correctness]
    incorrect_e = entropies[~correctness]

    fig, ax = plt.subplots(figsize=(10, 6))
    bins = np.linspace(min(entropies), max(entropies), 50)

    ax.hist(correct_e, bins=bins, alpha=0.7, label=f'Correct (n={len(correct_e)}, μ={np.mean(correct_e):.4f})')
    ax.hist(incorrect_e, bins=bins, alpha=0.7, label=f'Incorrect (n={len(incorrect_e)}, μ={np.mean(incorrect_e):.4f})')

    ax.set_xlabel('Mean Token Entropy')
    ax.set_ylabel('Count')
    ax.set_title('Entropy Distribution by Correctness')
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_curve(entropies: list[float], correctness: list[bool], out_path: str):
    """ROC curve with AUC annotation."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    y_true = np.array(correctness, dtype=int)
    y_scores = -np.array(entropies)  # low entropy = high confidence = correct

    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(fpr, tpr, lw=2, label=f'ROC (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Random')
    ax.axhline(y=0.55, color='r', linestyle=':', label='Target (0.55)')

    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve: Entropy as Correctness Predictor')
    ax.legend(loc='lower right')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
