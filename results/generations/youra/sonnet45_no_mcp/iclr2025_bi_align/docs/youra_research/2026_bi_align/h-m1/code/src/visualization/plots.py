"""
Visualization functions for annotation study results.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path


def plot_base_rate_comparison(
    base_rate: float,
    threshold: float = 0.40,
    p_value: float = None,
    output_path: str = "outputs/figures/base_rate.png"
) -> None:
    """
    Generate bar chart comparing base-rate to threshold.

    Args:
        base_rate: Observed base-rate p
        threshold: Null hypothesis threshold (0.40)
        p_value: Binomial test p-value (for annotation)
        output_path: Save path for figure
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Bar chart
    labels = ['Threshold\n(H0: p < 0.40)', 'Observed\nBase-Rate']
    values = [threshold, base_rate]
    colors = ['#d62728', '#2ca02c' if base_rate >= threshold else '#ff7f0e']

    bars = ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')

    # Horizontal line at threshold
    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label='Threshold (0.40)')

    # Annotations
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.3f}',
                ha='center', va='bottom', fontsize=14, fontweight='bold')

    # Add p-value annotation if provided
    if p_value is not None:
        decision = "PASS" if p_value < 0.05 else "FAIL"
        color = "green" if decision == "PASS" else "red"
        ax.text(0.5, 0.95, f'Binomial Test: p = {p_value:.4f} ({decision})',
                transform=ax.transAxes,
                ha='center', va='top',
                fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor=color, alpha=0.3))

    ax.set_ylabel('Proportion', fontsize=12)
    ax.set_title('Base-Rate of Genuine Safety Violations\nvs MUST_WORK Gate Threshold',
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(1.0, max(values) * 1.2))
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved base-rate comparison to {output_path}")


def plot_agreement_heatmap(
    pairwise_kappas: pd.DataFrame,
    output_path: str = "outputs/figures/agreement_heatmap.png"
) -> None:
    """
    Generate heatmap of inter-annotator agreement (Cohen's kappa).

    Args:
        pairwise_kappas: 3×3 DataFrame of pairwise kappa values
        output_path: Save path for figure
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Heatmap
    sns.heatmap(pairwise_kappas, annot=True, fmt='.3f', cmap='RdYlGn',
                vmin=0, vmax=1, center=0.5,
                cbar_kws={'label': "Cohen's Kappa"},
                ax=ax, square=True, linewidths=1)

    ax.set_title("Inter-Annotator Agreement Matrix\n(Cohen's Kappa)",
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Annotator ID', fontsize=12)
    ax.set_ylabel('Annotator ID', fontsize=12)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved agreement heatmap to {output_path}")


def plot_violation_distribution(
    annotations: pd.DataFrame,
    output_path: str = "outputs/figures/violation_types.png"
) -> None:
    """
    Generate bar chart of violation type frequency.

    Args:
        annotations: DataFrame with violation counts
        output_path: Save path for figure
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # For this simplified version, we'll show distribution of judgments
    fig, ax = plt.subplots(figsize=(8, 6))

    # Count violations vs non-violations
    violation_counts = annotations.groupby('judgment').size()

    labels = ['Marginal Preference', 'Genuine Violation']
    # Handle both boolean and integer judgments
    false_count = violation_counts.get(False, 0)
    if false_count == 0:
        false_count = violation_counts.get(0, 0)
    true_count = violation_counts.get(True, 0)
    if true_count == 0:
        true_count = violation_counts.get(1, 0)

    values = [false_count, true_count]
    colors = ['#ff7f0e', '#d62728']

    bars = ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')

    # Annotations
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value}\n({value/sum(values)*100:.1f}%)',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution of Annotation Judgments',
                 fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved violation distribution to {output_path}")


def plot_length_bias(
    samples: pd.DataFrame,
    final_labels: np.ndarray,
    output_path: str = "outputs/figures/length_bias.png"
) -> None:
    """
    Generate scatter plot of violation rate vs response length quartile.

    Args:
        samples: DataFrame with length_quartile column
        final_labels: Binary array (1=violation, 0=marginal)
        output_path: Save path for figure
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Add final labels to samples
    samples_with_labels = samples.copy()
    samples_with_labels['final_label'] = final_labels

    # Calculate violation rate per quartile
    quartile_stats = samples_with_labels.groupby('length_quartile')['final_label'].agg([
        ('violation_rate', 'mean'),
        ('count', 'size')
    ]).reset_index()

    fig, ax = plt.subplots(figsize=(8, 6))

    # Bar chart (better than scatter for categorical quartiles)
    bars = ax.bar(quartile_stats['length_quartile'],
                  quartile_stats['violation_rate'],
                  color='steelblue', alpha=0.7, edgecolor='black')

    # Annotations
    for bar, row in zip(bars, quartile_stats.itertuples()):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{row.violation_rate:.3f}\n(n={row.count})',
                ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('Response Length Quartile', fontsize=12)
    ax.set_ylabel('Violation Rate', fontsize=12)
    ax.set_title('Violation Rate by Response Length Quartile',
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.0)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved length bias analysis to {output_path}")
