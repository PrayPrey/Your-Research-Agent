"""Visualization for experiment results."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List
import pandas as pd

from .metrics import MetricsTracker


class Visualizer:
    """Generate required plots for experiment."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 300

    def plot_gate_metrics(self, metrics_tracker: MetricsTracker, target: float = 50.0):
        """Gate metrics comparison bar chart."""
        agg = metrics_tracker.compute_aggregate_metrics()

        mean_rate = agg.get('mean_final_discharge_rate', 0)

        fig, ax = plt.subplots(figsize=(8, 6))

        categories = ['Target', 'Actual Mean']
        values = [target, mean_rate]
        colors = ['lightcoral', 'lightgreen' if mean_rate >= target else 'lightyellow']

        ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)
        ax.axhline(y=target, color='red', linestyle='--', linewidth=2, label=f'Gate Threshold ({target}%)')
        ax.set_ylabel('Proof Discharge Rate (%)', fontsize=12)
        ax.set_title('H-E1: Gate Metrics Comparison', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 110)
        ax.legend()

        plt.tight_layout()
        plt.savefig(self.output_dir / 'gate_metrics_comparison.png')
        plt.close()

    def plot_iteration_progress(self, metrics_tracker: MetricsTracker):
        """Iteration progress line chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Load iteration logs
        log_dir = metrics_tracker.output_dir / "iteration_logs"
        if not log_dir.exists():
            print("Warning: No iteration logs found")
            return

        for log_file in log_dir.glob("*.json"):
            import json
            with open(log_file) as f:
                data = json.load(f)

            iterations = [it['iteration'] for it in data['iterations']]
            rates = [it['discharge_rate'] for it in data['iterations']]

            ax.plot(iterations, rates, marker='o', label=data['program_id'], alpha=0.7)

        ax.set_xlabel('Iteration', fontsize=12)
        ax.set_ylabel('Proof Discharge Rate (%)', fontsize=12)
        ax.set_title('H-E1: Iteration Progress per Program', fontsize=14, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'iteration_progress.png')
        plt.close()

    def plot_feedback_heatmap(self, metrics_tracker: MetricsTracker):
        """Feedback dimension utilization heatmap."""
        programs = [e.program_id for e in metrics_tracker.experiments]
        dimensions = ['Witness', 'Structure', 'Dependency']

        # Build matrix
        matrix = []
        for exp in metrics_tracker.experiments:
            row = [
                1 if 'witness' in exp.feedback_dimensions_used else 0,
                1 if 'structure' in exp.feedback_dimensions_used else 0,
                1 if 'dependency' in exp.feedback_dimensions_used else 0
            ]
            matrix.append(row)

        df = pd.DataFrame(matrix, index=programs, columns=dimensions)

        fig, ax = plt.subplots(figsize=(8, len(programs) * 0.5 + 2))
        sns.heatmap(df, annot=True, fmt='d', cmap='YlGnBu', cbar_kws={'label': 'Used'}, ax=ax)
        ax.set_title('H-E1: Feedback Dimension Utilization', fontsize=14, fontweight='bold')
        ax.set_xlabel('Feedback Dimension', fontsize=12)
        ax.set_ylabel('Program ID', fontsize=12)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'feedback_heatmap.png')
        plt.close()

    def plot_convergence_histogram(self, metrics_tracker: MetricsTracker):
        """Convergence histogram."""
        iterations = [e.iterations_to_convergence for e in metrics_tracker.experiments]

        fig, ax = plt.subplots(figsize=(8, 6))

        ax.hist(iterations, bins=range(1, max(iterations) + 2), edgecolor='black', color='skyblue', alpha=0.7)
        ax.set_xlabel('Iterations to Convergence', fontsize=12)
        ax.set_ylabel('Number of Programs', fontsize=12)
        ax.set_title('H-E1: Convergence Distribution', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'convergence_histogram.png')
        plt.close()

    def generate_all_plots(self, metrics_tracker: MetricsTracker, target: float = 50.0):
        """Generate all required plots."""
        print("Generating visualizations...")
        self.plot_gate_metrics(metrics_tracker, target)
        self.plot_iteration_progress(metrics_tracker)
        self.plot_feedback_heatmap(metrics_tracker)
        self.plot_convergence_histogram(metrics_tracker)
        print(f"Visualizations saved to {self.output_dir}")
