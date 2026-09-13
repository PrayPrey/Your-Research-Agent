import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict
from pathlib import Path


def plot_gate_metrics(metrics: Dict[str, float], save_path: str, target_precision: float = 0.70, target_recall: float = 0.85) -> None:
    """Bar chart with target lines. metrics: {precision, recall, f1, accuracy}"""
    fig, ax = plt.subplots(figsize=(10, 6))

    metric_names = ['Precision\n(MAJOR)', 'Recall\n(MAJOR)', 'F1\n(MAJOR)', 'Accuracy']
    values = [
        metrics.get('precision_major', 0),
        metrics.get('recall_major', 0),
        metrics.get('f1_major', 0),
        metrics.get('accuracy', 0)
    ]
    targets = [target_precision, target_recall, None, None]

    x = np.arange(len(metric_names))
    bars = ax.bar(x, values, color=['#2ecc71', '#3498db', '#9b59b6', '#e74c3c'], alpha=0.7)

    # Add target lines for precision and recall
    for i, target in enumerate(targets):
        if target is not None:
            ax.axhline(y=target, xmin=i/len(x), xmax=(i+1)/len(x),
                      color='red', linestyle='--', linewidth=2, label=f'Target: {target:.0%}' if i == 0 else '')

    ax.set_xlabel('Metrics', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('SVAD Drift Classifier - Gate Metrics', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metric_names)
    ax.set_ylim(0, 1.1)
    ax.grid(axis='y', alpha=0.3)
    ax.legend()

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2%}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_confusion_matrix(cm: np.ndarray, save_path: str) -> None:
    """Seaborn heatmap. cm: [3, 3]"""
    fig, ax = plt.subplots(figsize=(8, 6))

    labels = ['MAJOR', 'MINOR', 'PATCH']
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels,
                cbar_kws={'label': 'Count'}, ax=ax)

    ax.set_xlabel('Predicted Label', fontsize=12)
    ax.set_ylabel('True Label', fontsize=12)
    ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_drift_scores(results: List[Dict], save_path: str) -> None:
    """Histogram of KS/MMD scores by label."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Extract scores by true label
    major_ks = [r['scores']['ks_score'] for r in results if r['true_label'] == 'MAJOR']
    minor_ks = [r['scores']['ks_score'] for r in results if r['true_label'] == 'MINOR']
    patch_ks = [r['scores']['ks_score'] for r in results if r['true_label'] == 'PATCH']

    major_mmd = [r['scores']['mmd_score'] for r in results if r['true_label'] == 'MAJOR']
    minor_mmd = [r['scores']['mmd_score'] for r in results if r['true_label'] == 'MINOR']
    patch_mmd = [r['scores']['mmd_score'] for r in results if r['true_label'] == 'PATCH']

    # KS scores
    ax1.hist([major_ks, minor_ks, patch_ks], label=['MAJOR', 'MINOR', 'PATCH'],
             bins=10, alpha=0.7, color=['#e74c3c', '#f39c12', '#2ecc71'])
    ax1.axvline(x=0.07, color='red', linestyle='--', label='MAJOR threshold (0.07)')
    ax1.axvline(x=0.02, color='orange', linestyle='--', label='MINOR threshold (0.02)')
    ax1.set_xlabel('KS Score', fontsize=11)
    ax1.set_ylabel('Frequency', fontsize=11)
    ax1.set_title('KS Test Scores Distribution', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # MMD scores
    ax2.hist([major_mmd, minor_mmd, patch_mmd], label=['MAJOR', 'MINOR', 'PATCH'],
             bins=10, alpha=0.7, color=['#e74c3c', '#f39c12', '#2ecc71'])
    ax2.axvline(x=0.07, color='red', linestyle='--', label='MAJOR threshold (0.07)')
    ax2.axvline(x=0.02, color='orange', linestyle='--', label='MINOR threshold (0.02)')
    ax2.set_xlabel('MMD Score', fontsize=11)
    ax2.set_ylabel('Frequency', fontsize=11)
    ax2.set_title('MMD Scores Distribution', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_per_dataset_performance(results: List[Dict], dataset_names: List[str], save_path: str) -> None:
    """Bar chart of accuracy per dataset."""
    fig, ax = plt.subplots(figsize=(12, 6))

    correct = [1 if results[i]['correct'] else 0 for i in range(len(results))]
    colors = ['#2ecc71' if c else '#e74c3c' for c in correct]

    x = np.arange(len(dataset_names))
    bars = ax.bar(x, [1] * len(dataset_names), color=colors, alpha=0.7)

    ax.set_xlabel('Dataset', fontsize=12)
    ax.set_ylabel('Correct (1) / Incorrect (0)', fontsize=12)
    ax.set_title('Per-Dataset Classification Results', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(dataset_names, rotation=45, ha='right', fontsize=9)
    ax.set_ylim(0, 1.2)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Incorrect', 'Correct'])
    ax.grid(axis='y', alpha=0.3)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', alpha=0.7, label='Correct'),
        Patch(facecolor='#e74c3c', alpha=0.7, label='Incorrect')
    ]
    ax.legend(handles=legend_elements)

    # Add accuracy text
    accuracy = sum(correct) / len(correct) if correct else 0
    ax.text(0.5, 1.1, f'Overall Accuracy: {accuracy:.1%}',
            transform=ax.transAxes, ha='center', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
