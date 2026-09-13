"""Visualization generation for h-c1 results."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path


class ComputeMatchedVisualizer:
    """Generate publication-quality figures for compute-matched comparison."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_style('whitegrid')

    def plot_primary_comparison(self, results: dict, output_path: str = None):
        """Bar plot comparing baselines."""
        if output_path is None:
            output_path = self.output_dir / "primary_comparison.png"

        baselines = ['IterativeFeedback', 'SelfConsistency', 'Hybrid']
        means = [
            results['mean_baseline1'],
            results['mean_baseline2'],
            results.get('mean_baseline3', 0)
        ]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(baselines, means, color=['#2ecc71', '#e74c3c', '#3498db'])

        ax.set_ylabel('Mean Discharge Rate (%)', fontsize=12)
        ax.set_title('Compute-Matched Baseline Comparison', fontsize=14, fontweight='bold')
        ax.axhline(y=results['mean_baseline2'] + 10, color='black', linestyle='--',
                   label='10pp threshold', linewidth=1.5)

        # Add gap annotations
        gap = means[0] - means[1]
        ax.text(0.5, max(means) + 2, f'Gap: {gap:.1f}pp',
                ha='center', fontsize=11, fontweight='bold')

        ax.legend()
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_gap_distribution(self, gaps: list, output_path: str = None):
        """Histogram of per-program gaps."""
        if output_path is None:
            output_path = self.output_dir / "gap_distribution.png"

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(gaps, bins=20, color='#3498db', edgecolor='black', alpha=0.7)

        mean_gap = np.mean(gaps)
        ax.axvline(x=mean_gap, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_gap:.1f}pp')
        ax.axvline(x=10, color='green', linestyle='--', linewidth=2, label='10pp threshold')

        ax.set_xlabel('Gap (IterativeFeedback - SelfConsistency) in pp', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Distribution of Per-Program Gaps', fontsize=14, fontweight='bold')
        ax.legend()

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_compute_budget_scatter(self, program_results: list, output_path: str = None):
        """Scatter plot: tokens vs discharge rate."""
        if output_path is None:
            output_path = self.output_dir / "compute_budget_scatter.png"

        b1_tokens = [r['baseline1']['compute_budget']['total_tokens'] for r in program_results]
        b1_rates = [r['baseline1']['discharge_rate'] for r in program_results]
        b2_tokens = [r['baseline2']['compute_budget']['total_tokens'] for r in program_results]
        b2_rates = [r['baseline2']['discharge_rate'] for r in program_results]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(b1_tokens, b1_rates, label='IterativeFeedback', color='#2ecc71', alpha=0.6, s=100)
        ax.scatter(b2_tokens, b2_rates, label='SelfConsistency', color='#e74c3c', alpha=0.6, s=100)

        ax.set_xlabel('Total Tokens Used', fontsize=12)
        ax.set_ylabel('Discharge Rate (%)', fontsize=12)
        ax.set_title('Compute Budget vs Performance', fontsize=14, fontweight='bold')
        ax.legend()

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()

    def generate_all_figures(self, results: dict, program_results: list):
        """Generate all publication figures."""
        # Primary comparison
        self.plot_primary_comparison(results)

        # Gap distribution
        gaps = [r['baseline1']['discharge_rate'] - r['baseline2']['discharge_rate']
                for r in program_results]
        self.plot_gap_distribution(gaps)

        # Compute scatter
        self.plot_compute_budget_scatter(program_results)

        print(f"All figures saved to {self.output_dir}")
