# H-M1 Visualization suite
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc
import os

def plot_box(correct: list[float], incorrect: list[float], out_path: str):
    """Box/violin plot comparing entropy distributions."""
    fig, ax = plt.subplots(figsize=(8, 6))
    data = [correct, incorrect]
    ax.boxplot(data, labels=['Correct', 'Incorrect'])
    ax.set_ylabel('Mean Token Entropy')
    ax.set_title('Entropy Distribution by Correctness')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_histogram_kde(correct: list[float], incorrect: list[float], out_path: str):
    """Overlaid histograms with KDE."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(correct, kde=True, label='Correct', alpha=0.5, ax=ax)
    sns.histplot(incorrect, kde=True, label='Incorrect', alpha=0.5, ax=ax)
    ax.set_xlabel('Mean Token Entropy')
    ax.set_ylabel('Count')
    ax.legend()
    ax.set_title('Entropy Distributions')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()

def plot_roc(entropies: list[float], labels: list[int], out_path: str):
    """ROC curve using entropy as classifier score."""
    fpr, tpr, _ = roc_curve(labels, entropies)
    roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fpr, tpr, label=f'ROC (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--')
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve: Entropy as Incorrectness Predictor')
    ax.legend()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    return roc_auc

def plot_entropy_vs_length(entropies: list[float], lengths: list[int], out_path: str):
    """Scatter plot of entropy vs response length."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(lengths, entropies, alpha=0.5, s=10)
    ax.set_xlabel('Response Length (tokens)')
    ax.set_ylabel('Mean Token Entropy')
    ax.set_title('Entropy vs Response Length')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
