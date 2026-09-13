"""Visualization generation module for h-m1 benchmark distinctiveness analysis."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List


class VisualizationGenerator:
    """Generate visualizations for benchmark distinctiveness analysis."""

    def __init__(
        self,
        correlation_matrix: pd.DataFrame,
        divergences: Dict[str, float],
        feature_df: pd.DataFrame,
        output_dir: str = "figures"
    ):
        """Initialize visualization generator."""
        self.correlation_matrix = correlation_matrix
        self.divergences = divergences
        self.feature_df = feature_df
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def plot_correlation_heatmap(self, save_path: str = None) -> str:
        """Plot correlation matrix heatmap (MANDATORY - gate metric)."""
        if save_path is None:
            save_path = self.output_dir / "correlation_heatmap.png"

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            self.correlation_matrix, annot=True, fmt='.3f', cmap='coolwarm',
            center=0.8, vmin=0.0, vmax=1.0,
            cbar_kws={'label': 'Spearman Correlation (ρ)'}, ax=ax
        )
        ax.set_title('Benchmark Ranking Correlation Matrix\n(Threshold: ρ = 0.8)', fontsize=14)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return str(save_path)

    def plot_kl_divergence_bars(self, save_path: str = None) -> str:
        """Plot KL divergence bar chart."""
        if save_path is None:
            save_path = self.output_dir / "kl_divergence_bars.png"

        fig, ax = plt.subplots(figsize=(10, 6))
        pairs = list(self.divergences.keys())
        values = list(self.divergences.values())
        bars = ax.bar(pairs, values, color='steelblue', alpha=0.7)
        
        threshold = 0.1
        for i, value in enumerate(values):
            if value > threshold:
                bars[i].set_color('darkgreen')
        
        ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold (KL = {threshold})')
        ax.set_xlabel('Benchmark Pair', fontsize=12)
        ax.set_ylabel('KL Divergence', fontsize=12)
        ax.set_title('KL Divergence Across Benchmark Pairs', fontsize=14)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return str(save_path)

    def plot_ranking_scatter(self, bench1: str, bench2: str, feature: str = 'pass@1', save_path: str = None) -> str:
        """Plot ranking scatter plot for two benchmarks."""
        if save_path is None:
            save_path = self.output_dir / f"ranking_scatter_{bench1.lower()}_{bench2.lower()}.png"

        scores1 = self.feature_df[self.feature_df['benchmark'] == bench1].set_index('model')[feature]
        scores2 = self.feature_df[self.feature_df['benchmark'] == bench2].set_index('model')[feature]
        common = scores1.index.intersection(scores2.index)
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(scores1.loc[common], scores2.loc[common], alpha=0.6, s=100, color='steelblue')
        
        lims = [min(scores1.loc[common].min(), scores2.loc[common].min()), 
                max(scores1.loc[common].max(), scores2.loc[common].max())]
        ax.plot(lims, lims, 'k--', alpha=0.3, label='Perfect Agreement')
        
        ax.set_xlabel(f'{bench1} {feature}', fontsize=12)
        ax.set_ylabel(f'{bench2} {feature}', fontsize=12)
        ax.set_title(f'Model Ranking: {bench1} vs {bench2}', fontsize=14)
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return str(save_path)

    def plot_feature_distributions(self, feature: str = 'pass@1', save_path: str = None) -> str:
        """Plot overlaid feature distributions for each benchmark."""
        if save_path is None:
            save_path = self.output_dir / "feature_distributions.png"

        fig, ax = plt.subplots(figsize=(10, 6))
        benchmarks = self.feature_df['benchmark'].unique()
        colors = sns.color_palette("husl", len(benchmarks))
        
        for bench, color in zip(benchmarks, colors):
            data = self.feature_df[self.feature_df['benchmark'] == bench][feature]
            ax.hist(data, bins=15, alpha=0.5, label=bench, color=color, density=True)
        
        ax.set_xlabel(feature, fontsize=12)
        ax.set_ylabel('Density', fontsize=12)
        ax.set_title(f'Feature Distribution: {feature}', fontsize=14)
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return str(save_path)

    def generate_all_figures(self) -> List[str]:
        """Generate all required figures."""
        figures = []
        figures.append(self.plot_correlation_heatmap())
        figures.append(self.plot_kl_divergence_bars())
        figures.append(self.plot_feature_distributions())
        
        benchmarks = self.correlation_matrix.index.tolist()
        for i, bench1 in enumerate(benchmarks):
            for bench2 in benchmarks[i+1:]:
                figures.append(self.plot_ranking_scatter(bench1, bench2))
        
        return figures
