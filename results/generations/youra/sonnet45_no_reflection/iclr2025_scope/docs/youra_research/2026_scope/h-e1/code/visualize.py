"""
Visualization and reporting for h-e1 experiment.
Generates plots for gate metrics, training curves, and expert utilization.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import torch
from typing import Dict, List
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


def plot_gate_metrics(
    baseline: float,
    proposed: float,
    target: float,
    save_path: str
) -> None:
    """
    Plot gate satisfaction metrics (baseline vs proposed vs target).

    Args:
        baseline: Baseline accuracy
        proposed: Proposed model accuracy
        target: Target accuracy for gate satisfaction
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    categories = ['Baseline', 'Proposed', 'Target']
    values = [baseline, proposed, target]
    colors = ['#e74c3c', '#3498db', '#2ecc71']

    bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2%}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Add gate satisfaction line
    ax.axhline(y=target, color='#2ecc71', linestyle='--', linewidth=2,
               label=f'Gate Target ({target:.2%})')

    # Styling
    ax.set_ylabel('Accuracy', fontsize=14, fontweight='bold')
    ax.set_title('Gate Metrics: Super-Additive Gain', fontsize=16, fontweight='bold')
    ax.set_ylim(0, max(values) * 1.2)
    ax.legend(fontsize=12)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_training_curves(
    metrics_history: Dict[str, List[float]],
    save_path: str
) -> None:
    """
    Plot training curves (loss, alignment loss, etc.).

    Args:
        metrics_history: Dictionary with metric names and their epoch values
        save_path: Path to save figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    metrics = ['loss', 'task_loss', 'alignment_loss', 'aux_loss']
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']

    for idx, (metric, color) in enumerate(zip(metrics, colors)):
        if metric in metrics_history:
            values = metrics_history[metric]
            epochs = list(range(1, len(values) + 1))

            axes[idx].plot(epochs, values, marker='o', linewidth=2,
                          color=color, markersize=6, label=metric)
            axes[idx].set_xlabel('Epoch', fontsize=12, fontweight='bold')
            axes[idx].set_ylabel('Value', fontsize=12, fontweight='bold')
            axes[idx].set_title(f'{metric.replace("_", " ").title()}',
                               fontsize=14, fontweight='bold')
            axes[idx].grid(alpha=0.3)
            axes[idx].legend(fontsize=10)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_expert_utilization(
    expert_probs: torch.Tensor,
    task_names: List[str],
    save_path: str
) -> None:
    """
    Plot expert utilization heatmap.

    Args:
        expert_probs: Tensor of shape [num_tasks, num_experts] with routing probabilities
        task_names: List of task names
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Convert to numpy
    if isinstance(expert_probs, torch.Tensor):
        expert_probs = expert_probs.cpu().numpy()

    # Create heatmap
    sns.heatmap(
        expert_probs,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Routing Probability'},
        xticklabels=[f'Expert {i}' for i in range(expert_probs.shape[1])],
        yticklabels=task_names if len(task_names) == expert_probs.shape[0] else range(expert_probs.shape[0]),
        ax=ax
    )

    ax.set_title('Expert Utilization Across Tasks', fontsize=16, fontweight='bold')
    ax.set_xlabel('Expert ID', fontsize=12, fontweight='bold')
    ax.set_ylabel('Task', fontsize=12, fontweight='bold')

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_per_task_comparison(
    task_results: Dict[str, Dict[str, float]],
    save_path: str
) -> None:
    """
    Plot per-task performance comparison.

    Args:
        task_results: Dictionary with per-task accuracy results
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    tasks = list(task_results.keys())
    accuracies = [task_results[task]['accuracy'] for task in tasks]

    # Create bar plot
    bars = ax.bar(range(len(tasks)), accuracies, color='#3498db', alpha=0.7, edgecolor='black')

    # Add value labels
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{acc:.2%}',
                ha='center', va='bottom', fontsize=9)

    ax.set_xticks(range(len(tasks)))
    ax.set_xticklabels(tasks, rotation=45, ha='right', fontsize=10)
    ax.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax.set_title('Per-Task Performance', fontsize=16, fontweight='bold')
    ax.set_ylim(0, max(accuracies) * 1.2 if accuracies else 1.0)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_all_figures(
    results: Dict,
    metrics_history: Dict,
    save_dir: str
) -> None:
    """
    Generate all figures for the experiment.

    Args:
        results: Dictionary with experiment results
        metrics_history: Dictionary with training metrics history
        save_dir: Directory to save figures
    """
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    # Plot gate metrics
    if 'baseline_acc' in results and 'proposed_acc' in results:
        plot_gate_metrics(
            baseline=results['baseline_acc'],
            proposed=results['proposed_acc'],
            target=results.get('target_acc', results['baseline_acc'] + 0.02),
            save_path=str(save_dir / 'gate_metrics.png')
        )

    # Plot training curves
    if metrics_history:
        plot_training_curves(
            metrics_history=metrics_history,
            save_path=str(save_dir / 'training_curves.png')
        )

    # Plot expert utilization
    if 'expert_probs' in results:
        task_names = results.get('task_names', [f'Task {i}' for i in range(17)])
        plot_expert_utilization(
            expert_probs=results['expert_probs'],
            task_names=task_names,
            save_path=str(save_dir / 'expert_utilization.png')
        )

    # Plot per-task comparison
    if 'task_results' in results:
        plot_per_task_comparison(
            task_results=results['task_results'],
            save_path=str(save_dir / 'per_task_performance.png')
        )

    print(f"All figures saved to {save_dir}")
