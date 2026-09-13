"""
Visualization utilities for experiment results
"""
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10


def plot_calibration_curve(confidences: np.ndarray,
                            correctness: np.ndarray,
                            title: str = "Calibration Curve",
                            save_path: str = None,
                            n_bins: int = 10):
    """
    Plot reliability diagram (calibration curve)
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left plot: Calibration curve
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]

    bin_confidences = []
    bin_accuracies = []
    bin_counts = []

    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(correctness[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            count_in_bin = np.sum(in_bin)

            bin_confidences.append(avg_confidence_in_bin)
            bin_accuracies.append(accuracy_in_bin)
            bin_counts.append(count_in_bin)
        else:
            bin_confidences.append((bin_lower + bin_upper) / 2)
            bin_accuracies.append(0)
            bin_counts.append(0)

    # Plot calibration curve
    ax1.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration', linewidth=2)
    ax1.plot(bin_confidences, bin_accuracies, 'o-', label='Model', linewidth=2, markersize=8)
    ax1.set_xlabel('Confidence', fontsize=12)
    ax1.set_ylabel('Accuracy', fontsize=12)
    ax1.set_title(f'{title}', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 1])
    ax1.set_ylim([0, 1])

    # Right plot: Histogram of confidence distribution
    ax2.hist(confidences, bins=n_bins, alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Confidence', fontsize=12)
    ax2.set_ylabel('Count', fontsize=12)
    ax2.set_title('Confidence Distribution', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved calibration curve to {save_path}")

    plt.close()


def plot_method_comparison(results: Dict[str, Dict[str, float]],
                            save_path: str = None):
    """
    Compare different methods across multiple metrics
    """
    methods = list(results.keys())
    metrics = ['ece', 'brier_score', 'auroc', 'auprc', 'sharpness']
    metric_labels = ['ECE ↓', 'Brier Score ↓', 'AUROC ↑', 'AUPRC ↑', 'Sharpness']

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
        ax = axes[idx]

        values = [results[method][metric] for method in methods]

        # Create bar plot
        bars = ax.bar(range(len(methods)), values, alpha=0.7, edgecolor='black')

        # Color bars
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(methods)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        ax.set_xticks(range(len(methods)))
        ax.set_xticklabels(methods, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel(label, fontsize=11, fontweight='bold')
        ax.set_title(f'{label}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{val:.3f}',
                    ha='center', va='bottom', fontsize=8)

    # Remove extra subplot
    fig.delaxes(axes[-1])

    plt.suptitle('Method Comparison Across Metrics', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved comparison plot to {save_path}")

    plt.close()


def plot_selective_prediction(confidences: np.ndarray,
                               correctness: np.ndarray,
                               title: str = "Selective Prediction",
                               save_path: str = None):
    """
    Plot accuracy vs coverage for selective prediction
    """
    # Sort by confidence (descending)
    sorted_indices = np.argsort(confidences)[::-1]
    sorted_correctness = correctness[sorted_indices]

    # Compute cumulative accuracy at different coverage levels
    coverage_levels = np.linspace(0.1, 1.0, 50)
    accuracies = []

    for coverage in coverage_levels:
        n_samples = int(len(sorted_correctness) * coverage)
        if n_samples > 0:
            acc = np.mean(sorted_correctness[:n_samples])
            accuracies.append(acc)
        else:
            accuracies.append(0)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(coverage_levels * 100, accuracies, 'o-', linewidth=2, markersize=6)
    ax.axhline(y=np.mean(correctness), color='r', linestyle='--',
               label=f'Full Dataset Accuracy ({np.mean(correctness):.3f})', linewidth=2)

    ax.set_xlabel('Coverage (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 100])
    ax.set_ylim([0, 1])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved selective prediction plot to {save_path}")

    plt.close()


def plot_confidence_distribution_by_correctness(confidences: np.ndarray,
                                                 correctness: np.ndarray,
                                                 title: str = "Confidence Distribution",
                                                 save_path: str = None):
    """
    Plot confidence distributions for correct vs incorrect predictions
    """
    correct_confidences = confidences[correctness == 1]
    incorrect_confidences = confidences[correctness == 0]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(correct_confidences, bins=20, alpha=0.6, label='Correct', color='green', edgecolor='black')
    ax.hist(incorrect_confidences, bins=20, alpha=0.6, label='Incorrect', color='red', edgecolor='black')

    ax.set_xlabel('Confidence', fontsize=12, fontweight='bold')
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved confidence distribution plot to {save_path}")

    plt.close()


def plot_training_curves(train_losses: List[float],
                          val_losses: List[float],
                          save_path: str = None):
    """
    Plot training and validation loss curves
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    epochs = range(1, len(train_losses) + 1)
    ax.plot(epochs, train_losses, 'o-', label='Train Loss', linewidth=2, markersize=5)
    ax.plot(epochs, val_losses, 's-', label='Val Loss', linewidth=2, markersize=5)

    ax.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax.set_ylabel('Loss', fontsize=12, fontweight='bold')
    ax.set_title('Training and Validation Loss', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved training curves to {save_path}")

    plt.close()


def create_results_summary_table(results: Dict[str, Dict[str, float]]) -> str:
    """
    Create a markdown table summarizing results
    """
    methods = list(results.keys())
    metrics = ['ece', 'brier_score', 'auroc', 'auprc', 'selective_acc_80', 'selective_acc_90']
    metric_names = ['ECE', 'Brier Score', 'AUROC', 'AUPRC', 'Sel. Acc@80%', 'Sel. Acc@90%']

    # Create header
    table = "| Method | " + " | ".join(metric_names) + " |\n"
    table += "|" + "---|" * (len(metrics) + 1) + "\n"

    # Add rows
    for method in methods:
        row = f"| {method} |"
        for metric in metrics:
            value = results[method].get(metric, 0.0)
            row += f" {value:.4f} |"
        table += row + "\n"

    return table
