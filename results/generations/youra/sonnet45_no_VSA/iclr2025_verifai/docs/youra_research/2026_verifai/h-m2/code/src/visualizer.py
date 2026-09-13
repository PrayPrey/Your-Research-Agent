"""Visualization module for comparison experiment results."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import List

import comparison_experiment

ComparisonMetrics = comparison_experiment.ComparisonMetrics
ExperimentResults = comparison_experiment.ExperimentResults


class ComparisonVisualizer:
    """Generate comparison plots for Staged vs Complete strategies."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_style("whitegrid")

    def generate_all_plots(self, results: ExperimentResults):
        """Generate all required visualization plots."""
        metrics = results.comparison_metrics

        print("\nGenerating visualization plots...")

        # 1. Gate Metrics Comparison (Mandatory)
        self.plot_gate_metrics(metrics)

        # 2. Convergence Comparison
        self.plot_convergence_comparison(results)

        # 3. Per-Stage Improvement
        self.plot_per_stage_improvement(results)

        # 4. Iteration Distribution
        self.plot_iteration_distribution(results)

        # 5. Backtracking Analysis
        self.plot_backtracking_analysis(results)

        # 6. Statistical Test
        self.plot_statistical_test(results)

        print(f"All plots saved to {self.output_dir}")

    def plot_gate_metrics(self, metrics: ComparisonMetrics):
        """Bar chart: Target vs Actual for both strategies."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Discharge rate comparison
        strategies = ['Staged', 'Complete']
        actual_discharge = [metrics.staged_mean_discharge, metrics.complete_mean_discharge]
        target_discharge = [55.0, 50.0]  # Complete + 5pp for Staged

        x = np.arange(len(strategies))
        width = 0.35

        ax1.bar(x - width/2, target_discharge, width, label='Target', alpha=0.7)
        ax1.bar(x + width/2, actual_discharge, width, label='Actual', alpha=0.7)
        ax1.set_ylabel('Proof Discharge Rate (%)')
        ax1.set_title('Discharge Rate: Target vs Actual')
        ax1.set_xticks(x)
        ax1.set_xticklabels(strategies)
        ax1.legend()
        ax1.axhline(y=50, color='r', linestyle='--', alpha=0.3, label='Baseline Target')

        # Iteration ratio comparison
        actual_ratio = [metrics.iteration_reduction_ratio, 1.0]
        target_ratio = [0.7, 1.0]

        ax2.bar(x - width/2, target_ratio, width, label='Target', alpha=0.7)
        ax2.bar(x + width/2, actual_ratio, width, label='Actual', alpha=0.7)
        ax2.set_ylabel('Iteration Ratio (normalized to Complete)')
        ax2.set_title('Iteration Convergence: Target vs Actual')
        ax2.set_xticks(x)
        ax2.set_xticklabels(strategies)
        ax2.legend()
        ax2.axhline(y=0.7, color='r', linestyle='--', alpha=0.3, label='Target (≤70%)')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'gate_metrics_comparison.png', dpi=300)
        plt.close()

    def plot_convergence_comparison(self, results: ExperimentResults):
        """Line plot: Iteration vs Discharge rate for both strategies."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Average discharge history over all programs
        max_iters = max(
            max(r.total_iterations for r in results.staged_results),
            max(r.total_iterations for r in results.complete_results)
        )

        # Staged: aggregate per-stage discharge rates
        staged_avg = []
        for i in range(4):  # 4 stages
            stage_rates = [
                list(r.stage_history.values())[i].discharge_rate
                for r in results.staged_results
                if len(r.stage_history) > i
            ]
            if stage_rates:
                staged_avg.append(np.mean(stage_rates))

        # Complete: aggregate iteration discharge rates
        complete_avg = []
        for i in range(max_iters):
            iter_rates = [
                r.discharge_history[i]
                for r in results.complete_results
                if len(r.discharge_history) > i
            ]
            if iter_rates:
                complete_avg.append(np.mean(iter_rates))

        # Plot
        ax.plot(range(1, len(staged_avg) + 1), staged_avg, 'o-', label='Staged', linewidth=2)
        ax.plot(range(1, len(complete_avg) + 1), complete_avg, 's-', label='Complete', linewidth=2)

        # Mark stage boundaries for Staged
        for i in range(1, 4):
            ax.axvline(x=i+0.5, color='gray', linestyle='--', alpha=0.3)

        ax.set_xlabel('Iteration / Stage')
        ax.set_ylabel('Proof Discharge Rate (%)')
        ax.set_title('Convergence Comparison: Staged vs Complete')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'convergence_comparison.png', dpi=300)
        plt.close()

    def plot_per_stage_improvement(self, results: ExperimentResults):
        """Bar chart: Cumulative discharge rate per stage (Staged only)."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Average discharge rate per stage
        stages = ['Types', 'Pre', 'Post', 'Inv']
        stage_rates = []

        for i in range(4):
            rates = [
                list(r.stage_history.values())[i].discharge_rate
                for r in results.staged_results
                if len(r.stage_history) > i
            ]
            stage_rates.append(np.mean(rates) if rates else 0.0)

        ax.bar(stages, stage_rates, alpha=0.7)
        ax.set_ylabel('Cumulative Discharge Rate (%)')
        ax.set_title('Per-Stage Improvement (Staged Strategy)')
        ax.grid(True, axis='y', alpha=0.3)

        # Annotate improvement deltas
        for i in range(1, len(stage_rates)):
            delta = stage_rates[i] - stage_rates[i-1]
            ax.text(i, stage_rates[i] + 1, f'+{delta:.1f}%', ha='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'per_stage_improvement.png', dpi=300)
        plt.close()

    def plot_iteration_distribution(self, results: ExperimentResults):
        """Box plot: Iteration counts for both strategies."""
        fig, ax = plt.subplots(figsize=(8, 6))

        staged_iters = [r.total_iterations for r in results.staged_results]
        complete_iters = [r.total_iterations for r in results.complete_results]

        ax.boxplot([staged_iters, complete_iters], labels=['Staged', 'Complete'])
        ax.set_ylabel('Iterations to Convergence')
        ax.set_title('Iteration Distribution Comparison')
        ax.grid(True, axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'iteration_distribution.png', dpi=300)
        plt.close()

    def plot_backtracking_analysis(self, results: ExperimentResults):
        """Histogram: Backtracking events (Staged only)."""
        fig, ax = plt.subplots(figsize=(10, 6))

        backtracking_counts = [r.backtracking_events for r in results.staged_results]

        ax.hist(backtracking_counts, bins=range(max(backtracking_counts) + 2), alpha=0.7, edgecolor='black')
        ax.set_xlabel('Backtracking Events per Program')
        ax.set_ylabel('Frequency (Program Count)')
        ax.set_title('Backtracking Analysis (Staged Strategy)')

        mean_backtrack = np.mean(backtracking_counts)
        ax.axvline(x=mean_backtrack, color='r', linestyle='--', label=f'Mean: {mean_backtrack:.2f}')
        ax.legend()
        ax.grid(True, axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'backtracking_analysis.png', dpi=300)
        plt.close()

    def plot_statistical_test(self, results: ExperimentResults):
        """Paired difference plot with p-value annotation."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Compute paired differences
        staged_rates = [list(r.stage_history.values())[-1].discharge_rate for r in results.staged_results]
        complete_rates = [r.discharge_history[-1] if r.discharge_history else 0.0 for r in results.complete_results]
        differences = np.array(staged_rates) - np.array(complete_rates)

        # Plot differences
        ax.scatter(range(len(differences)), differences, alpha=0.6)
        ax.axhline(y=0, color='r', linestyle='--', label='No difference')
        ax.set_xlabel('Program Index')
        ax.set_ylabel('Discharge Rate Difference (Staged - Complete) [%]')
        ax.set_title('Paired Difference Analysis')

        # Annotate statistics
        metrics = results.comparison_metrics
        stats_text = f'p-value: {metrics.p_value:.4f}\nEffect size (Cohen\'s d): {metrics.effect_size:.3f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'statistical_test.png', dpi=300)
        plt.close()
