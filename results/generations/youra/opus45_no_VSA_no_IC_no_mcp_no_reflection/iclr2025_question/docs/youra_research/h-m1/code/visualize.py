# visualize.py - Visualization for h-m1 results
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
import numpy as np


def plot_auroc_comparison(aurocs: dict[str, float], out_path: str) -> None:
    """Bar chart comparing AUROC across methods."""
    methods = list(aurocs.keys())
    values = [aurocs[m] for m in methods]
    plt.figure(figsize=(8, 5))
    bars = plt.bar(methods, values, color=['#2ecc71' if m == 'semantic_entropy' else '#3498db' for m in methods])
    plt.axhline(y=0.70, color='r', linestyle='--', label='Gate threshold (0.70)')
    plt.ylabel('AUROC')
    plt.title('h-m1: Semantic Entropy vs Baselines')
    plt.ylim(0, 1)
    for bar, v in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, v + 0.02, f'{v:.3f}', ha='center')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_cluster_histogram(results: list[dict], out_path: str) -> None:
    """Histogram of num_clusters across questions."""
    clusters = [r["num_clusters"] for r in results]
    plt.figure(figsize=(8, 5))
    plt.hist(clusters, bins=range(1, max(clusters)+2), edgecolor='black', alpha=0.7)
    plt.xlabel('Number of Clusters')
    plt.ylabel('Count')
    plt.title(f'Cluster Distribution (avg={np.mean(clusters):.2f})')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_score_correlation(semantic_scores: list[float], other_scores: list[float],
                           other_label: str, out_path: str) -> None:
    """Scatter plot of semantic entropy vs another method."""
    plt.figure(figsize=(6, 6))
    plt.scatter(other_scores, semantic_scores, alpha=0.5, s=10)
    plt.xlabel(other_label)
    plt.ylabel('Semantic Entropy')
    plt.title(f'Correlation: Semantic Entropy vs {other_label}')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_overlay(y_true: list[int], scores: dict[str, list[float]], out_path: str) -> None:
    """ROC curves for all methods."""
    plt.figure(figsize=(8, 8))
    for method, method_scores in scores.items():
        if len(method_scores) == len(y_true):
            fpr, tpr, _ = roc_curve(y_true, method_scores)
            plt.plot(fpr, tpr, label=method)
    plt.plot([0, 1], [0, 1], 'k--', label='Random')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
