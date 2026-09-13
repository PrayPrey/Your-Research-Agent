"""Evaluation metrics for hallucination detection and uncertainty calibration."""

import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_recall_curve,
    roc_curve, accuracy_score, f1_score, confusion_matrix
)
import matplotlib.pyplot as plt
import json


def compute_auroc(y_true: np.ndarray, y_scores: np.ndarray) -> float:
    """Compute Area Under ROC Curve."""
    try:
        return roc_auc_score(y_true, y_scores)
    except:
        return 0.5


def compute_auprc(y_true: np.ndarray, y_scores: np.ndarray) -> float:
    """Compute Area Under Precision-Recall Curve."""
    try:
        return average_precision_score(y_true, y_scores)
    except:
        return 0.5


def compute_ece(y_true: np.ndarray, y_probs: np.ndarray, num_bins: int = 10) -> float:
    """
    Compute Expected Calibration Error.

    Args:
        y_true: True binary labels
        y_probs: Predicted probabilities
        num_bins: Number of bins for calibration

    Returns:
        ECE value
    """
    bin_boundaries = np.linspace(0, 1, num_bins + 1)
    ece = 0.0
    total_samples = len(y_true)

    for i in range(num_bins):
        bin_mask = (y_probs >= bin_boundaries[i]) & (y_probs < bin_boundaries[i + 1])
        if i == num_bins - 1:
            bin_mask = (y_probs >= bin_boundaries[i]) & (y_probs <= bin_boundaries[i + 1])

        bin_size = bin_mask.sum()
        if bin_size > 0:
            bin_accuracy = y_true[bin_mask].mean()
            bin_confidence = y_probs[bin_mask].mean()
            ece += (bin_size / total_samples) * abs(bin_accuracy - bin_confidence)

    return ece


def compute_brier_score(y_true: np.ndarray, y_probs: np.ndarray) -> float:
    """Compute Brier Score."""
    return np.mean((y_probs - y_true) ** 2)


def selective_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    uncertainty: np.ndarray,
    coverage: float
) -> float:
    """
    Compute accuracy on the most confident predictions.

    Args:
        y_true: True labels
        y_pred: Predicted labels
        uncertainty: Uncertainty scores (lower = more confident)
        coverage: Fraction of samples to include

    Returns:
        Accuracy on selected samples
    """
    n_select = max(1, int(len(y_true) * coverage))
    sorted_indices = np.argsort(uncertainty)[:n_select]

    return accuracy_score(y_true[sorted_indices], y_pred[sorted_indices])


def compute_all_metrics(
    hallucination_labels: np.ndarray,
    uncertainty_scores: np.ndarray,
    predictions: np.ndarray = None,
    num_bins: int = 10
) -> Dict[str, float]:
    """
    Compute all evaluation metrics.

    Args:
        hallucination_labels: Binary labels (1 = hallucination)
        uncertainty_scores: Predicted uncertainty scores
        predictions: Optional predicted labels
        num_bins: Number of bins for ECE

    Returns:
        Dictionary of metrics
    """
    metrics = {}

    # AUROC and AUPRC for hallucination detection
    metrics["auroc"] = compute_auroc(hallucination_labels, uncertainty_scores)
    metrics["auprc"] = compute_auprc(hallucination_labels, uncertainty_scores)

    # Calibration metrics
    # Treat uncertainty as probability of hallucination
    metrics["ece"] = compute_ece(hallucination_labels, uncertainty_scores, num_bins)
    metrics["brier_score"] = compute_brier_score(hallucination_labels, uncertainty_scores)

    # Selective accuracy at different coverage levels
    if predictions is not None:
        for coverage in [0.5, 0.7, 0.9]:
            metrics[f"selective_acc_{int(coverage*100)}"] = selective_accuracy(
                hallucination_labels, predictions, uncertainty_scores, coverage
            )

    return metrics


def plot_roc_curve(
    results_dict: Dict[str, Dict],
    save_path: str = "roc_curve.png"
):
    """Plot ROC curves for multiple methods."""
    plt.figure(figsize=(8, 6))

    colors = plt.cm.Set2(np.linspace(0, 1, len(results_dict)))

    for (method_name, results), color in zip(results_dict.items(), colors):
        y_true = np.array(results["labels"])
        y_scores = np.array(results["scores"])

        fpr, tpr, _ = roc_curve(y_true, y_scores)
        auc = compute_auroc(y_true, y_scores)

        plt.plot(fpr, tpr, color=color, lw=2, label=f"{method_name} (AUC={auc:.3f})")

    plt.plot([0, 1], [0, 1], 'k--', lw=1)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curves for Hallucination Detection', fontsize=14)
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_precision_recall_curve(
    results_dict: Dict[str, Dict],
    save_path: str = "pr_curve.png"
):
    """Plot Precision-Recall curves for multiple methods."""
    plt.figure(figsize=(8, 6))

    colors = plt.cm.Set2(np.linspace(0, 1, len(results_dict)))

    for (method_name, results), color in zip(results_dict.items(), colors):
        y_true = np.array(results["labels"])
        y_scores = np.array(results["scores"])

        precision, recall, _ = precision_recall_curve(y_true, y_scores)
        auprc = compute_auprc(y_true, y_scores)

        plt.plot(recall, precision, color=color, lw=2, label=f"{method_name} (AUPRC={auprc:.3f})")

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('Precision-Recall Curves for Hallucination Detection', fontsize=14)
    plt.legend(loc="lower left", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_calibration_curve(
    results_dict: Dict[str, Dict],
    num_bins: int = 10,
    save_path: str = "calibration_curve.png"
):
    """Plot calibration curves for multiple methods."""
    plt.figure(figsize=(8, 6))

    colors = plt.cm.Set2(np.linspace(0, 1, len(results_dict)))
    bin_centers = np.linspace(1/(2*num_bins), 1 - 1/(2*num_bins), num_bins)

    for (method_name, results), color in zip(results_dict.items(), colors):
        y_true = np.array(results["labels"])
        y_scores = np.array(results["scores"])

        bin_accuracies = []
        bin_boundaries = np.linspace(0, 1, num_bins + 1)

        for i in range(num_bins):
            bin_mask = (y_scores >= bin_boundaries[i]) & (y_scores < bin_boundaries[i + 1])
            if i == num_bins - 1:
                bin_mask = (y_scores >= bin_boundaries[i]) & (y_scores <= bin_boundaries[i + 1])

            if bin_mask.sum() > 0:
                bin_accuracies.append(y_true[bin_mask].mean())
            else:
                bin_accuracies.append(np.nan)

        ece = compute_ece(y_true, y_scores, num_bins)
        plt.plot(bin_centers, bin_accuracies, 'o-', color=color, lw=2,
                 label=f"{method_name} (ECE={ece:.3f})", markersize=6)

    plt.plot([0, 1], [0, 1], 'k--', lw=1, label="Perfect calibration")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('Predicted Probability', fontsize=12)
    plt.ylabel('Actual Proportion', fontsize=12)
    plt.title('Calibration Curves', fontsize=14)
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_confusion_matrices(
    results_dict: Dict[str, Dict],
    threshold: float = 0.5,
    save_path: str = "confusion_matrices.png"
):
    """Plot confusion matrices for multiple methods."""
    num_methods = len(results_dict)
    fig, axes = plt.subplots(1, num_methods, figsize=(4 * num_methods, 4))

    if num_methods == 1:
        axes = [axes]

    for ax, (method_name, results) in zip(axes, results_dict.items()):
        y_true = np.array(results["labels"])
        y_scores = np.array(results["scores"])
        y_pred = (y_scores >= threshold).astype(int)

        cm = confusion_matrix(y_true, y_pred)
        im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)

        ax.set_title(f"{method_name}", fontsize=12)
        ax.set_xlabel('Predicted', fontsize=10)
        ax.set_ylabel('Actual', fontsize=10)

        # Add text annotations
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                        color='white' if cm[i, j] > cm.max()/2 else 'black', fontsize=12)

        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Non-Hall.', 'Hall.'])
        ax.set_yticklabels(['Non-Hall.', 'Hall.'])

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_training_curves(
    train_losses: List[float],
    val_losses: List[float],
    train_metrics: Dict[str, List[float]] = None,
    val_metrics: Dict[str, List[float]] = None,
    save_path: str = "training_curves.png"
):
    """Plot training and validation curves."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Loss curves
    epochs = range(1, len(train_losses) + 1)
    axes[0].plot(epochs, train_losses, 'b-', lw=2, label='Train Loss', marker='o', markersize=4)
    axes[0].plot(epochs, val_losses, 'r-', lw=2, label='Val Loss', marker='s', markersize=4)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].set_title('Training and Validation Loss', fontsize=14)
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)

    # Metrics curves
    if train_metrics and val_metrics:
        for metric_name in train_metrics.keys():
            if metric_name in val_metrics:
                axes[1].plot(epochs, train_metrics[metric_name], '--', lw=2,
                             label=f'Train {metric_name}', marker='o', markersize=4)
                axes[1].plot(epochs, val_metrics[metric_name], '-', lw=2,
                             label=f'Val {metric_name}', marker='s', markersize=4)

        axes[1].set_xlabel('Epoch', fontsize=12)
        axes[1].set_ylabel('Metric Value', fontsize=12)
        axes[1].set_title('Training Metrics', fontsize=14)
        axes[1].legend(fontsize=10)
        axes[1].grid(True, alpha=0.3)
    else:
        axes[1].text(0.5, 0.5, 'No additional metrics', ha='center', va='center',
                     transform=axes[1].transAxes, fontsize=14)
        axes[1].axis('off')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_method_comparison(
    metrics_dict: Dict[str, Dict[str, float]],
    save_path: str = "method_comparison.png"
):
    """Plot bar chart comparing metrics across methods."""
    methods = list(metrics_dict.keys())
    metric_names = ["auroc", "auprc", "ece", "brier_score"]
    x = np.arange(len(metric_names))
    width = 0.8 / len(methods)

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = plt.cm.Set2(np.linspace(0, 1, len(methods)))

    for i, (method, color) in enumerate(zip(methods, colors)):
        values = [metrics_dict[method].get(m, 0) for m in metric_names]
        # Invert ECE and Brier score so higher is better for visualization
        display_values = values.copy()
        display_values[2] = 1 - display_values[2]  # ECE
        display_values[3] = 1 - display_values[3]  # Brier

        ax.bar(x + i * width, display_values, width, label=method, color=color)

    ax.set_xlabel('Metric', fontsize=12)
    ax.set_ylabel('Score (higher is better)', fontsize=12)
    ax.set_title('Method Comparison', fontsize=14)
    ax.set_xticks(x + width * (len(methods) - 1) / 2)
    ax.set_xticklabels(['AUROC', 'AUPRC', '1 - ECE', '1 - Brier'], fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim([0, 1.1])

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def save_results(results: Dict, path: str):
    """Save results to JSON file."""
    # Convert numpy arrays to lists
    def convert_to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        return obj

    serializable_results = convert_to_serializable(results)

    with open(path, 'w') as f:
        json.dump(serializable_results, f, indent=2)
