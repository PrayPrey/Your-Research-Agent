"""Visualization functions for h-m1 experiment."""
import numpy as np
import matplotlib.pyplot as plt
from typing import List


def plot_threshold_curve(thresholds: List[float], accuracies: List[float],
                        best_threshold: float, save_path: str) -> None:
    """Plot 101-point accuracy vs threshold with best marker."""
    plt.figure(figsize=(10, 6))
    plt.plot(thresholds, accuracies, 'b-', linewidth=2, label='Training Accuracy')

    best_idx = thresholds.index(best_threshold)
    plt.scatter([best_threshold], [accuracies[best_idx]],
                c='red', s=100, zorder=5, label=f'Best Threshold = {best_threshold:.3f}')

    plt.xlabel('Entropy Threshold', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    plt.title('Threshold Grid Search: Training Accuracy', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_confusion_matrix(cm: np.ndarray, save_path: str) -> None:
    """2x2 heatmap with counts."""
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, cmap='Blues', interpolation='nearest')

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Entity-Error', 'Non-Entity-Error'])
    ax.set_yticklabels(['Entity-Error', 'Non-Entity-Error'])

    for i in range(2):
        for j in range(2):
            text = ax.text(j, i, str(cm[i][j]), ha="center", va="center",
                          color="white" if cm[i][j] > cm.max() / 2 else "black", fontsize=18)

    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('True', fontsize=12)
    ax.set_title('Confusion Matrix (Test Set)', fontsize=14)
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_entropy_distribution(entity_vals: List[float], non_entity_vals: List[float],
                              threshold: float, save_path: str) -> None:
    """Overlaid histograms + vertical threshold line."""
    plt.figure(figsize=(10, 6))
    plt.hist(entity_vals, bins=20, alpha=0.5, label='Entity-Error', color='blue')
    plt.hist(non_entity_vals, bins=20, alpha=0.5, label='Non-Entity-Error', color='orange')
    plt.axvline(threshold, color='red', linestyle='--', linewidth=2,
                label=f'Threshold = {threshold:.3f}')

    plt.xlabel('Attention Entropy', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Entropy Distribution by Error Type', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
