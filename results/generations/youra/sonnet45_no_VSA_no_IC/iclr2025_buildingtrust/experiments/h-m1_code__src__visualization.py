"""Visualization for difficulty-controlled coupling analysis."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def plot_partial_vs_raw_phi(
    partial_results: pd.DataFrame,
    raw_phi: dict,
    output_path: str
):
    """Scatter plot comparing raw vs partial phi coefficients.

    Args:
        partial_results: DataFrame with columns [dim1, dim2, partial_r]
        raw_phi: {(dim1, dim2): phi} raw phi coefficients
        output_path: Output file path
    """
    plt.figure(figsize=(8, 6))

    raw_values = []
    partial_values = []
    labels = []

    for _, row in partial_results.iterrows():
        pair = (row['dim1'], row['dim2'])
        raw_values.append(raw_phi.get(pair, 0.0))
        partial_values.append(abs(row['partial_r']))
        labels.append(f"{row['dim1'][:4]}-{row['dim2'][:4]}")

    plt.scatter(raw_values, partial_values, s=100, alpha=0.7)

    for i, label in enumerate(labels):
        plt.annotate(label, (raw_values[i], partial_values[i]),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)

    plt.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='y=x')
    plt.axhline(0.25, color='r', linestyle='--', alpha=0.3, label='Threshold (0.25)')
    plt.axvline(0.25, color='r', linestyle='--', alpha=0.3)

    plt.xlabel('Raw Phi Coefficient')
    plt.ylabel('Partial Phi (|partial_r|)')
    plt.title('Raw vs Difficulty-Controlled Coupling')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_quartile_stratified_phi(
    quartile_results: pd.DataFrame,
    output_path: str
):
    """Line plot showing phi across quartiles for each dimension pair.

    Args:
        quartile_results: DataFrame with columns [dim1, dim2, quartile, phi]
        output_path: Output file path
    """
    plt.figure(figsize=(10, 6))

    for (dim1, dim2), group in quartile_results.groupby(['dim1', 'dim2']):
        label = f"{dim1[:4]}-{dim2[:4]}"
        plt.plot(group['quartile'], group['phi'], marker='o', label=label)

    plt.axhline(0.25, color='r', linestyle='--', alpha=0.3, label='Threshold (0.25)')
    plt.xlabel('Difficulty Quartile (0=easy, 3=hard)')
    plt.ylabel('Phi Coefficient')
    plt.title('Coupling Persistence Across Difficulty Quartiles')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_difficulty_independence(
    df: pd.DataFrame,
    dimensions: list[str],
    output_path: str
):
    """Correlation heatmap: difficulty vs dimension labels.

    Args:
        df: DataFrame with difficulty_score and dimension columns
        dimensions: List of dimension names
        output_path: Output file path
    """
    plt.figure(figsize=(6, 5))

    corr_data = []
    for dim in dimensions:
        corr = df[['difficulty_score', dim]].corr().iloc[0, 1]
        corr_data.append(corr)

    corr_matrix = pd.DataFrame({
        'Difficulty': corr_data
    }, index=dimensions)

    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm',
                center=0, vmin=-0.5, vmax=0.5, cbar_kws={'label': 'Correlation'})

    plt.title('Difficulty Independence Check\n(Should be near 0)')
    plt.ylabel('Dimension')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_effect_size_retention(
    partial_results: pd.DataFrame,
    raw_phi: dict,
    output_path: str
):
    """Bar plot: effect size retention after difficulty control.

    Args:
        partial_results: DataFrame with columns [dim1, dim2, partial_r]
        raw_phi: {(dim1, dim2): phi} raw phi coefficients
        output_path: Output file path
    """
    plt.figure(figsize=(10, 6))

    pairs = []
    retention_ratios = []
    raw_values = []
    partial_values = []

    for _, row in partial_results.iterrows():
        pair = (row['dim1'], row['dim2'])
        raw_val = raw_phi.get(pair, 0.0)
        partial_val = abs(row['partial_r'])

        pairs.append(f"{row['dim1'][:4]}-{row['dim2'][:4]}")
        raw_values.append(raw_val)
        partial_values.append(partial_val)

        if raw_val > 0:
            retention_ratios.append(partial_val / raw_val)
        else:
            retention_ratios.append(0.0)

    x = np.arange(len(pairs))
    width = 0.35

    plt.bar(x - width/2, raw_values, width, label='Raw Phi', alpha=0.7)
    plt.bar(x + width/2, partial_values, width, label='Partial Phi', alpha=0.7)

    plt.axhline(0.25, color='r', linestyle='--', alpha=0.3, label='Threshold (0.25)')
    plt.xlabel('Dimension Pair')
    plt.ylabel('Phi Coefficient')
    plt.title('Effect Size Retention After Difficulty Control')
    plt.xticks(x, pairs, rotation=45, ha='right')
    plt.legend()
    plt.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
