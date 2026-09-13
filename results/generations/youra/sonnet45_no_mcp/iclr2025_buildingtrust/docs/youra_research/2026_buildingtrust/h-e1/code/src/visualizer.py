"""Visualization Module

This module generates figures for data availability analysis.
Creates publication-quality visualizations with matplotlib and seaborn.
"""

import logging
from typing import Dict, List
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


logger = logging.getLogger(__name__)


class ExperimentVisualizer:
    """Generates visualizations for experiment results."""

    def __init__(self, extracted_df: pd.DataFrame, metrics: Dict):
        """
        Initialize visualizer.

        Args:
            extracted_df: Extracted data DataFrame
            metrics: Metrics from GateMetricsAnalyzer
        """
        self.df = extracted_df
        self.metrics = metrics

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 300

    def plot_gate_metrics(self, save_path: str) -> None:
        """
        Plot gate metrics bar chart (MANDATORY).

        Args:
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Data for plotting
        families_with_both = self.metrics['families_with_both_count']
        threshold = 3

        # Bar chart
        categories = ['Families with\nBoth Timepoints']
        values = [families_with_both]

        colors = ['#06A77D' if families_with_both >= threshold else '#C73E1D']

        ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold})')

        # Labels
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('Gate Metric: Model Family Coverage', fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(threshold + 1, families_with_both + 1))
        ax.legend()

        # Add value labels on bars
        for i, v in enumerate(values):
            ax.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved gate metrics chart: {save_path}")

    def plot_granularity_heatmap(self, save_path: str) -> None:
        """
        Plot category granularity heatmap.

        Args:
            save_path: Path to save figure
        """
        # Create pivot table: families × benchmarks
        pivot_data = []
        for family in self.df['model_family'].unique():
            row_data = {'family': family}
            for benchmark in self.df['benchmark'].unique():
                subset = self.df[
                    (self.df['model_family'] == family) &
                    (self.df['benchmark'] == benchmark)
                ]
                category_count = subset['category'].nunique()
                row_data[benchmark] = category_count
            pivot_data.append(row_data)

        if not pivot_data:
            logger.warning("No data for granularity heatmap")
            return

        pivot_df = pd.DataFrame(pivot_data).set_index('family')

        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 8))

        sns.heatmap(
            pivot_df,
            annot=True,
            fmt='d',
            cmap='YlGnBu',
            cbar_kws={'label': 'Category Count'},
            linewidths=0.5,
            ax=ax
        )

        ax.set_title('Category Granularity by Model Family and Benchmark',
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Benchmark', fontsize=12, fontweight='bold')
        ax.set_ylabel('Model Family', fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved granularity heatmap: {save_path}")

    def plot_completeness_matrix(self, save_path: str) -> None:
        """
        Plot data completeness matrix.

        Args:
            save_path: Path to save figure
        """
        # Create completeness matrix: families × (benchmark × timepoint)
        matrix_data = []
        for family in self.df['model_family'].unique():
            row_data = {'family': family}
            for benchmark in self.df['benchmark'].unique():
                for timepoint in ['baseline', 'current']:
                    subset = self.df[
                        (self.df['model_family'] == family) &
                        (self.df['benchmark'] == benchmark) &
                        (self.df['timepoint'] == timepoint)
                    ]
                    # Calculate completeness
                    if len(subset) > 0:
                        completeness = (subset['error_rate'].notna().sum() / len(subset)) * 100
                    else:
                        completeness = 0
                    key = f"{benchmark}\n{timepoint}"
                    row_data[key] = completeness
            matrix_data.append(row_data)

        if not matrix_data:
            logger.warning("No data for completeness matrix")
            return

        matrix_df = pd.DataFrame(matrix_data).set_index('family')

        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 8))

        sns.heatmap(
            matrix_df,
            annot=True,
            fmt='.0f',
            cmap='RdYlGn',
            vmin=0,
            vmax=100,
            cbar_kws={'label': 'Completeness %'},
            linewidths=0.5,
            ax=ax
        )

        ax.set_title('Data Completeness Matrix',
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Benchmark × Timepoint', fontsize=12, fontweight='bold')
        ax.set_ylabel('Model Family', fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved completeness matrix: {save_path}")

    def plot_temporal_timeline(self, metadata: Dict, save_path: str) -> None:
        """
        Plot temporal coverage timeline.

        Args:
            metadata: Metadata from TechnicalReportCollector
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(14, 4))

        # Extract publication info
        timeline_data = []
        for key, info in metadata.items():
            if 'model_family' in info and 'timepoint' in info:
                timeline_data.append({
                    'family': info['model_family'],
                    'timepoint': info['timepoint'],
                    'date': info.get('downloaded_at', 'Unknown')
                })

        if not timeline_data:
            logger.warning("No metadata for temporal timeline")
            # Create simple placeholder
            ax.text(0.5, 0.5, 'No temporal data available',
                   ha='center', va='center', transform=ax.transAxes)
        else:
            # Group by family and timepoint
            families = sorted(set(d['family'] for d in timeline_data))
            timepoints = ['baseline', 'current']

            y_pos = 0
            for family in families:
                for i, tp in enumerate(timepoints):
                    x_pos = i
                    color = '#2E86AB' if tp == 'baseline' else '#A23B72'
                    ax.scatter(x_pos, y_pos, s=200, color=color, alpha=0.7,
                             edgecolors='black', linewidths=2)
                    ax.text(x_pos + 0.1, y_pos, f"{family}\n{tp}",
                           va='center', fontsize=10)
                y_pos += 1

            ax.set_xlim(-0.5, 1.5)
            ax.set_ylim(-0.5, y_pos - 0.5)
            ax.set_xticks([0, 1])
            ax.set_xticklabels(['Baseline Models', 'Current Models'])

        ax.set_title('Temporal Coverage Timeline',
                     fontsize=14, fontweight='bold')
        ax.set_yticks([])
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved temporal timeline: {save_path}")

    def generate_all_figures(self, output_dir: str, metadata: Dict = None) -> List[str]:
        """
        Generate all required figures.

        Args:
            output_dir: Directory to save figures
            metadata: Optional metadata for timeline

        Returns:
            List of generated file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        generated_files = []

        # 1. Gate metrics (MANDATORY)
        gate_path = output_path / "gate_metrics.png"
        self.plot_gate_metrics(str(gate_path))
        generated_files.append(str(gate_path))

        # 2. Granularity heatmap
        heatmap_path = output_path / "granularity_heatmap.png"
        self.plot_granularity_heatmap(str(heatmap_path))
        generated_files.append(str(heatmap_path))

        # 3. Completeness matrix
        matrix_path = output_path / "completeness_matrix.png"
        self.plot_completeness_matrix(str(matrix_path))
        generated_files.append(str(matrix_path))

        # 4. Temporal timeline
        timeline_path = output_path / "temporal_timeline.png"
        self.plot_temporal_timeline(metadata or {}, str(timeline_path))
        generated_files.append(str(timeline_path))

        logger.info(f"Generated {len(generated_files)} figures")
        return generated_files
