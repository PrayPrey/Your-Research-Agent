"""Generate required and optional figures for validation report."""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from typing import Dict, List
import numpy as np


class ExperimentVisualizer:
    """Generate visualizations for h-m4 experiment."""

    def __init__(self, output_dir: Path):
        """Initialize visualizer."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        plt.style.use('seaborn-v0_8-darkgrid')

    def generate_gate_metrics_chart(
        self,
        ci_only_median: float,
        ci_contracts_median: float,
        threshold: float = -5.0
    ) -> None:
        """Generate gate metrics comparison (required figure)."""
        fig, ax = plt.subplots(figsize=(10, 6))

        arms = ['CI-Only', 'CI+Contracts']
        medians = [ci_only_median, ci_contracts_median]
        colors = ['#FF6B6B', '#4ECDC4']

        bars = ax.bar(arms, medians, color=colors, alpha=0.7)

        # Add threshold line
        reduction = ci_only_median - ci_contracts_median
        ax.axhline(y=ci_only_median + threshold, color='red', linestyle='--',
                   linewidth=2, label=f'Target: ≥{abs(threshold)}h reduction')

        ax.set_ylabel('Median TTFF (hours)', fontsize=12)
        ax.set_title('Time-to-First-Failure: CI-Only vs. CI+Contracts', fontsize=14, fontweight='bold')
        ax.legend()

        # Add value labels on bars
        for bar, median in zip(bars, medians):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{median:.2f}h',
                   ha='center', va='bottom', fontsize=11)

        # Add reduction annotation
        ax.text(0.5, max(medians) * 0.9,
               f'Reduction: {reduction:.2f}h',
               ha='center', fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        save_path = self.output_dir / 'gate_metrics.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved gate metrics chart to {save_path}")

    def generate_stage_distribution_chart(self, stage_data: Dict[str, Dict[str, float]]) -> None:
        """Generate stage-of-failure distribution (stacked bar chart)."""
        fig, ax = plt.subplots(figsize=(10, 6))

        arms = list(stage_data.keys())
        environment = [stage_data[arm].get('environment', 0) for arm in arms]
        training = [stage_data[arm].get('training', 0) for arm in arms]
        unknown = [stage_data[arm].get('unknown', 0) for arm in arms]

        x = np.arange(len(arms))
        width = 0.6

        # Create stacked bars
        p1 = ax.bar(x, environment, width, label='Environment', color='#4ECDC4')
        p2 = ax.bar(x, training, width, bottom=environment, label='Training', color='#FF6B6B')
        p3 = ax.bar(x, unknown, width, bottom=np.array(environment) + np.array(training),
                    label='Unknown', color='#95A5A6')

        ax.set_ylabel('Proportion (%)', fontsize=12)
        ax.set_title('Stage-of-First-Failure Distribution', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(arms)
        ax.legend()

        plt.tight_layout()
        save_path = self.output_dir / 'stage_distribution.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved stage distribution chart to {save_path}")

    def generate_ttff_distribution_chart(
        self,
        ci_only: List[float],
        ci_contracts: List[float]
    ) -> None:
        """Generate TTFF distribution (box plot or violin plot)."""
        fig, ax = plt.subplots(figsize=(10, 6))

        data = [ci_only, ci_contracts]
        labels = ['CI-Only', 'CI+Contracts']

        bp = ax.boxplot(data, labels=labels, patch_artist=True)

        # Color the boxes
        colors = ['#FF6B6B', '#4ECDC4']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel('TTFF (hours)', fontsize=12)
        ax.set_title('Time-to-First-Failure Distribution', fontsize=14, fontweight='bold')

        plt.tight_layout()
        save_path = self.output_dir / 'ttff_distribution.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved TTFF distribution chart to {save_path}")
