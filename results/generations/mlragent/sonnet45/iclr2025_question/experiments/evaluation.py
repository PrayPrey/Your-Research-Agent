"""
Evaluation metrics and utilities.
"""

import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, roc_curve, precision_recall_curve
)
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import seaborn as sns


class EvaluationMetrics:
    """Compute evaluation metrics for hallucination detection."""

    def __init__(self):
        self.y_true = []
        self.y_pred = []
        self.y_scores = []

    def add_prediction(self, true_label: bool, predicted_label: bool, score: float):
        """Add a prediction."""
        self.y_true.append(int(true_label))
        self.y_pred.append(int(predicted_label))
        self.y_scores.append(score)

    def compute_metrics(self) -> Dict:
        """Compute all evaluation metrics."""
        y_true = np.array(self.y_true)
        y_pred = np.array(self.y_pred)
        y_scores = np.array(self.y_scores)

        metrics = {
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0),
            "accuracy": np.mean(y_true == y_pred)
        }

        # Add AUC if we have both classes
        if len(np.unique(y_true)) > 1:
            metrics["auc"] = roc_auc_score(y_true, y_scores)
        else:
            metrics["auc"] = 0.0

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            metrics["true_negatives"] = int(tn)
            metrics["false_positives"] = int(fp)
            metrics["false_negatives"] = int(fn)
            metrics["true_positives"] = int(tp)
        else:
            metrics["true_negatives"] = 0
            metrics["false_positives"] = 0
            metrics["false_negatives"] = 0
            metrics["true_positives"] = 0

        return metrics

    def plot_roc_curve(self, save_path: str):
        """Plot ROC curve."""
        y_true = np.array(self.y_true)
        y_scores = np.array(self.y_scores)

        if len(np.unique(y_true)) < 2:
            print("Cannot plot ROC curve: only one class present")
            return

        fpr, tpr, thresholds = roc_curve(y_true, y_scores)
        auc = roc_auc_score(y_true, y_scores)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.3f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random', linewidth=1)
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('ROC Curve for Hallucination Detection', fontsize=14)
        plt.legend(fontsize=11)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_precision_recall_curve(self, save_path: str):
        """Plot Precision-Recall curve."""
        y_true = np.array(self.y_true)
        y_scores = np.array(self.y_scores)

        if len(np.unique(y_true)) < 2:
            print("Cannot plot PR curve: only one class present")
            return

        precision, recall, thresholds = precision_recall_curve(y_true, y_scores)

        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, linewidth=2, label='PR Curve')
        plt.xlabel('Recall', fontsize=12)
        plt.ylabel('Precision', fontsize=12)
        plt.title('Precision-Recall Curve', fontsize=14)
        plt.legend(fontsize=11)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

    def plot_confusion_matrix(self, save_path: str):
        """Plot confusion matrix."""
        y_true = np.array(self.y_true)
        y_pred = np.array(self.y_pred)

        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['No Hallucination', 'Hallucination'],
                   yticklabels=['No Hallucination', 'Hallucination'],
                   cbar_kws={'label': 'Count'})
        plt.xlabel('Predicted Label', fontsize=12)
        plt.ylabel('True Label', fontsize=12)
        plt.title('Confusion Matrix', fontsize=14)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()


def plot_model_comparison(results: Dict[str, Dict], save_path: str):
    """Plot comparison of different models."""
    models = list(results.keys())
    metrics = ['precision', 'recall', 'f1', 'accuracy', 'auc']

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Bar plot
    x = np.arange(len(metrics))
    width = 0.15
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for i, model in enumerate(models):
        values = [results[model].get(m, 0) for m in metrics]
        axes[0].bar(x + i * width, values, width, label=model, color=colors[i % len(colors)])

    axes[0].set_xlabel('Metrics', fontsize=12)
    axes[0].set_ylabel('Score', fontsize=12)
    axes[0].set_title('Model Comparison - All Metrics', fontsize=14)
    axes[0].set_xticks(x + width * (len(models) - 1) / 2)
    axes[0].set_xticklabels(metrics)
    axes[0].legend(fontsize=10)
    axes[0].grid(axis='y', alpha=0.3)
    axes[0].set_ylim([0, 1.05])

    # Radar plot
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    ax = plt.subplot(122, projection='polar')
    for i, model in enumerate(models):
        values = [results[model].get(m, 0) for m in metrics]
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[i % len(colors)])
        ax.fill(angles, values, alpha=0.15, color=colors[i % len(colors)])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1)
    ax.set_title('Model Comparison - Radar Chart', fontsize=14, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    ax.grid(True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_error_analysis(results: Dict[str, Dict], save_path: str):
    """Plot error type analysis."""
    models = list(results.keys())
    error_types = ['False Positives', 'False Negatives', 'True Positives', 'True Negatives']

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Stacked bar chart
    fps = [results[m].get('false_positives', 0) for m in models]
    fns = [results[m].get('false_negatives', 0) for m in models]
    tps = [results[m].get('true_positives', 0) for m in models]
    tns = [results[m].get('true_negatives', 0) for m in models]

    x = np.arange(len(models))
    width = 0.5

    axes[0].bar(x, tps, width, label='True Positives', color='#2ca02c')
    axes[0].bar(x, tns, width, bottom=tps, label='True Negatives', color='#1f77b4')
    axes[0].bar(x, fps, width, bottom=np.array(tps) + np.array(tns),
               label='False Positives', color='#ff7f0e')
    axes[0].bar(x, fns, width,
               bottom=np.array(tps) + np.array(tns) + np.array(fps),
               label='False Negatives', color='#d62728')

    axes[0].set_ylabel('Count', fontsize=12)
    axes[0].set_title('Error Type Distribution', fontsize=14)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(models, rotation=15, ha='right')
    axes[0].legend(fontsize=10)
    axes[0].grid(axis='y', alpha=0.3)

    # Error rate comparison
    total_predictions = [fps[i] + fns[i] + tps[i] + tns[i] for i in range(len(models))]
    fp_rates = [fps[i] / max(total_predictions[i], 1) for i in range(len(models))]
    fn_rates = [fns[i] / max(total_predictions[i], 1) for i in range(len(models))]

    x = np.arange(len(models))
    width = 0.35

    axes[1].bar(x - width/2, fp_rates, width, label='False Positive Rate', color='#ff7f0e')
    axes[1].bar(x + width/2, fn_rates, width, label='False Negative Rate', color='#d62728')

    axes[1].set_ylabel('Error Rate', fontsize=12)
    axes[1].set_title('Error Rates Comparison', fontsize=14)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(models, rotation=15, ha='right')
    axes[1].legend(fontsize=10)
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_hallucination_rate_by_domain(dataset: List[Dict],
                                      predictions: Dict[str, List[Dict]],
                                      save_path: str):
    """Plot hallucination detection rate by domain."""
    domains = list(set(d['domain'] for d in dataset))
    models = list(predictions.keys())

    # Calculate detection rates by domain
    detection_rates = {model: {domain: [] for domain in domains} for model in models}

    for i, data in enumerate(dataset):
        domain = data['domain']
        true_label = data['annotation']['has_contradiction']

        for model in models:
            pred = predictions[model][i]
            detected = pred['has_hallucination']
            if true_label:  # Only count for actual hallucinations
                detection_rates[model][domain].append(int(detected))

    # Compute average detection rates
    avg_rates = {model: {} for model in models}
    for model in models:
        for domain in domains:
            rates = detection_rates[model][domain]
            avg_rates[model][domain] = np.mean(rates) if rates else 0.0

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(domains))
    width = 0.15
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for i, model in enumerate(models):
        values = [avg_rates[model][domain] for domain in domains]
        ax.bar(x + i * width, values, width, label=model, color=colors[i % len(colors)])

    ax.set_xlabel('Domain', fontsize=12)
    ax.set_ylabel('Detection Rate', fontsize=12)
    ax.set_title('Hallucination Detection Rate by Domain', fontsize=14)
    ax.set_xticks(x + width * (len(models) - 1) / 2)
    ax.set_xticklabels(domains)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim([0, 1.05])

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
