"""Visualization functions for SAT profiling results."""

from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path


# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300


def plot_sat_vs_degradation(
    SAT_values: List[float],
    degradations: List[float],
    architectures: List[str],
    output_path: str
) -> None:
    """
    Scatter plot: SAT vs Epoch Degradation with decision boundary.

    Args:
        SAT_values: List of SAT measurements
        degradations: List of degradation percentages (as fractions)
        architectures: List of architecture names
        output_path: Output file path
    """
    plt.figure(figsize=(10, 6))

    # Convert degradations to percentages for plotting
    degradations_pct = [d * 100 for d in degradations]

    # Color by architecture type (CNN vs Transformer)
    colors = ['blue' if 'resnet' in arch or 'mobile' in arch or 'efficient' in arch
              else 'red' for arch in architectures]

    plt.scatter(SAT_values, degradations_pct, c=colors, alpha=0.6, s=100)

    # Decision boundaries
    plt.axhline(y=15, color='green', linestyle='--', label='15% Degradation Threshold')
    plt.axvline(x=1.5, color='orange', linestyle='--', label='SAT Threshold (1.5)')

    plt.xlabel('GPU-normalized SAT')
    plt.ylabel('Epoch-time Degradation (%)')
    plt.title('SAT vs Epoch-time Degradation')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_precision_recall_curve(
    thresholds: List[float],
    precisions: List[float],
    recalls: List[float],
    output_path: str
) -> None:
    """
    Precision-Recall curve varying SAT threshold.

    Args:
        thresholds: List of SAT thresholds
        precisions: Corresponding precision values
        recalls: Corresponding recall values
        output_path: Output file path
    """
    plt.figure(figsize=(10, 6))

    plt.plot(recalls, precisions, 'b-', linewidth=2, label='Precision-Recall Curve')

    # Mark target point (Precision ≥0.80, Recall ≥0.70)
    plt.axhline(y=0.80, color='green', linestyle='--', alpha=0.5, label='Target Precision (0.80)')
    plt.axvline(x=0.70, color='orange', linestyle='--', alpha=0.5, label='Target Recall (0.70)')

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve (Varying SAT Threshold)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 1)
    plt.ylim(0, 1)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_jitter_validation(
    jitter_results: Dict[str, Dict[int, float]],
    output_path: str
) -> None:
    """
    SAT vs injected delay, stratified by GPU utilization.

    Args:
        jitter_results: Dictionary with experiment results
        output_path: Output file path
    """
    plt.figure(figsize=(10, 6))

    for exp_name, sat_by_delay in jitter_results.items():
        delays = sorted(sat_by_delay.keys())
        sat_values = [sat_by_delay[d] for d in delays]

        plt.plot(delays, sat_values, marker='o', linewidth=2, label=exp_name)

    plt.xlabel('Injected Delay (ms)')
    plt.ylabel('SAT')
    plt.title('Synthetic Jitter Validation: SAT vs Injected Delay')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_architecture_sat_distribution(
    results: Dict[str, Dict],
    output_path: str
) -> None:
    """
    Violin plot: SAT distribution per architecture.

    Args:
        results: Dictionary mapping config_id -> {SAT, architecture, ...}
        output_path: Output file path
    """
    # Group SAT values by architecture
    arch_to_sat = {}
    for config_id, result in results.items():
        arch = result.get('architecture', 'unknown')
        sat = result.get('SAT', 0.0)

        if arch not in arch_to_sat:
            arch_to_sat[arch] = []
        arch_to_sat[arch].append(sat)

    # Prepare data for violin plot
    architectures = list(arch_to_sat.keys())
    sat_data = [arch_to_sat[arch] for arch in architectures]

    plt.figure(figsize=(14, 6))
    positions = range(len(architectures))

    parts = plt.violinplot(sat_data, positions=positions, showmeans=True, showmedians=True)

    plt.xticks(positions, architectures, rotation=45, ha='right')
    plt.ylabel('SAT')
    plt.title('SAT Distribution by Architecture')
    plt.axhline(y=1.5, color='red', linestyle='--', alpha=0.5, label='SAT Threshold (1.5)')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_confusion_matrix(
    cm: np.ndarray,
    output_path: str
) -> None:
    """
    Confusion matrix visualization.

    Args:
        cm: 2x2 confusion matrix [[TN, FP], [FN, TP]]
        output_path: Output file path
    """
    plt.figure(figsize=(8, 6))

    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=['No Degradation', 'Degradation'],
        yticklabels=['No Degradation', 'Degradation'],
        cbar=True
    )

    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.title('Confusion Matrix: SAT Degradation Prediction')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_gate_metrics_comparison(
    metrics: Dict[str, float],
    targets: Dict[str, float],
    output_path: str
) -> None:
    """
    Bar chart: Achieved vs Target metrics.

    Args:
        metrics: Dictionary with achieved metrics (precision, recall, f1)
        targets: Dictionary with target metrics
        output_path: Output file path
    """
    plt.figure(figsize=(10, 6))

    metric_names = ['Precision', 'Recall', 'F1-Score']
    achieved_values = [metrics.get('precision', 0), metrics.get('recall', 0), metrics.get('f1', 0)]
    target_values = [targets.get('precision', 0.80), targets.get('recall', 0.70), targets.get('f1', 0.75)]

    x = np.arange(len(metric_names))
    width = 0.35

    plt.bar(x - width/2, achieved_values, width, label='Achieved', color='steelblue')
    plt.bar(x + width/2, target_values, width, label='Target', color='lightcoral')

    plt.xlabel('Metrics')
    plt.ylabel('Score')
    plt.title('Gate Metrics: Achieved vs Target')
    plt.xticks(x, metric_names)
    plt.ylim(0, 1.0)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for i, (achieved, target) in enumerate(zip(achieved_values, target_values)):
        plt.text(i - width/2, achieved + 0.02, f'{achieved:.2f}', ha='center', va='bottom')
        plt.text(i + width/2, target + 0.02, f'{target:.2f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
