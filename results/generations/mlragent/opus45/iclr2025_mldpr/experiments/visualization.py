"""
Visualization utilities for DDHS experiments.
Generates figures for results analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import pandas as pd
from pathlib import Path
import os


def setup_style():
    """Setup matplotlib style"""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 150
    plt.rcParams['savefig.bbox'] = 'tight'


def plot_deprecation_prediction_comparison(
    results: Dict[str, Dict],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot comparison of deprecation prediction metrics across methods.
    """
    setup_style()

    methods = list(results.keys())
    metrics = ['auc_roc', 'avg_precision', 'f1_at_optimal']
    metric_labels = ['AUC-ROC', 'Average Precision', 'F1 (Optimal)']

    x = np.arange(len(methods))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
        values = [results[m]['deprecation'][metric] for m in methods]
        bars = ax.bar(x + i * width, values, width, label=label, alpha=0.8)

        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{val:.2f}', ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('Method')
    ax.set_ylabel('Score')
    ax.set_title('Deprecation Prediction Performance Comparison')
    ax.set_xticks(x + width)
    ax.set_xticklabels(methods, rotation=30, ha='right')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1.1)
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Random')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Saved: {save_path}")

    return fig


def plot_user_alignment_comparison(
    results: Dict[str, Dict],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot comparison of user alignment metrics across methods.
    """
    setup_style()

    methods = list(results.keys())
    metrics = ['kendall_tau', 'spearman_rho', 'pearson_r']
    metric_labels = ["Kendall's τ", "Spearman's ρ", "Pearson's r"]

    x = np.arange(len(methods))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
        values = [results[m]['alignment'][metric] for m in methods]
        bars = ax.bar(x + i * width, values, width, label=label, alpha=0.8)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{val:.2f}', ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('Method')
    ax.set_ylabel('Correlation')
    ax.set_title('User Alignment (Expert Score Correlation)')
    ax.set_xticks(x + width)
    ax.set_xticklabels(methods, rotation=30, ha='right')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1.1)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Saved: {save_path}")

    return fig


def plot_efficiency_comparison(
    results: Dict[str, Dict],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot computational efficiency comparison.
    """
    setup_style()

    methods = list(results.keys())
    times = [results[m]['efficiency']['time_per_dataset'] * 1000 for m in methods]  # ms

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(methods)))
    bars = ax.barh(methods, times, color=colors, alpha=0.8)

    for bar, time in zip(bars, times):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
               f'{time:.2f} ms', va='center', fontsize=10)

    ax.set_xlabel('Time per Dataset (ms)')
    ax.set_title('Computational Efficiency Comparison')
    ax.set_xlim(0, max(times) * 1.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Saved: {save_path}")

    return fig


def plot_score_distribution(
    scores_dict: Dict[str, List[float]],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot distribution of health scores for different methods.
    """
    setup_style()

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()

    for idx, (method, scores) in enumerate(scores_dict.items()):
        if idx >= len(axes):
            break

        ax = axes[idx]
        ax.hist(scores, bins=20, alpha=0.7, edgecolor='black', linewidth=0.5)
        ax.axvline(np.mean(scores), color='red', linestyle='--',
                  label=f'Mean: {np.mean(scores):.2f}')
        ax.axvline(np.median(scores), color='green', linestyle=':',
                  label=f'Median: {np.median(scores):.2f}')
        ax.set_xlabel('Health Score')
        ax.set_ylabel('Frequency')
        ax.set_title(method)
        ax.legend(fontsize=8)
        ax.set_xlim(0, 1)

    # Hide unused axes
    for idx in range(len(scores_dict), len(axes)):
        axes[idx].set_visible(False)

    plt.suptitle('Health Score Distributions by Method', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Saved: {save_path}")

    return fig


def plot_score_vs_expert(
    scores_dict: Dict[str, List[float]],
    expert_scores: List[float],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot computed scores vs expert scores for each method.
    """
    setup_style()

    n_methods = len(scores_dict)
    n_cols = 3
    n_rows = (n_methods + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 4 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    for idx, (method, scores) in enumerate(scores_dict.items()):
        row = idx // n_cols
        col = idx % n_cols
        ax = axes[row, col]

        ax.scatter(expert_scores, scores, alpha=0.5, s=30)

        # Add regression line
        z = np.polyfit(expert_scores, scores, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(expert_scores), max(expert_scores), 100)
        ax.plot(x_line, p(x_line), 'r--', alpha=0.7, label='Linear fit')

        # Perfect correlation line
        ax.plot([0, 1], [0, 1], 'k:', alpha=0.3, label='Perfect correlation')

        ax.set_xlabel('Expert Score')
        ax.set_ylabel('Computed Score')
        ax.set_title(method)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.legend(fontsize=8, loc='upper left')

    # Hide unused axes
    for idx in range(n_methods, n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        axes[row, col].set_visible(False)

    plt.suptitle('Computed Scores vs Expert Quality Scores', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Saved: {save_path}")

    return fig


def plot_dimension_breakdown(
    dimension_scores: Dict[str, float],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot radar/spider chart of DDHS dimension scores.
    """
    setup_style()

    categories = list(dimension_scores.keys())
    values = list(dimension_scores.values())

    # Number of variables
    N = len(categories)

    # Compute angle for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    values = values + values[:1]
    angles = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

    ax.plot(angles, values, 'o-', linewidth=2, color='blue', alpha=0.7)
    ax.fill(angles, values, alpha=0.25, color='blue')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 1)

    plt.title('DDHS Dimension Breakdown', y=1.08)

    if save_path:
        plt.savefig(save_path)
        print(f"Saved: {save_path}")

    return fig


def plot_scalability(
    scalability_results: List[Dict],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot scalability benchmark results.
    """
    setup_style()

    df = pd.DataFrame(scalability_results)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Total time vs dataset size
    for method in df['method'].unique():
        method_df = df[df['method'] == method]
        ax1.errorbar(
            method_df['n_datasets'],
            method_df['mean_time'],
            yerr=method_df['std_time'],
            marker='o',
            label=method,
            capsize=3
        )

    ax1.set_xlabel('Number of Datasets')
    ax1.set_ylabel('Total Time (seconds)')
    ax1.set_title('Scalability: Total Computation Time')
    ax1.legend()
    ax1.set_xscale('log')
    ax1.grid(True, alpha=0.3)

    # Time per dataset
    for method in df['method'].unique():
        method_df = df[df['method'] == method]
        ax2.plot(
            method_df['n_datasets'],
            method_df['time_per_dataset'] * 1000,  # Convert to ms
            marker='o',
            label=method
        )

    ax2.set_xlabel('Number of Datasets')
    ax2.set_ylabel('Time per Dataset (ms)')
    ax2.set_title('Scalability: Per-Dataset Overhead')
    ax2.legend()
    ax2.set_xscale('log')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Saved: {save_path}")

    return fig


def plot_deprecation_by_score_bin(
    scores: List[float],
    is_deprecated: List[bool],
    method_name: str,
    n_bins: int = 10,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot deprecation rate by score bin.
    """
    setup_style()

    scores = np.array(scores)
    deprecated = np.array(is_deprecated)

    bins = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    bin_indices = np.digitize(scores, bins) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)

    deprecation_rates = []
    counts = []

    for i in range(n_bins):
        mask = bin_indices == i
        if np.sum(mask) > 0:
            rate = np.mean(deprecated[mask])
            count = np.sum(mask)
        else:
            rate = 0
            count = 0
        deprecation_rates.append(rate)
        counts.append(count)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    color1 = 'steelblue'
    ax1.bar(bin_centers, deprecation_rates, width=0.08, alpha=0.7, color=color1)
    ax1.set_xlabel('Health Score Bin')
    ax1.set_ylabel('Deprecation Rate', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, 1)

    # Add count on secondary axis
    ax2 = ax1.twinx()
    color2 = 'coral'
    ax2.plot(bin_centers, counts, 'o-', color=color2, alpha=0.7)
    ax2.set_ylabel('Number of Datasets', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    plt.title(f'Deprecation Rate by Health Score ({method_name})')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Saved: {save_path}")

    return fig


def plot_comprehensive_summary(
    results: Dict[str, Dict],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create comprehensive summary figure with multiple subplots.
    """
    setup_style()

    fig = plt.figure(figsize=(16, 12))

    # Layout: 2x3 grid
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

    methods = list(results.keys())

    # 1. AUC-ROC comparison
    ax1 = fig.add_subplot(gs[0, 0])
    auc_values = [results[m]['deprecation']['auc_roc'] for m in methods]
    colors = ['green' if v > 0.7 else 'orange' if v > 0.5 else 'red' for v in auc_values]
    bars = ax1.bar(range(len(methods)), auc_values, color=colors, alpha=0.7)
    ax1.set_xticks(range(len(methods)))
    ax1.set_xticklabels(methods, rotation=45, ha='right', fontsize=9)
    ax1.set_ylabel('AUC-ROC')
    ax1.set_title('Deprecation Prediction (AUC-ROC)')
    ax1.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    ax1.set_ylim(0, 1)
    for bar, val in zip(bars, auc_values):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.02, f'{val:.2f}',
                ha='center', fontsize=9)

    # 2. Kendall's tau comparison
    ax2 = fig.add_subplot(gs[0, 1])
    tau_values = [results[m]['alignment']['kendall_tau'] for m in methods]
    colors = ['green' if v > 0.5 else 'orange' if v > 0.3 else 'red' for v in tau_values]
    bars = ax2.bar(range(len(methods)), tau_values, color=colors, alpha=0.7)
    ax2.set_xticks(range(len(methods)))
    ax2.set_xticklabels(methods, rotation=45, ha='right', fontsize=9)
    ax2.set_ylabel("Kendall's τ")
    ax2.set_title('Expert Alignment')
    ax2.set_ylim(0, 1)
    for bar, val in zip(bars, tau_values):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.02, f'{val:.2f}',
                ha='center', fontsize=9)

    # 3. Efficiency (time per dataset)
    ax3 = fig.add_subplot(gs[0, 2])
    times = [results[m]['efficiency']['time_per_dataset'] * 1000 for m in methods]
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(methods)))
    bars = ax3.barh(methods, times, color=colors, alpha=0.7)
    ax3.set_xlabel('Time per Dataset (ms)')
    ax3.set_title('Computational Efficiency')
    for bar, val in zip(bars, times):
        ax3.text(val + 0.1, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}', va='center', fontsize=9)

    # 4. Heatmap of all metrics
    ax4 = fig.add_subplot(gs[1, :2])
    metric_names = ['AUC-ROC', 'Avg Precision', 'F1', "Kendall's τ", "Spearman's ρ"]
    metric_keys = [
        ('deprecation', 'auc_roc'),
        ('deprecation', 'avg_precision'),
        ('deprecation', 'f1_at_optimal'),
        ('alignment', 'kendall_tau'),
        ('alignment', 'spearman_rho')
    ]

    heatmap_data = []
    for m in methods:
        row = [results[m][cat][key] for cat, key in metric_keys]
        heatmap_data.append(row)

    heatmap_df = pd.DataFrame(heatmap_data, index=methods, columns=metric_names)
    sns.heatmap(heatmap_df, annot=True, fmt='.2f', cmap='RdYlGn', ax=ax4,
                vmin=0, vmax=1, cbar_kws={'label': 'Score'})
    ax4.set_title('Performance Summary Heatmap')

    # 5. Ranking comparison
    ax5 = fig.add_subplot(gs[1, 2])
    overall_scores = []
    for m in methods:
        score = (
            0.4 * results[m]['deprecation']['auc_roc'] +
            0.4 * results[m]['alignment']['kendall_tau'] +
            0.2 * (1 - min(1, results[m]['efficiency']['time_per_dataset'] * 10))
        )
        overall_scores.append(score)

    sorted_indices = np.argsort(overall_scores)[::-1]
    sorted_methods = [methods[i] for i in sorted_indices]
    sorted_scores = [overall_scores[i] for i in sorted_indices]

    colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(methods)))
    bars = ax5.barh(range(len(sorted_methods)), sorted_scores, color=colors[::-1], alpha=0.8)
    ax5.set_yticks(range(len(sorted_methods)))
    ax5.set_yticklabels(sorted_methods)
    ax5.set_xlabel('Overall Score')
    ax5.set_title('Overall Ranking')
    ax5.set_xlim(0, 1)
    for i, (bar, val) in enumerate(zip(bars, sorted_scores)):
        ax5.text(val + 0.02, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}', va='center', fontsize=10)

    plt.suptitle('DDHS Experimental Results Summary', fontsize=14, y=1.02)

    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig


if __name__ == "__main__":
    # Test visualizations with dummy data
    setup_style()

    dummy_results = {
        'DDHS': {
            'deprecation': {'auc_roc': 0.85, 'avg_precision': 0.72, 'f1_at_optimal': 0.68},
            'alignment': {'kendall_tau': 0.65, 'spearman_rho': 0.72, 'pearson_r': 0.75},
            'efficiency': {'time_per_dataset': 0.001, 'n_datasets': 100}
        },
        'Downloads-Only': {
            'deprecation': {'auc_roc': 0.58, 'avg_precision': 0.45, 'f1_at_optimal': 0.42},
            'alignment': {'kendall_tau': 0.35, 'spearman_rho': 0.40, 'pearson_r': 0.38},
            'efficiency': {'time_per_dataset': 0.0005, 'n_datasets': 100}
        }
    }

    fig = plot_deprecation_prediction_comparison(dummy_results)
    plt.show()
