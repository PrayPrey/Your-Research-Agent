"""Ablation Visualization Module - Generate publication-quality figures"""

from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from dataclasses import asdict

from .ablation_experiment import AblationResults, ConditionResults
from .statistical_analyzer import RegressionResult, GapTest, MonotonicTest
from .feedback_ablator import FeedbackCondition


class AblationVisualizer:
    """Generate visualizations for ablation study"""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.color_map = {
            FeedbackCondition.FULL_STRUCTURED.value: "#2ecc71",
            FeedbackCondition.OBLIGATION_SLICE.value: "#3498db",
            FeedbackCondition.TAG_ONLY.value: "#f39c12",
            FeedbackCondition.RAW_ERROR.value: "#e74c3c"
        }

        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 300

    def plot_monotonic_ordering(
        self,
        condition_results: Dict[str, ConditionResults],
        output_path: str
    ):
        """Line plot: feedback condition vs. mean discharge rate with CI"""
        conditions_ordered = [
            FeedbackCondition.RAW_ERROR.value,
            FeedbackCondition.TAG_ONLY.value,
            FeedbackCondition.OBLIGATION_SLICE.value,
            FeedbackCondition.FULL_STRUCTURED.value
        ]

        means = [condition_results[c].mean_rate for c in conditions_ordered]
        stds = [condition_results[c].std_rate for c in conditions_ordered]
        n = len(condition_results[conditions_ordered[0]].trials)
        ci = [1.96 * s / np.sqrt(n) for s in stds]

        fig, ax = plt.subplots(figsize=(10, 6))
        x = range(len(conditions_ordered))

        ax.errorbar(x, means, yerr=ci, marker='o', linewidth=2, markersize=8,
                   capsize=5, label='Mean ± 95% CI')

        for i, trial_list in enumerate([condition_results[c].trials for c in conditions_ordered]):
            rates = [t.discharge_rate for t in trial_list]
            jitter = np.random.normal(0, 0.05, len(rates))
            ax.scatter([i] * len(rates) + jitter, rates, alpha=0.3, s=30)

        ax.set_xticks(x)
        ax.set_xticklabels([c.replace('_', '\n') for c in conditions_ordered])
        ax.set_ylabel('Proof Discharge Rate (%)')
        ax.set_xlabel('Feedback Condition')
        ax.set_title('Information Gradient: Discharge Rate vs. Feedback Richness')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / output_path, bbox_inches='tight')
        plt.close()

    def plot_per_program_heatmap(
        self,
        raw_trials: List,
        output_path: str
    ):
        """Heatmap: programs × conditions with discharge rate color coding"""
        programs = sorted(set(t.program_id for t in raw_trials))
        conditions = [
            FeedbackCondition.RAW_ERROR.value,
            FeedbackCondition.TAG_ONLY.value,
            FeedbackCondition.OBLIGATION_SLICE.value,
            FeedbackCondition.FULL_STRUCTURED.value
        ]

        matrix = np.zeros((len(programs), len(conditions)))

        for trial in raw_trials:
            prog_idx = programs.index(trial.program_id)
            cond_idx = conditions.index(trial.condition)
            matrix[prog_idx, cond_idx] = trial.discharge_rate

        fig, ax = plt.subplots(figsize=(8, max(6, len(programs) * 0.3)))
        sns.heatmap(matrix, annot=True, fmt='.1f', cmap='RdYlGn',
                   xticklabels=[c.replace('_', '\n') for c in conditions],
                   yticklabels=programs, cbar_kws={'label': 'Discharge Rate (%)'},
                   ax=ax, vmin=0, vmax=100)

        ax.set_title('Per-Program Performance Across Conditions')
        ax.set_xlabel('Feedback Condition')
        ax.set_ylabel('Program ID')

        plt.tight_layout()
        plt.savefig(self.output_dir / output_path, bbox_inches='tight')
        plt.close()

    def plot_regression(
        self,
        ablation_results: AblationResults,
        regression_result: RegressionResult,
        output_path: str
    ):
        """Scatter: feedback richness vs. discharge rate with fitted line"""
        encoding = {
            FeedbackCondition.RAW_ERROR.value: 1,
            FeedbackCondition.TAG_ONLY.value: 2,
            FeedbackCondition.OBLIGATION_SLICE.value: 3,
            FeedbackCondition.FULL_STRUCTURED.value: 4
        }

        x = [encoding[t.condition] for t in ablation_results.raw_trials]
        y = [t.discharge_rate for t in ablation_results.raw_trials]

        fig, ax = plt.subplots(figsize=(10, 6))

        for condition in encoding.keys():
            trials_cond = [t for t in ablation_results.raw_trials if t.condition == condition]
            x_cond = [encoding[condition]] * len(trials_cond)
            y_cond = [t.discharge_rate for t in trials_cond]
            ax.scatter(x_cond, y_cond, label=condition, alpha=0.6,
                      color=self.color_map[condition], s=50)

        x_line = np.array([1, 2, 3, 4])
        y_line = regression_result.coefficient * x_line + (np.mean(y) - regression_result.coefficient * np.mean(x))
        ax.plot(x_line, y_line, 'k--', linewidth=2, label='Regression Line')

        ax.set_xticks([1, 2, 3, 4])
        ax.set_xticklabels(['Raw', 'Tag', 'Obligation', 'Full'])
        ax.set_xlabel('Feedback Richness (Ordinal)')
        ax.set_ylabel('Proof Discharge Rate (%)')
        ax.set_title(f'Regression Analysis\n'
                    f'β={regression_result.coefficient:.2f}, '
                    f'p={regression_result.p_value:.4f}, '
                    f'R²={regression_result.r_squared:.3f}')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / output_path, bbox_inches='tight')
        plt.close()

    def plot_gate_metrics_comparison(
        self,
        condition_results: Dict[str, ConditionResults],
        gap_test: GapTest,
        output_path: str
    ):
        """Required gate plot: target vs actual metrics"""
        conditions_ordered = [
            FeedbackCondition.RAW_ERROR.value,
            FeedbackCondition.TAG_ONLY.value,
            FeedbackCondition.OBLIGATION_SLICE.value,
            FeedbackCondition.FULL_STRUCTURED.value
        ]

        means = [condition_results[c].mean_rate for c in conditions_ordered]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        x = range(len(conditions_ordered))
        ax1.bar(x, means, color=[self.color_map[c] for c in conditions_ordered])
        ax1.set_xticks(x)
        ax1.set_xticklabels([c.replace('_', '\n') for c in conditions_ordered])
        ax1.set_ylabel('Mean Discharge Rate (%)')
        ax1.set_title('Mean Performance by Condition')
        ax1.grid(True, alpha=0.3, axis='y')

        gap_names = list(gap_test.gaps.keys())
        gap_values = list(gap_test.gaps.values())
        colors = ['green' if g >= gap_test.threshold else 'red' for g in gap_values]

        ax2.bar(range(len(gap_names)), gap_values, color=colors)
        ax2.axhline(y=gap_test.threshold, color='k', linestyle='--', label=f'Target: {gap_test.threshold}pp')
        ax2.set_xticks(range(len(gap_names)))
        ax2.set_xticklabels([name.split(' - ')[0].replace('_', '\n') + '\nvs\n' + name.split(' - ')[1].replace('_', '\n')
                            for name in gap_names], fontsize=8)
        ax2.set_ylabel('Gap (percentage points)')
        ax2.set_title('Adjacent Condition Gaps')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(self.output_dir / output_path, bbox_inches='tight')
        plt.close()

    def generate_all_figures(
        self,
        ablation_results: AblationResults,
        stats: Dict
    ):
        """Generate all visualization figures"""
        print("\nGenerating visualizations...")

        self.plot_gate_metrics_comparison(
            ablation_results.results_by_condition,
            stats['gap_test'],
            'gate_metrics_comparison.png'
        )
        print("  ✓ Gate metrics comparison")

        self.plot_monotonic_ordering(
            ablation_results.results_by_condition,
            'monotonic_ordering.png'
        )
        print("  ✓ Monotonic ordering plot")

        self.plot_per_program_heatmap(
            ablation_results.raw_trials,
            'per_program_heatmap.png'
        )
        print("  ✓ Per-program heatmap")

        self.plot_regression(
            ablation_results,
            stats['regression'],
            'regression_plot.png'
        )
        print("  ✓ Regression plot")

        print(f"\nAll figures saved to {self.output_dir}")
