"""
Visualization Module for H-M1 Correlation Analysis
Generates required figures for validation report.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple


class CorrelationVisualizer:
    """Generate visualizations for correlation analysis results."""

    def __init__(self, output_dir: str):
        """
        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set consistent style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300

    def plot_gate_metrics(
        self,
        correlations: Dict[str, Dict],
        threshold: float = 0.3,
        top_n: int = 10
    ):
        """
        Figure 1: Gate Metrics Comparison
        Bar chart showing correlation strength vs threshold.
        """
        # Get top correlations by |rho|
        sorted_pairs = sorted(
            correlations.items(),
            key=lambda x: abs(x[1]['rho']),
            reverse=True
        )[:top_n]

        names = [name.replace('_vs_', '\nvs\n') for name, _ in sorted_pairs]
        rhos = [data['rho'] for _, data in sorted_pairs]
        colors = ['green' if abs(r) > threshold else 'orange' for r in rhos]

        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(range(len(names)), rhos, color=colors, alpha=0.7)

        # Threshold line
        ax.axhline(y=threshold, color='red', linestyle='--', label=f'Threshold (ρ={threshold})')
        ax.axhline(y=-threshold, color='red', linestyle='--')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        ax.set_xlabel('Feature-Method Pairs', fontsize=12)
        ax.set_ylabel('Spearman Correlation (ρ)', fontsize=12)
        ax.set_title('H-M1: Feature-Ranking Correlation Analysis (Gate Metrics)', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        save_path = self.output_dir / 'gate_metrics.png'
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved: {save_path}")

    def plot_correlation_heatmap(
        self,
        features_df: pd.DataFrame,
        rankings_df: pd.DataFrame,
        correlations: Dict[str, Dict]
    ):
        """
        Figure 2: Feature-Method Correlation Heatmap
        """
        # Build correlation matrix
        feature_names = features_df.columns.tolist()
        method_names = rankings_df.columns.tolist()

        corr_matrix = np.zeros((len(feature_names), len(method_names)))

        for i, feature in enumerate(feature_names):
            for j, method in enumerate(method_names):
                pair_name = f"{feature}_vs_{method}"
                if pair_name in correlations:
                    corr_matrix[i, j] = correlations[pair_name]['rho']

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt='.2f',
            cmap='RdBu_r',
            center=0,
            vmin=-1,
            vmax=1,
            xticklabels=method_names,
            yticklabels=feature_names,
            cbar_kws={'label': 'Spearman ρ'},
            ax=ax
        )

        ax.set_title('Feature-Method Correlation Matrix', fontsize=14, fontweight='bold')
        ax.set_xlabel('Method Families', fontsize=12)
        ax.set_ylabel('Dataset Features', fontsize=12)

        plt.tight_layout()
        save_path = self.output_dir / 'heatmap.png'
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved: {save_path}")

    def plot_significance(
        self,
        correlations: Dict[str, Dict],
        alpha: float = 0.05,
        top_n: int = 15
    ):
        """
        Figure 3: Significance Plot
        Bar chart of p-values with threshold line.
        """
        # Get correlations sorted by p-value
        sorted_pairs = sorted(
            correlations.items(),
            key=lambda x: x[1]['p_value']
        )[:top_n]

        names = [name.replace('_vs_', '\nvs\n') for name, _ in sorted_pairs]
        p_values = [data['p_value'] for _, data in sorted_pairs]
        colors = ['green' if p < alpha else 'red' for p in p_values]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(range(len(names)), p_values, color=colors, alpha=0.7)

        # Threshold line
        ax.axhline(y=alpha, color='red', linestyle='--', linewidth=2, label=f'α={alpha}')

        ax.set_xlabel('Feature-Method Pairs', fontsize=12)
        ax.set_ylabel('p-value', fontsize=12)
        ax.set_title('Statistical Significance of Correlations', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
        ax.set_yscale('log')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        save_path = self.output_dir / 'significance.png'
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved: {save_path}")

    def plot_top_scatter_plots(
        self,
        features_df: pd.DataFrame,
        rankings_df: pd.DataFrame,
        correlations: Dict[str, Dict],
        top_n: int = 3
    ):
        """
        Figure 4: Top 3 Scatter Plots
        Scatter plots for strongest correlations.
        """
        # Get top 3 significant correlations
        sorted_pairs = sorted(
            [
                (name, data)
                for name, data in correlations.items()
                if data['significant']
            ],
            key=lambda x: abs(x[1]['rho']),
            reverse=True
        )[:top_n]

        if not sorted_pairs:
            print("⚠️ No significant correlations to plot")
            return

        fig, axes = plt.subplots(1, len(sorted_pairs), figsize=(6*len(sorted_pairs), 5))
        if len(sorted_pairs) == 1:
            axes = [axes]

        for ax, (pair_name, data) in zip(axes, sorted_pairs):
            # Parse feature and method names
            feature_name, method_name = pair_name.split('_vs_')

            # Get data
            feature_values = features_df[feature_name].values
            ranking_values = rankings_df[method_name].values

            # Remove NaN
            mask = ~(np.isnan(feature_values) | np.isnan(ranking_values))
            x = feature_values[mask]
            y = ranking_values[mask]

            # Scatter plot
            ax.scatter(x, y, alpha=0.6, s=50)

            # Regression line (with error handling)
            try:
                if len(set(x)) > 1:  # Need variation in x for regression
                    z = np.polyfit(x, y, 1)
                    p = np.poly1d(z)
                    x_sorted = np.sort(x)
                    ax.plot(x_sorted, p(x_sorted), "r--", alpha=0.8, linewidth=2)
            except:
                pass  # Skip regression line if it fails

            ax.set_xlabel(feature_name.replace('_', ' ').title(), fontsize=11)
            ax.set_ylabel(f"{method_name} Ranking %ile", fontsize=11)
            ax.set_title(f"ρ={data['rho']:.3f}, p={data['p_value']:.4f}", fontsize=12, fontweight='bold')
            ax.grid(alpha=0.3)

        plt.suptitle('Top Correlations: Feature vs Method Performance', fontsize=14, fontweight='bold')
        plt.tight_layout()

        save_path = self.output_dir / 'scatter.png'
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved: {save_path}")
