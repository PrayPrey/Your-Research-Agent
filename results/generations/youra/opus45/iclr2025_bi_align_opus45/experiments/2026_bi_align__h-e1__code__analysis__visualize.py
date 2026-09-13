"""
Visualization Suite for H-E1 experiment.

Generates publication-quality figures:
1. Forest plot (effect sizes with CI)
2. Violin plot (score distributions)
3. Interaction plot (factorial analysis)
4. Gate metrics comparison
"""

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Configure matplotlib for publication quality
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.figsize': (10, 6),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Colorblind-friendly palette
COLORS = {
    'positive': '#2E86AB',  # Blue
    'negative': '#A23B72',  # Pink
    'neutral': '#F18F01',   # Orange
    'threshold': '#C73E1D', # Red
    'enumerated': '#2E86AB',
    'synthesized': '#A23B72',
}


def plot_forest(per_rm_df: pd.DataFrame, output_dir: str) -> None:
    """
    FR-4.1: Per-RM effect size forest plot with 95% CI.

    Args:
        per_rm_df: DataFrame with [rm, cohens_d, ci_low, ci_high]
        output_dir: Directory to save figures
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Sort by effect size
    df = per_rm_df.sort_values('cohens_d', ascending=True)
    y_pos = np.arange(len(df))

    # Plot effect sizes with CI
    for i, (_, row) in enumerate(df.iterrows()):
        color = COLORS['positive'] if row['cohens_d'] >= 0.3 else COLORS['neutral']
        ax.errorbar(
            row['cohens_d'], i,
            xerr=[[row['cohens_d'] - row['ci_low']], [row['ci_high'] - row['cohens_d']]],
            fmt='o', markersize=10, capsize=5,
            color=color, ecolor=color, elinewidth=2,
        )

    # Add threshold line
    ax.axvline(x=0.3, color=COLORS['threshold'], linestyle='--', linewidth=2,
               label='Gate Threshold (d=0.3)')
    ax.axvline(x=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)

    # Labels and formatting
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df['rm'].str.upper())
    ax.set_xlabel("Cohen's d (Effect Size)")
    ax.set_ylabel("Reward Model")
    ax.set_title("Enumeration Preference Effect Size by Reward Model\n(Positive = Enumerated > Synthesized)")
    ax.legend(loc='lower right')
    ax.grid(axis='x', alpha=0.3)

    # Add annotation for gate condition
    n_passing = sum(1 for d in df['cohens_d'] if d >= 0.3)
    gate_text = f"Gate: {n_passing}/4 RMs ≥ 0.3"
    ax.annotate(gate_text, xy=(0.02, 0.98), xycoords='axes fraction',
                fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Save
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path / "forest_plot.png")
    fig.savefig(output_path / "forest_plot.pdf")
    plt.close(fig)
    print(f"Saved forest plot to {output_path}")


def plot_violin(scores_df: pd.DataFrame, output_dir: str) -> None:
    """
    FR-4.2: Score distribution violin per RM (enumerated vs synthesized).

    Args:
        scores_df: DataFrame with [rm, structure, score]
        output_dir: Directory to save figures
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create violin plot
    palette = {
        'enumerated': COLORS['enumerated'],
        'synthesized': COLORS['synthesized'],
    }

    sns.violinplot(
        data=scores_df,
        x='rm', y='score', hue='structure',
        split=True, inner='box',
        palette=palette, ax=ax
    )

    # Formatting
    ax.set_xlabel("Reward Model")
    ax.set_ylabel("Reward Score (Normalized)")
    ax.set_title("Score Distribution: Enumerated vs. Synthesized Responses")
    ax.legend(title="Structure", loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    # Rotate x-axis labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

    # Save
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path / "violin_plot.png")
    fig.savefig(output_path / "violin_plot.pdf")
    plt.close(fig)
    print(f"Saved violin plot to {output_path}")


def plot_interaction(scores_df: pd.DataFrame, output_dir: str) -> None:
    """
    FR-4.3: Factorial interaction plot (Structure x Correctness x Completeness).

    Args:
        scores_df: DataFrame with [rm, structure, score, correctness, completeness]
        output_dir: Directory to save figures
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Check if factorial columns exist
    has_factorial = all(col in scores_df.columns for col in ['correctness', 'completeness'])

    if has_factorial:
        # Plot 1: Structure x Correctness
        ax1 = axes[0]
        interaction1 = scores_df.groupby(['structure', 'correctness'])['score'].mean().unstack()
        interaction1.plot(kind='bar', ax=ax1, color=[COLORS['positive'], COLORS['negative']])
        ax1.set_xlabel("Structure")
        ax1.set_ylabel("Mean Score")
        ax1.set_title("Structure × Correctness Interaction")
        ax1.legend(title="Correctness")
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)

        # Plot 2: Structure x Completeness
        ax2 = axes[1]
        interaction2 = scores_df.groupby(['structure', 'completeness'])['score'].mean().unstack()
        interaction2.plot(kind='bar', ax=ax2, color=[COLORS['positive'], COLORS['neutral']])
        ax2.set_xlabel("Structure")
        ax2.set_ylabel("Mean Score")
        ax2.set_title("Structure × Completeness Interaction")
        ax2.legend(title="Completeness")
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)
    else:
        # Simpler plot if factorial columns missing
        ax1 = axes[0]
        mean_scores = scores_df.groupby(['rm', 'structure'])['score'].mean().unstack()
        mean_scores.plot(kind='bar', ax=ax1, color=[COLORS['enumerated'], COLORS['synthesized']])
        ax1.set_xlabel("Reward Model")
        ax1.set_ylabel("Mean Score")
        ax1.set_title("Mean Score by RM and Structure")
        ax1.legend(title="Structure")
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)

        axes[1].axis('off')
        axes[1].text(0.5, 0.5, "Factorial columns\nnot available",
                     ha='center', va='center', fontsize=14)

    plt.tight_layout()

    # Save
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path / "interaction_plot.png")
    fig.savefig(output_path / "interaction_plot.pdf")
    plt.close(fig)
    print(f"Saved interaction plot to {output_path}")


def plot_gate_metrics(
    per_rm_df: pd.DataFrame,
    gate_threshold: float,
    output_dir: str
) -> None:
    """
    FR-4.4: Gate metrics comparison bar chart.

    Args:
        per_rm_df: DataFrame with [rm, cohens_d]
        gate_threshold: Effect size threshold for gate
        output_dir: Directory to save figures
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Prepare data
    df = per_rm_df.sort_values('cohens_d', ascending=False)
    x = np.arange(len(df))
    width = 0.35

    # Plot actual values
    colors = [COLORS['positive'] if d >= gate_threshold else COLORS['neutral']
              for d in df['cohens_d']]
    bars = ax.bar(x, df['cohens_d'], width, label='Actual', color=colors, edgecolor='black')

    # Plot threshold line
    ax.axhline(y=gate_threshold, color=COLORS['threshold'], linestyle='--',
               linewidth=2, label=f'Threshold (d={gate_threshold})')

    # Add value labels on bars
    for bar, val in zip(bars, df['cohens_d']):
        ax.annotate(f'{val:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords='offset points',
                    ha='center', va='bottom', fontsize=10)

    # Gate status annotation
    n_passing = sum(1 for d in df['cohens_d'] if d >= gate_threshold)
    gate_status = "PASS" if n_passing >= 2 else "FAIL"
    status_color = 'green' if gate_status == "PASS" else 'red'
    ax.annotate(f"Gate: {gate_status} ({n_passing}/4 ≥ {gate_threshold})",
                xy=(0.98, 0.98), xycoords='axes fraction',
                fontsize=14, fontweight='bold',
                verticalalignment='top', horizontalalignment='right',
                color=status_color,
                bbox=dict(boxstyle='round', facecolor='white', edgecolor=status_color))

    # Labels and formatting
    ax.set_xlabel("Reward Model")
    ax.set_ylabel("Cohen's d (Effect Size)")
    ax.set_title("Gate Condition: Effect Size by Reward Model")
    ax.set_xticks(x)
    ax.set_xticklabels(df['rm'].str.upper())
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(bottom=min(0, df['cohens_d'].min() - 0.1))

    # Save
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path / "gate_metrics.png")
    fig.savefig(output_path / "gate_metrics.pdf")
    plt.close(fig)
    print(f"Saved gate metrics plot to {output_path}")


def generate_all_figures(
    scores_df: pd.DataFrame,
    per_rm_df: pd.DataFrame,
    gate_threshold: float,
    output_dir: str
) -> None:
    """
    Generate all required figures.

    Args:
        scores_df: Raw scores DataFrame
        per_rm_df: Per-RM statistics DataFrame
        gate_threshold: Effect size threshold
        output_dir: Output directory for figures
    """
    print("Generating figures...")

    plot_forest(per_rm_df, output_dir)
    plot_violin(scores_df, output_dir)
    plot_interaction(scores_df, output_dir)
    plot_gate_metrics(per_rm_df, gate_threshold, output_dir)

    print(f"All figures saved to {output_dir}")
