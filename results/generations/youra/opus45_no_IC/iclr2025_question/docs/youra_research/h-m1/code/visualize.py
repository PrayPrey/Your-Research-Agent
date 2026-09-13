"""Visualization for H-M1 results."""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc
from config import FIGURES_DIR
import os


def plot_gate_bar_chart(results: dict, out_path: str = None) -> str:
    """REQUIRED: Bar chart comparing mean entropy with error bars, p-value, Cohen's d."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "gate_bar_chart.png")

    fig, ax = plt.subplots(figsize=(8, 6))

    categories = ['Correct', 'Incorrect']
    means = [results['mean_entropy_correct'], results['mean_entropy_incorrect']]
    stds = [results['std_entropy_correct'], results['std_entropy_incorrect']]
    colors = ['#2ecc71', '#e74c3c']

    bars = ax.bar(categories, means, yerr=stds, capsize=5, color=colors, edgecolor='black')

    ax.set_ylabel('Semantic Entropy (nats)', fontsize=12)
    ax.set_title('H-M1: Semantic Entropy by Correctness', fontsize=14, fontweight='bold')

    # Annotate with statistics
    p_val = results['p_value']
    d_val = results['cohens_d']
    gate = "PASS" if results['gate_passed'] else "FAIL"

    stats_text = f"p = {p_val:.4f}\nCohen's d = {d_val:.3f}\nGate: {gate}"
    ax.annotate(stats_text, xy=(0.95, 0.95), xycoords='axes fraction',
                ha='right', va='top', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_entropy_violin(entropy_correct: np.ndarray, entropy_incorrect: np.ndarray,
                        out_path: str = None) -> str:
    """Violin plot of entropy distributions."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "entropy_violin.png")

    fig, ax = plt.subplots(figsize=(8, 6))

    data = [entropy_correct, entropy_incorrect]
    positions = [1, 2]

    parts = ax.violinplot(data, positions=positions, showmeans=True, showmedians=True)

    # Color the violins
    colors = ['#2ecc71', '#e74c3c']
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)

    ax.set_xticks(positions)
    ax.set_xticklabels(['Correct', 'Incorrect'])
    ax.set_ylabel('Semantic Entropy (nats)', fontsize=12)
    ax.set_title('Entropy Distribution by Correctness', fontsize=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_roc_curve(entropies: np.ndarray, labels: np.ndarray, out_path: str = None) -> str:
    """ROC curve for entropy as incorrectness predictor."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "roc_curve.png")

    fpr, tpr, _ = roc_curve(labels, entropies)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(fpr, tpr, color='#3498db', lw=2, label=f'ROC (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--')

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('ROC: Semantic Entropy as Incorrectness Predictor', fontsize=14)
    ax.legend(loc='lower right')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def generate_all_figures(results: dict, entropy_correct: np.ndarray,
                         entropy_incorrect: np.ndarray) -> list:
    """Generate all required figures."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    figures = []

    # Required: gate bar chart
    fig1 = plot_gate_bar_chart(results)
    figures.append(fig1)
    print(f"Saved: {fig1}")

    # Violin plot
    fig2 = plot_entropy_violin(entropy_correct, entropy_incorrect)
    figures.append(fig2)
    print(f"Saved: {fig2}")

    # ROC curve
    all_entropies = np.concatenate([entropy_correct, entropy_incorrect])
    labels = np.concatenate([np.zeros(len(entropy_correct)), np.ones(len(entropy_incorrect))])
    fig3 = plot_roc_curve(all_entropies, labels)
    figures.append(fig3)
    print(f"Saved: {fig3}")

    return figures
