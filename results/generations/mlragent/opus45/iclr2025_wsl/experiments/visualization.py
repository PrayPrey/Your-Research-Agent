"""
Visualization utilities for SymVAE experiments.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import os


def plot_training_curves(train_history: Dict[str, List[float]],
                         val_history: Dict[str, List[float]],
                         title: str, save_path: str):
    """Plot training and validation loss curves."""
    fig, axes = plt.subplots(1, len(train_history), figsize=(5 * len(train_history), 4))
    if len(train_history) == 1:
        axes = [axes]

    colors = plt.cm.tab10(np.linspace(0, 1, 10))

    for i, (metric_name, train_values) in enumerate(train_history.items()):
        ax = axes[i]
        epochs = range(1, len(train_values) + 1)

        ax.plot(epochs, train_values, 'o-', color=colors[0], label=f'Train {metric_name}',
                markersize=3, linewidth=1.5)

        if metric_name in val_history:
            ax.plot(epochs, val_history[metric_name], 's-', color=colors[1],
                    label=f'Val {metric_name}', markersize=3, linewidth=1.5)

        ax.set_xlabel('Epoch', fontsize=12)
        ax.set_ylabel(metric_name.replace('_', ' ').title(), fontsize=12)
        ax.set_title(f'{title} - {metric_name.replace("_", " ").title()}', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', which='major', labelsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_model_comparison(results: Dict[str, Dict[str, float]],
                          metrics: List[str], title: str, save_path: str):
    """Create bar chart comparing different models across metrics."""
    models = list(results.keys())
    n_metrics = len(metrics)
    n_models = len(models)

    fig, ax = plt.subplots(figsize=(max(10, n_metrics * 2), 6))

    x = np.arange(n_metrics)
    width = 0.8 / n_models
    colors = plt.cm.Set2(np.linspace(0, 1, n_models))

    for i, model in enumerate(models):
        values = [results[model].get(m, 0) for m in metrics]
        stds = [results[model].get(f'{m}_std', 0) for m in metrics]

        bars = ax.bar(x + i * width - (n_models - 1) * width / 2, values, width,
                      label=model, color=colors[i], yerr=stds, capsize=3)

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{val:.3f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

    ax.set_xlabel('Metric', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace('_', '\n') for m in metrics], fontsize=10)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_latent_space_variance(variance_results: Dict[str, Dict[str, float]],
                               save_path: str):
    """Plot latent space variance across permutations for different models."""
    models = list(variance_results.keys())
    means = [variance_results[m].get('latent_variance_mean', 0) for m in models]
    stds = [variance_results[m].get('latent_variance_std', 0) for m in models]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.Set3(np.linspace(0, 1, len(models)))

    bars = ax.bar(models, means, yerr=stds, capsize=5, color=colors, edgecolor='black')

    for bar, mean in zip(bars, means):
        height = bar.get_height()
        ax.annotate(f'{mean:.4f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Latent Variance under Permutations', fontsize=12)
    ax.set_title('Symmetry Invariance: Lower is Better', fontsize=14)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_generation_quality(quality_results: Dict[str, Dict[str, float]],
                            save_path: str, task_type: str = 'classification'):
    """Plot generation quality metrics for different models."""
    models = list(quality_results.keys())

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    colors = plt.cm.Paired(np.linspace(0, 1, len(models)))

    # Plot test loss
    ax = axes[0]
    losses = [quality_results[m].get('test_loss', 0) for m in models]
    loss_stds = [quality_results[m].get('test_loss_std', 0) for m in models]

    bars = ax.bar(models, losses, yerr=loss_stds, capsize=5, color=colors, edgecolor='black')
    for bar, loss in zip(bars, losses):
        ax.annotate(f'{loss:.4f}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Test Loss', fontsize=12)
    ax.set_title('Generation Quality: Test Loss (Lower is Better)', fontsize=12)
    ax.grid(True, axis='y', alpha=0.3)
    ax.tick_params(axis='x', rotation=15)

    # Plot accuracy (for classification) or R^2 (for regression)
    ax = axes[1]
    if task_type == 'classification':
        accs = [quality_results[m].get('test_accuracy', 0) for m in models]
        acc_stds = [quality_results[m].get('test_accuracy_std', 0) for m in models]

        bars = ax.bar(models, accs, yerr=acc_stds, capsize=5, color=colors, edgecolor='black')
        for bar, acc in zip(bars, accs):
            ax.annotate(f'{acc:.3f}',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

        ax.set_ylabel('Test Accuracy', fontsize=12)
        ax.set_title('Generation Quality: Test Accuracy (Higher is Better)', fontsize=12)
        ax.set_ylim(0, 1.1)
    else:
        # For regression, use inverse of test loss as a proxy
        inv_losses = [1.0 / (quality_results[m].get('test_loss', 1) + 0.01) for m in models]
        bars = ax.bar(models, inv_losses, color=colors, edgecolor='black')
        ax.set_ylabel('1 / Test Loss', fontsize=12)
        ax.set_title('Generation Quality: Inverse Test Loss (Higher is Better)', fontsize=12)

    ax.set_xlabel('Model', fontsize=12)
    ax.grid(True, axis='y', alpha=0.3)
    ax.tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_interpolation_smoothness(smoothness_results: Dict[str, Dict[str, float]],
                                  save_path: str):
    """Plot interpolation smoothness for different models."""
    models = list(smoothness_results.keys())
    means = [smoothness_results[m].get('interpolation_smoothness_mean', 0) for m in models]
    stds = [smoothness_results[m].get('interpolation_smoothness_std', 0) for m in models]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.coolwarm(np.linspace(0.2, 0.8, len(models)))

    bars = ax.bar(models, means, yerr=stds, capsize=5, color=colors, edgecolor='black')

    for bar, mean in zip(bars, means):
        height = bar.get_height()
        ax.annotate(f'{mean:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Interpolation Smoothness', fontsize=12)
    ax.set_title('Latent Space Interpolation Smoothness (Higher is Better)', fontsize=14)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_ablation_study(ablation_results: Dict[str, Dict[str, float]],
                        metrics: List[str], save_path: str):
    """Plot ablation study results."""
    variants = list(ablation_results.keys())
    n_metrics = len(metrics)

    fig, axes = plt.subplots(1, n_metrics, figsize=(5 * n_metrics, 5))
    if n_metrics == 1:
        axes = [axes]

    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(variants)))

    for i, metric in enumerate(metrics):
        ax = axes[i]
        values = [ablation_results[v].get(metric, 0) for v in variants]
        stds = [ablation_results[v].get(f'{metric}_std', 0) for v in variants]

        bars = ax.bar(range(len(variants)), values, yerr=stds, capsize=4, color=colors, edgecolor='black')

        for bar, val in zip(bars, values):
            ax.annotate(f'{val:.4f}',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

        ax.set_xticks(range(len(variants)))
        ax.set_xticklabels([v.replace('_', '\n') for v in variants], fontsize=9, rotation=15)
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=11)
        ax.set_title(f'Ablation: {metric.replace("_", " ").title()}', fontsize=12)
        ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def create_summary_table(results: Dict[str, Dict[str, float]],
                         metrics: List[str]) -> pd.DataFrame:
    """Create a summary table of results."""
    data = []
    for model, model_results in results.items():
        row = {'Model': model}
        for metric in metrics:
            value = model_results.get(metric, float('nan'))
            std = model_results.get(f'{metric}_std', None)
            if std is not None and not np.isnan(std):
                row[metric] = f'{value:.4f} ± {std:.4f}'
            else:
                row[metric] = f'{value:.4f}'
        data.append(row)

    return pd.DataFrame(data)


def plot_radar_chart(results: Dict[str, Dict[str, float]],
                     metrics: List[str], save_path: str):
    """Create radar chart comparing models across multiple metrics."""
    models = list(results.keys())
    n_metrics = len(metrics)

    # Normalize values to [0, 1] for comparison
    normalized_results = {}
    for metric in metrics:
        values = [results[m].get(metric, 0) for m in models]
        min_val, max_val = min(values), max(values)
        if max_val - min_val > 0:
            for i, m in enumerate(models):
                if m not in normalized_results:
                    normalized_results[m] = {}
                # For loss/variance metrics, lower is better, so invert
                if 'loss' in metric.lower() or 'variance' in metric.lower():
                    normalized_results[m][metric] = 1 - (values[i] - min_val) / (max_val - min_val)
                else:
                    normalized_results[m][metric] = (values[i] - min_val) / (max_val - min_val)
        else:
            for m in models:
                if m not in normalized_results:
                    normalized_results[m] = {}
                normalized_results[m][metric] = 0.5

    # Create radar chart
    angles = np.linspace(0, 2 * np.pi, n_metrics, endpoint=False).tolist()
    angles += angles[:1]  # Complete the loop

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    colors = plt.cm.Set2(np.linspace(0, 1, len(models)))

    for i, model in enumerate(models):
        values = [normalized_results[model].get(m, 0) for m in metrics]
        values += values[:1]

        ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[i], markersize=6)
        ax.fill(angles, values, alpha=0.1, color=colors[i])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m.replace('_', '\n') for m in metrics], fontsize=10)
    ax.set_ylim(0, 1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1), fontsize=10)
    ax.set_title('Model Comparison (Normalized Metrics)', fontsize=14, pad=20)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
