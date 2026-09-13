"""
Visualization Pipeline for Oracle Gap Analysis
Based on: 03_architecture.md - Module 5: VisualizationModule
Based on: 03_logic.md - A-6: Visualization Pipeline
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300


class ExperimentVisualizer:
    """Generate visualization for oracle gap analysis."""

    def __init__(self, output_dir: str):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Color scheme for ranks
        self.rank_colors = {
            4: "#1f77b4",
            8: "#ff7f0e",
            16: "#2ca02c",
            32: "#d62728"
        }

    def plot_gate_metrics(self, target_gap: float, actual_gap: float):
        """
        Plot gate metrics comparison (MANDATORY figure).

        Args:
            target_gap: Target oracle gap (10%)
            actual_gap: Actual measured oracle gap
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Bar chart
        categories = ['Target', 'Actual']
        values = [target_gap, actual_gap]
        colors = ['#cccccc', '#2ca02c' if actual_gap >= target_gap else '#d62728']

        bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.2f}%',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')

        # Add threshold line
        ax.axhline(y=target_gap, color='red', linestyle='--', linewidth=2, label='MUST_WORK Gate')

        ax.set_ylabel('Oracle Gap (%)', fontsize=12, fontweight='bold')
        ax.set_title('Gate Metrics: Oracle Gap Validation', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        # Add pass/fail text
        status = "PASS" if actual_gap >= target_gap else "FAIL"
        status_color = "green" if actual_gap >= target_gap else "red"
        ax.text(0.95, 0.95, f'Gate: {status}',
               transform=ax.transAxes,
               fontsize=16, fontweight='bold',
               color=status_color,
               ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        output_path = self.output_dir / "gate_metrics.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Gate metrics plot saved: {output_path}")

    def plot_pareto_fronts(self, results: Dict, oracle_selections: Dict):
        """
        Plot per-task Pareto fronts.

        Args:
            results: {task: {rank: {accuracy, flops, ...}}}
            oracle_selections: {task: best_rank}
        """
        tasks = list(results.keys())
        n_tasks = len(tasks)

        # Create grid
        n_cols = 4
        n_rows = (n_tasks + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, n_rows * 3))
        axes = axes.flatten() if n_tasks > 1 else [axes]

        for idx, task_name in enumerate(tasks):
            ax = axes[idx]
            task_results = results[task_name]
            oracle_rank = oracle_selections[task_name]

            # Plot points
            for rank, metrics in task_results.items():
                acc = metrics['accuracy']
                flops = metrics['flops']
                color = self.rank_colors.get(rank, 'gray')
                marker = '*' if rank == oracle_rank else 'o'
                size = 200 if rank == oracle_rank else 100

                ax.scatter(flops, acc, color=color, marker=marker, s=size,
                          label=f'r={rank}' + (' (Oracle)' if rank == oracle_rank else ''),
                          alpha=0.7, edgecolors='black', linewidth=1.5)

            ax.set_xlabel('FLOPs', fontsize=9)
            ax.set_ylabel('Accuracy', fontsize=9)
            ax.set_title(task_name, fontsize=10, fontweight='bold')
            ax.set_xscale('log')
            ax.legend(fontsize=7, loc='best')
            ax.grid(True, alpha=0.3)

        # Hide unused subplots
        for idx in range(n_tasks, len(axes)):
            axes[idx].axis('off')

        plt.tight_layout()
        output_path = self.output_dir / "pareto_fronts.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Pareto fronts plot saved: {output_path}")

    def plot_oracle_vs_fixed(self, oracle_hv: float, fixed_hvs: Dict[int, float],
                             oracle_gap_pct: float):
        """
        Plot bar chart comparing oracle vs fixed-rank baselines.

        Args:
            oracle_hv: Oracle hypervolume
            fixed_hvs: {rank: hypervolume}
            oracle_gap_pct: Oracle gap percentage
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Prepare data
        categories = ['Oracle'] + [f'Rank {r}' for r in sorted(fixed_hvs.keys())]
        values = [oracle_hv] + [fixed_hvs[r] for r in sorted(fixed_hvs.keys())]
        colors = ['#2ca02c'] + ['#cccccc'] * len(fixed_hvs)

        bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.4f}',
                   ha='center', va='bottom', fontsize=10)

        # Add oracle gap annotation
        ax.text(0.95, 0.95, f'Oracle Gap: {oracle_gap_pct:.2f}%',
               transform=ax.transAxes,
               fontsize=14, fontweight='bold',
               ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))

        ax.set_ylabel('Hypervolume', fontsize=12, fontweight='bold')
        ax.set_title('Oracle vs Fixed-Rank Comparison', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_path = self.output_dir / "oracle_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Oracle comparison plot saved: {output_path}")

    def plot_rank_selection_heatmap(self, results: Dict, oracle_selections: Dict):
        """
        Plot heatmap of accuracy across tasks and ranks.

        Args:
            results: {task: {rank: {accuracy, ...}}}
            oracle_selections: {task: best_rank}
        """
        tasks = list(results.keys())
        ranks = sorted(list(next(iter(results.values())).keys()))

        # Create accuracy matrix
        acc_matrix = np.zeros((len(tasks), len(ranks)))

        for i, task in enumerate(tasks):
            for j, rank in enumerate(ranks):
                if rank in results[task]:
                    acc_matrix[i, j] = results[task][rank]['accuracy']

        # Create figure
        fig, ax = plt.subplots(figsize=(10, max(8, len(tasks) * 0.4)))

        # Heatmap
        im = ax.imshow(acc_matrix, cmap='YlOrRd', aspect='auto')

        # Set ticks
        ax.set_xticks(np.arange(len(ranks)))
        ax.set_yticks(np.arange(len(tasks)))
        ax.set_xticklabels([f'r={r}' for r in ranks])
        ax.set_yticklabels(tasks)

        # Add value annotations
        for i in range(len(tasks)):
            for j in range(len(ranks)):
                rank = ranks[j]
                is_oracle = (rank == oracle_selections[tasks[i]])
                text = ax.text(j, i, f'{acc_matrix[i, j]:.3f}',
                             ha="center", va="center", color="black",
                             fontweight='bold' if is_oracle else 'normal',
                             fontsize=8)

                # Mark oracle selections
                if is_oracle:
                    ax.add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1,
                                              fill=False, edgecolor='blue',
                                              linewidth=3))

        ax.set_xlabel('LoRA Rank', fontsize=12, fontweight='bold')
        ax.set_ylabel('Task', fontsize=12, fontweight='bold')
        ax.set_title('Rank Selection Heatmap (Blue box = Oracle)', fontsize=14, fontweight='bold')

        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Accuracy', fontsize=10)

        plt.tight_layout()
        output_path = self.output_dir / "rank_heatmap.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Rank heatmap plot saved: {output_path}")

    def plot_efficiency_tradeoff(self, results: Dict):
        """
        Plot 2D scatter of all configurations (efficiency-performance trade-off).

        Args:
            results: {task: {rank: {accuracy, flops, ...}}}
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        # Collect all points
        for task_name, task_results in results.items():
            for rank, metrics in task_results.items():
                acc = metrics['accuracy']
                flops = metrics['flops']
                color = self.rank_colors.get(rank, 'gray')

                ax.scatter(flops, acc, color=color, s=100, alpha=0.6,
                          edgecolors='black', linewidth=0.5)

        # Create legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                     markerfacecolor=self.rank_colors[r],
                                     markersize=10, label=f'Rank {r}')
                          for r in sorted(self.rank_colors.keys())]
        ax.legend(handles=legend_elements, fontsize=12, loc='best')

        ax.set_xlabel('FLOPs (log scale)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
        ax.set_title('Efficiency-Performance Trade-off (All Configurations)',
                    fontsize=14, fontweight='bold')
        ax.set_xscale('log')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / "efficiency_tradeoff.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Efficiency trade-off plot saved: {output_path}")

    def save_all_figures(self, results: Dict, oracle_results: Dict,
                        target_gap: float = 10.0):
        """
        Generate all required figures.

        Args:
            results: Full experiment results
            oracle_results: Oracle gap calculation results
            target_gap: Target oracle gap percentage
        """
        print("\n" + "="*80)
        print("GENERATING FIGURES")
        print("="*80)

        # 1. Gate metrics (MANDATORY)
        self.plot_gate_metrics(target_gap, oracle_results['oracle_gap_pct'])

        # 2. Pareto fronts
        self.plot_pareto_fronts(results, oracle_results['oracle_selections'])

        # 3. Oracle vs fixed
        self.plot_oracle_vs_fixed(oracle_results['oracle_hv'],
                                  oracle_results['fixed_hvs'],
                                  oracle_results['oracle_gap_pct'])

        # 4. Rank heatmap
        self.plot_rank_selection_heatmap(results, oracle_results['oracle_selections'])

        # 5. Efficiency trade-off
        self.plot_efficiency_tradeoff(results)

        print("="*80)
        print(f"✓ ALL FIGURES SAVED TO: {self.output_dir}")
        print("="*80)
