"""Visualization module for dose-response analysis."""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict


def plot_dose_response_curve(aggregated_df: pd.DataFrame, stats: Dict, save_path: str):
    """
    Dose-response with error bars + Spearman annotation.

    Args:
        aggregated_df: Aggregated results (from aggregate_seed_results)
        stats: Spearman test results (from compute_spearman_correlation)
        save_path: Output file path
    """
    # Filter to flip conditions
    flip_data = aggregated_df[aggregated_df['condition'].isin(['baseline', 'flip30', 'flip50', 'flip90'])].copy()

    # Map to probabilities
    prob_map = {'baseline': 0.0, 'flip30': 0.3, 'flip50': 0.5, 'flip90': 0.9}
    flip_data['flip_prob'] = flip_data['condition'].map(prob_map)
    flip_data = flip_data.sort_values('flip_prob')

    # Plot
    plt.figure(figsize=(8, 6))
    plt.errorbar(
        flip_data['flip_prob'],
        flip_data['mean_asym'],
        yerr=flip_data['std_asym'],
        marker='o',
        markersize=10,
        linewidth=2,
        capsize=5,
        label='Asymmetric digits (2,3,5,6,7,9)'
    )

    # Add rotation control as separate point
    rotation_data = aggregated_df[aggregated_df['condition'] == 'rotation']
    if not rotation_data.empty:
        plt.scatter(
            [0.5],
            rotation_data['mean_asym'].values,
            marker='x',
            s=200,
            c='red',
            label='Rotation control',
            zorder=5
        )

    # Annotations
    plt.xlabel('Horizontal Flip Probability', fontsize=12)
    plt.ylabel('Asymmetric Digit Accuracy (%)', fontsize=12)
    plt.title('Dose-Response: Flip Probability Effect on Asymmetric Digits', fontsize=14)

    # Spearman annotation
    plt.text(
        0.05, 0.95,
        f"Spearman ρ = {stats['rho']:.3f}\np = {stats['p_value']:.4f}",
        transform=plt.gca().transAxes,
        fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )

    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_seed_variability_boxplot(results_df: pd.DataFrame, save_path: str):
    """
    Box plots showing distribution across seeds.

    Args:
        results_df: Raw per-seed results
        save_path: Output file path
    """
    plt.figure(figsize=(10, 6))

    # Order conditions
    order = ['baseline', 'flip30', 'flip50', 'flip90', 'rotation']

    sns.boxplot(
        data=results_df,
        x='condition',
        y='asymmetric_acc',
        order=order,
        palette='Set2'
    )

    plt.xlabel('Condition', fontsize=12)
    plt.ylabel('Asymmetric Digit Accuracy (%)', fontsize=12)
    plt.title('Seed Variability Across Conditions (n=5 seeds)', fontsize=14)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_scatter_with_regression(results_df: pd.DataFrame, stats: Dict, save_path: str):
    """
    Scatter plot with all 20 data points.

    Args:
        results_df: Raw per-seed results
        stats: Spearman test results
        save_path: Output file path
    """
    # Filter to flip conditions
    flip_data = results_df[results_df['condition'].isin(['baseline', 'flip30', 'flip50', 'flip90'])].copy()

    # Map to probabilities
    prob_map = {'baseline': 0.0, 'flip30': 0.3, 'flip50': 0.5, 'flip90': 0.9}
    flip_data['flip_prob'] = flip_data['condition'].map(prob_map)

    # Plot scatter
    plt.figure(figsize=(8, 6))
    plt.scatter(
        flip_data['flip_prob'],
        flip_data['asymmetric_acc'],
        alpha=0.6,
        s=100,
        edgecolors='black'
    )

    # Add trend line
    z = np.polyfit(flip_data['flip_prob'], flip_data['asymmetric_acc'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(0, 0.9, 100)
    plt.plot(x_line, p(x_line), 'r--', linewidth=2, label='Linear fit')

    plt.xlabel('Horizontal Flip Probability', fontsize=12)
    plt.ylabel('Asymmetric Digit Accuracy (%)', fontsize=12)
    plt.title(f'Dose-Response Scatter (n=20 data points)\nSpearman ρ={stats["rho"]:.3f}, p={stats["p_value"]:.4f}', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
