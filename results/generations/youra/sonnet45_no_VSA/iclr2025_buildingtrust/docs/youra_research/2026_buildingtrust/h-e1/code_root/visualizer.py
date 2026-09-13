"""Visualization module for H-E1 Cross-Benchmark Analysis."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict
import os


class CorrelationVisualizer:
    """Visualization for correlation analysis results."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_correlation_heatmap(
        self, corr_matrix: pd.DataFrame, pvalues: pd.DataFrame,
        dpi: int = 300, figsize: Tuple[int, int] = (8, 6)
    ) -> None:
        """Plot 3x3 heatmap. Saves to {output_dir}/correlation_heatmap.png"""
        plt.figure(figsize=figsize)

        # Create annotation matrix with significance markers
        annot_matrix = corr_matrix.copy().astype(str)
        for i in corr_matrix.index:
            for j in corr_matrix.columns:
                rho = corr_matrix.loc[i, j]
                pval = pvalues.loc[i, j]

                if i == j:
                    annot_matrix.loc[i, j] = "1.00"
                else:
                    # Add significance markers
                    if pval < 0.001:
                        marker = "***"
                    elif pval < 0.01:
                        marker = "**"
                    elif pval < 0.05:
                        marker = "*"
                    else:
                        marker = ""

                    annot_matrix.loc[i, j] = f"{rho:.2f}{marker}"

        # Plot heatmap
        sns.heatmap(
            corr_matrix,
            annot=annot_matrix,
            fmt='s',
            cmap='RdYlGn',
            center=0,
            vmin=-1.0,
            vmax=1.0,
            square=True,
            linewidths=1,
            cbar_kws={'label': 'Spearman ρ'}
        )

        plt.title('Cross-Benchmark Ranking Correlation Heatmap', fontsize=14, fontweight='bold')
        plt.xlabel('Benchmark', fontsize=12)
        plt.ylabel('Benchmark', fontsize=12)
        plt.tight_layout()

        output_path = os.path.join(self.output_dir, 'correlation_heatmap.png')
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close()

        print(f"[Visualization] Saved heatmap: {output_path}")

    def plot_scatter_pair(
        self,
        rank1: pd.Series,
        rank2: pd.Series,
        benchmark_names: Tuple[str, str],
        rho: float,
        pvalue: float,
        dpi: int = 300,
        figsize: Tuple[int, int] = (6, 6)
    ) -> None:
        """Plot scatter. Saves to {output_dir}/scatter_{b1}_{b2}.png"""
        b1, b2 = benchmark_names

        plt.figure(figsize=figsize)

        # Align series by index
        common_idx = rank1.index.intersection(rank2.index)
        x = rank1.loc[common_idx].values
        y = rank2.loc[common_idx].values

        # Scatter plot
        plt.scatter(x, y, alpha=0.6, s=100, c='#3498db', edgecolors='black', linewidth=0.5)

        # Add trend line
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        plt.plot(x_line, p(x_line), 'r--', alpha=0.7, linewidth=2, label='Trend')

        # Labels
        plt.xlabel(f'{b1} Rank', fontsize=12)
        plt.ylabel(f'{b2} Rank', fontsize=12)
        plt.title(f'{b1} vs {b2}\nρ = {rho:.3f}, p = {pvalue:.4f}', fontsize=13, fontweight='bold')

        # Add grid
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend(fontsize=10)
        plt.tight_layout()

        # Sanitize filename
        filename = f"scatter_{b1.replace(' ', '_')}_{b2.replace(' ', '_')}.png"
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close()

        print(f"[Visualization] Saved scatter plot: {output_path}")

    def plot_gate_metrics(
        self,
        target_range: Tuple[float, float],
        actual_correlations: Dict[str, float],
        dpi: int = 300,
        figsize: Tuple[int, int] = (10, 6)
    ) -> None:
        """Plot bar chart. Saves to {output_dir}/gate_metrics.png"""
        plt.figure(figsize=figsize)

        pairs = list(actual_correlations.keys())
        rhos = list(actual_correlations.values())
        colors = ['#2ecc71' if target_range[0] <= rho <= target_range[1] else '#e74c3c' for rho in rhos]

        # Bar plot
        bars = plt.bar(pairs, rhos, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

        # Add target range
        plt.axhline(y=target_range[0], color='blue', linestyle='--', linewidth=2, label=f'Target Min (ρ={target_range[0]})')
        plt.axhline(y=target_range[1], color='blue', linestyle='--', linewidth=2, label=f'Target Max (ρ={target_range[1]})')

        # Fill target zone
        plt.axhspan(target_range[0], target_range[1], alpha=0.1, color='blue', label='Target Range')

        # Add value labels on bars
        for bar, rho in zip(bars, rhos):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{rho:.3f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=10)

        plt.xlabel('Benchmark Pair', fontsize=12)
        plt.ylabel('Spearman ρ', fontsize=12)
        plt.title('Gate Metrics: Correlation vs Target Range', fontsize=14, fontweight='bold')
        plt.ylim(-0.1, 1.1)
        plt.legend(fontsize=10, loc='upper right')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.xticks(rotation=15, ha='right')
        plt.tight_layout()

        output_path = os.path.join(self.output_dir, 'gate_metrics.png')
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close()

        print(f"[Visualization] Saved gate metrics: {output_path}")
