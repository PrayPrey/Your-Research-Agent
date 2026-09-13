"""
Visualization Generator
Generates required figures for gate metric validation
Based on 03_architecture.md specifications
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


class VisualizationGenerator:
    """Generate visualizations for execution trace features."""

    def __init__(self, feature_df: pd.DataFrame, output_dir: str = "figures"):
        self.feature_df = feature_df
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['font.size'] = 12

    def plot_completeness_comparison(self, completeness_rate: float, threshold: float = 95.0) -> str:
        """
        Figure 1: Feature completeness comparison (GATE METRIC).
        Bar chart showing overall completeness vs threshold.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = ['Overall\nCompleteness', 'Required\nThreshold']
        values = [completeness_rate, threshold]
        colors = ['green' if completeness_rate >= threshold else 'orange', 'gray']

        bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1f}%',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_ylabel('Completeness (%)', fontsize=14)
        ax.set_title('Feature Completeness: Gate Metric Validation', fontsize=16, fontweight='bold')
        ax.set_ylim([0, 105])
        ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold}%)')
        ax.legend(fontsize=12)

        # Add gate result annotation
        gate_status = "PASS ✓" if completeness_rate >= threshold else "FAIL ✗"
        gate_color = "green" if completeness_rate >= threshold else "red"
        ax.text(0.5, 0.95, f'Gate Status: {gate_status}',
               transform=ax.transAxes, ha='center', va='top',
               bbox=dict(boxstyle='round', facecolor=gate_color, alpha=0.3),
               fontsize=14, fontweight='bold')

        output_path = self.output_dir / "completeness_comparison.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_feature_coverage_heatmap(self) -> str:
        """
        Figure 2: Feature coverage heatmap (models × benchmarks).
        """
        # Create pivot table for heatmap
        if 'model' not in self.feature_df.columns or 'benchmark' not in self.feature_df.columns:
            print("Warning: Cannot create heatmap without model and benchmark columns")
            return None

        # Calculate completeness per model-benchmark pair
        completeness_data = []
        for idx, row in self.feature_df.iterrows():
            required_features = ['pass@1', 'pass@10', 'pass@100',
                               'runtime_q25', 'runtime_q50', 'runtime_q75',
                               'error_syntax', 'error_runtime', 'error_timeout']
            complete_count = sum(1 for feat in required_features if pd.notna(row.get(feat)))
            completeness_pct = (complete_count / len(required_features)) * 100

            completeness_data.append({
                'model': row['model'],
                'benchmark': row['benchmark'],
                'completeness': completeness_pct
            })

        completeness_df = pd.DataFrame(completeness_data)
        pivot = completeness_df.pivot(index='model', columns='benchmark', values='completeness')

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pivot, annot=True, fmt='.0f', cmap='RdYlGn', center=50,
                   vmin=0, vmax=100, cbar_kws={'label': 'Completeness (%)'},
                   linewidths=0.5, linecolor='gray', ax=ax)

        ax.set_title('Feature Coverage Heatmap: Models × Benchmarks', fontsize=14, fontweight='bold')
        ax.set_xlabel('Benchmark', fontsize=12)
        ax.set_ylabel('Model', fontsize=12)

        output_path = self.output_dir / "feature_coverage_heatmap.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_feature_distributions(self) -> str:
        """
        Figure 3: Feature distribution histograms.
        """
        features_to_plot = ['pass@1', 'runtime_q50', 'error_runtime']

        fig, axes = plt.subplots(1, 3, figsize=(15, 4))

        for idx, feature in enumerate(features_to_plot):
            if feature in self.feature_df.columns:
                data = self.feature_df[feature].dropna()
                if len(data) > 0:
                    axes[idx].hist(data, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
                    axes[idx].set_xlabel(feature, fontsize=12)
                    axes[idx].set_ylabel('Frequency', fontsize=12)
                    axes[idx].set_title(f'{feature} Distribution', fontsize=12, fontweight='bold')
                    axes[idx].grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / "feature_distributions.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_coverage_matrix(self) -> str:
        """
        Figure 4: Model-benchmark coverage matrix (binary).
        """
        if 'model' not in self.feature_df.columns or 'benchmark' not in self.feature_df.columns:
            return None

        # Create binary coverage matrix
        coverage_data = []
        for idx, row in self.feature_df.iterrows():
            has_passk = pd.notna(row.get('pass@1'))
            coverage_data.append({
                'model': row['model'],
                'benchmark': row['benchmark'],
                'has_data': 1 if has_passk else 0
            })

        coverage_df = pd.DataFrame(coverage_data)
        pivot = coverage_df.pivot(index='model', columns='benchmark', values='has_data')

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pivot, annot=True, fmt='.0f', cmap='RdYlGn', center=0.5,
                   vmin=0, vmax=1, cbar_kws={'label': 'Has Data (1=Yes, 0=No)'},
                   linewidths=0.5, linecolor='gray', ax=ax)

        ax.set_title('Model-Benchmark Coverage Matrix', fontsize=14, fontweight='bold')
        ax.set_xlabel('Benchmark', fontsize=12)
        ax.set_ylabel('Model', fontsize=12)

        output_path = self.output_dir / "coverage_matrix.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def generate_all_figures(self, completeness_rate: float, threshold: float = 95.0) -> list:
        """Generate all required figures."""
        figures = []

        fig1 = self.plot_completeness_comparison(completeness_rate, threshold)
        if fig1:
            figures.append(fig1)

        fig2 = self.plot_feature_coverage_heatmap()
        if fig2:
            figures.append(fig2)

        fig3 = self.plot_feature_distributions()
        if fig3:
            figures.append(fig3)

        fig4 = self.plot_coverage_matrix()
        if fig4:
            figures.append(fig4)

        return figures
