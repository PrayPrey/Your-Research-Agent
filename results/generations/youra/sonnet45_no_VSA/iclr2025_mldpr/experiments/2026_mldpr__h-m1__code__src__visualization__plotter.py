"""Visualization Module

Generates correlation plots and diagnostic visualizations.
"""

from typing import Tuple, Dict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path


class CorrelationVisualizer:
    """Creates visualizations for correlation analysis."""

    def __init__(self, output_dir: str = "figures"):
        """Initialize visualizer.

        Args:
            output_dir: Directory for saving figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 11

    def plot_primary_scatter(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        rho: float,
        p_value: float,
        title: str = None
    ) -> None:
        """Plot scatter plot with correlation statistics.

        Args:
            df: DataFrame with data
            x_col: X-axis column name
            y_col: Y-axis column name
            rho: Spearman correlation coefficient
            p_value: P-value
            title: Plot title (optional)
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Scatter plot
        ax.scatter(df[x_col], df[y_col], alpha=0.6, s=80, edgecolors='black', linewidth=0.5)

        # Add trend line (rank-based)
        x_ranks = df[x_col].rank()
        y_ranks = df[y_col].rank()
        z = np.polyfit(x_ranks, y_ranks, 1)
        p = np.poly1d(z)
        x_line = np.linspace(df[x_col].min(), df[x_col].max(), 100)
        x_line_ranks = pd.Series(x_line).rank()
        y_line_ranks = p(x_line_ranks)
        # Convert ranks back to values (approximate)
        y_line = df[y_col].min() + (y_line_ranks - y_ranks.min()) * (df[y_col].max() - df[y_col].min()) / (y_ranks.max() - y_ranks.min())
        ax.plot(x_line, y_line, 'r--', alpha=0.5, linewidth=2)

        # Labels
        ax.set_xlabel(x_col.replace('_', ' ').title(), fontsize=13)
        ax.set_ylabel(y_col.replace('_', ' ').title(), fontsize=13)

        if title is None:
            title = f"{x_col.replace('_', ' ').title()} vs {y_col.replace('_', ' ').title()}"
        ax.set_title(title, fontsize=15, fontweight='bold')

        # Statistics box
        stats_text = f'Spearman ρ = {rho:.3f}\np = {p_value:.4f}\nn = {len(df)}'
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
                fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        filename = self.output_dir / f"scatter_{x_col}_vs_{y_col}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {filename}")

    def plot_correlation_matrix(self, df: pd.DataFrame) -> None:
        """Plot correlation matrix heatmap.

        Args:
            df: DataFrame with all metrics
        """
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numeric_cols].corr(method='spearman')

        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                    center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                    vmin=-1, vmax=1, ax=ax)

        ax.set_title('Spearman Correlation Matrix', fontsize=15, fontweight='bold', pad=20)
        plt.tight_layout()

        filename = self.output_dir / "correlation_matrix.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {filename}")

    def plot_partial_comparison(
        self,
        raw_rho: float,
        partial_rho: float,
        ci_raw: Tuple[float, float],
        ci_partial: Tuple[float, float],
        metric_name: str = "Activity Metric"
    ) -> None:
        """Plot comparison of raw vs partial correlation.

        Args:
            raw_rho: Raw Spearman correlation
            partial_rho: Partial correlation (age-controlled)
            ci_raw: 95% CI for raw correlation
            ci_partial: 95% CI for partial correlation
            metric_name: Name of the activity metric
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = ['Raw Correlation', 'Partial Correlation\n(Age-Controlled)']
        rhos = [raw_rho, partial_rho]
        errors = [
            [raw_rho - ci_raw[0], ci_raw[1] - raw_rho],
            [partial_rho - ci_partial[0], ci_partial[1] - partial_rho]
        ]

        x_pos = np.arange(len(categories))
        ax.bar(x_pos, rhos, yerr=np.array(errors).T, capsize=10, alpha=0.7,
               color=['steelblue', 'coral'], edgecolor='black', linewidth=1.5)

        # Add horizontal line at ρ = 0.30 (primary threshold)
        ax.axhline(y=0.30, color='red', linestyle='--', linewidth=2, label='Primary Threshold (ρ=0.30)')
        # Add horizontal line at ρ = 0.25 (secondary threshold)
        ax.axhline(y=0.25, color='orange', linestyle='--', linewidth=2, label='Secondary Threshold (ρ=0.25)')

        ax.set_ylabel('Spearman ρ', fontsize=13)
        ax.set_title(f'{metric_name} vs DCS_3: Raw vs Partial Correlation', fontsize=15, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories, fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        filename = self.output_dir / f"partial_comparison_{metric_name.replace(' ', '_').lower()}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {filename}")

    def plot_component_correlations(self, df: pd.DataFrame, results: Dict) -> None:
        """Plot correlations for all activity metrics.

        Args:
            df: DataFrame with all metrics
            results: Dict with correlation results for each metric
        """
        fig, axes = plt.subplots(1, len(results), figsize=(15, 5))

        if len(results) == 1:
            axes = [axes]

        for idx, (metric_col, metric_results) in enumerate(results.items()):
            ax = axes[idx]

            spearman = metric_results.get('spearman', {})
            rho = spearman.get('rho', 0.0)
            p_value = spearman.get('p_value', 1.0)

            # Scatter plot
            ax.scatter(df[metric_col], df['dcs_3_score'], alpha=0.6, s=60,
                       edgecolors='black', linewidth=0.5)

            # Labels
            ax.set_xlabel(metric_col.replace('_', ' ').title(), fontsize=11)
            ax.set_ylabel('DCS_3 Score', fontsize=11)
            ax.set_title(f'ρ = {rho:.3f}, p = {p_value:.4f}', fontsize=12)

            # Grid
            ax.grid(alpha=0.3)

        fig.suptitle('Activity Metrics vs Documentation Quality', fontsize=15, fontweight='bold')
        plt.tight_layout()

        filename = self.output_dir / "component_correlations.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {filename}")
