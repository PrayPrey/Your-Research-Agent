"""Visualization module."""
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
from config import EXPERIMENT_CONFIG


def plot_gate_metrics(
    baseline_diff: float,
    rotation_diff: float,
    save_path: str,
    threshold: float = 0.02
) -> None:
    """Plot gate metrics comparison (mandatory figure).

    Args:
        baseline_diff: Baseline differential effect
        rotation_diff: Rotation differential effect
        save_path: Path to save figure
        threshold: Success threshold line (2%)
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    conditions = ['Baseline', 'Rotation']
    values = [abs(baseline_diff), abs(rotation_diff)]

    bars = ax.bar(conditions, values, color=['blue', 'orange'], alpha=0.7)
    ax.axhline(y=threshold, color='red', linestyle='--', label=f'Threshold ({threshold:.2%})')

    ax.set_ylabel('|Differential Effect| (Asymmetric - Symmetric Accuracy)')
    ax.set_title('H-C1 Gate Metrics: Rotation Differential Effect vs Baseline')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}',
                ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_per_class_accuracy(
    baseline_per_class: Dict[int, float],
    rotation_per_class: Dict[int, float],
    save_path: str
) -> None:
    """Plot per-class accuracy comparison.

    Args:
        baseline_per_class: Baseline accuracies {0-9: acc}
        rotation_per_class: Rotation accuracies {0-9: acc}
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    classes = list(range(10))
    baseline_acc = [baseline_per_class[i] for i in classes]
    rotation_acc = [rotation_per_class[i] for i in classes]

    x = np.arange(len(classes))
    width = 0.35

    # Add background shading
    symmetric_digits = EXPERIMENT_CONFIG["symmetric_digits"]
    for digit in symmetric_digits:
        ax.axvspan(digit - 0.5, digit + 0.5, alpha=0.1, color='blue')

    bars1 = ax.bar(x - width/2, baseline_acc, width, label='Baseline', color='blue', alpha=0.7)
    bars2 = ax.bar(x + width/2, rotation_acc, width, label='Rotation', color='orange', alpha=0.7)

    ax.set_xlabel('Digit Class')
    ax.set_ylabel('Test Accuracy')
    ax.set_title('Per-Class Accuracy Comparison (Symmetric: 0,1,8 shaded)')
    ax.set_xticks(x)
    ax.set_xticklabels(classes)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_training_curves(
    baseline_history: Dict[str, List[float]],
    rotation_history: Dict[str, List[float]],
    save_path: str
) -> None:
    """Plot training curves for both conditions.

    Args:
        baseline_history: {'train_loss': [...], 'val_loss': [...], 'val_acc': [...]}
        rotation_history: Same structure
        save_path: Path to save figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Baseline train loss
    axes[0, 0].plot(baseline_history['train_loss'], label='Baseline Train Loss', color='blue')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].set_title('Baseline Training Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    # Baseline val loss
    axes[0, 1].plot(baseline_history['val_loss'], label='Baseline Val Loss', color='blue')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].set_title('Baseline Validation Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    # Rotation train loss
    axes[1, 0].plot(rotation_history['train_loss'], label='Rotation Train Loss', color='orange')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('Loss')
    axes[1, 0].set_title('Rotation Training Loss')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    # Rotation val loss
    axes[1, 1].plot(rotation_history['val_loss'], label='Rotation Val Loss', color='orange')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('Loss')
    axes[1, 1].set_title('Rotation Validation Loss')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
