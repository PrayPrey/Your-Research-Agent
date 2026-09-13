"""Visualization for experiment results."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from config import FIGURES_DIR


def plot_gate_metrics(baseline_f1: float, proposed_f1: float, threshold: float, out_dir: str = FIGURES_DIR):
    """Bar chart comparing baseline, proposed, and threshold."""
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(['Baseline', 'Proposed', 'Threshold'], [baseline_f1, proposed_f1, threshold],
                  color=['gray', 'steelblue', 'red'], alpha=0.8)
    ax.axhline(y=threshold, color='red', linestyle='--', label=f'Gate: {threshold}')
    ax.set_ylabel('Macro-F1')
    ax.set_title('H-E0 Gate Metrics: Linear Separability of Instruction Prefixes')
    ax.set_ylim(0, 1)
    for bar, val in zip(bars, [baseline_f1, proposed_f1, threshold]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{val:.3f}',
                ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'gate_metrics.png'), dpi=150)
    plt.close()


def plot_confusion_matrix(y_true: list, y_pred: list, labels: list, out_dir: str = FIGURES_DIR):
    """Confusion matrix heatmap."""
    os.makedirs(out_dir, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(12, 10))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(ax=ax, cmap='Blues', xticks_rotation=45)
    ax.set_title('H-E0: Task Family Classification Confusion Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'confusion_matrix.png'), dpi=150)
    plt.close()


def plot_tsne_embeddings(embeddings: np.ndarray, labels: list, out_dir: str = FIGURES_DIR):
    """t-SNE visualization of embeddings colored by task family."""
    os.makedirs(out_dir, exist_ok=True)
    n_samples = min(2000, len(embeddings))
    idx = np.random.choice(len(embeddings), n_samples, replace=False)
    emb_subset = embeddings[idx]
    labels_subset = [labels[i] for i in idx]

    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    emb_2d = tsne.fit_transform(emb_subset)

    unique_labels = list(set(labels_subset))
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_labels)))
    label_to_color = {l: c for l, c in zip(unique_labels, colors)}

    fig, ax = plt.subplots(figsize=(12, 10))
    for label in unique_labels:
        mask = [l == label for l in labels_subset]
        ax.scatter(emb_2d[mask, 0], emb_2d[mask, 1], c=[label_to_color[label]],
                   label=label[:20], alpha=0.6, s=10)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.set_title('H-E0: t-SNE of Instruction Prefix Embeddings')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'tsne_embeddings.png'), dpi=150)
    plt.close()


def plot_per_family_f1(report: dict, out_dir: str = FIGURES_DIR):
    """Bar chart of F1 score per task family."""
    os.makedirs(out_dir, exist_ok=True)
    families = [k for k in report.keys() if k not in ['accuracy', 'macro avg', 'weighted avg']]
    f1_scores = [report[f]['f1-score'] for f in families]

    sorted_pairs = sorted(zip(families, f1_scores), key=lambda x: x[1], reverse=True)
    families, f1_scores = zip(*sorted_pairs)

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(range(len(families)), f1_scores, color='steelblue', alpha=0.8)
    ax.set_yticks(range(len(families)))
    ax.set_yticklabels([f[:30] for f in families], fontsize=8)
    ax.set_xlabel('F1 Score')
    ax.set_title('H-E0: Per-Family F1 Scores')
    ax.axvline(x=0.75, color='red', linestyle='--', label='Gate: 0.75')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'per_family_f1.png'), dpi=150)
    plt.close()
