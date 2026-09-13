"""
Visualization Suite for H-M3 Fisher z-Test Results
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, Tuple


class ComparisonVisualizer:
    """Generate publication-ready visualizations."""

    def __init__(self, output_dir: str):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 300

    def plot_gate_metrics_comparison(
        self,
        fisher_result: Dict,
        gate_result: Dict,
        target_p: float = 0.05
    ) -> None:
        """
        MANDATORY: Bar chart comparing observed vs target metrics.

        Args:
            fisher_result: Fisher test results
            gate_result: Gate evaluation results
            target_p: Target p-value threshold
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Subplot 1: p-value comparison
        metrics = ['Observed\np-value', 'Target\nThreshold']
        values = [fisher_result['p_value'], target_p]
        colors = ['steelblue' if fisher_result['p_value'] < target_p else 'coral', 'red']

        ax1.bar(metrics, values, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('p-value', fontsize=12)
        ax1.set_title('Primary Criterion: Fisher z-Test Significance', fontsize=14, fontweight='bold')
        ax1.axhline(target_p, color='red', linestyle='--', linewidth=2, label=f'Threshold: {target_p}')
        ax1.legend()
        ax1.set_ylim(0, max(fisher_result['p_value'], target_p) * 1.2)

        # Add value labels
        for i, v in enumerate(values):
            ax1.text(i, v + 0.01, f'{v:.4f}', ha='center', va='bottom', fontweight='bold')

        # Subplot 2: Delta r comparison
        delta_r_threshold = gate_result['criteria']['delta_r_threshold']
        metrics2 = ['Observed\nΔr', 'Target\nThreshold']
        values2 = [gate_result['delta_r'], delta_r_threshold]
        colors2 = ['steelblue' if gate_result['delta_r'] >= delta_r_threshold else 'coral', 'red']

        ax2.bar(metrics2, values2, color=colors2, alpha=0.7, edgecolor='black')
        ax2.set_ylabel('Correlation Difference |Δr|', fontsize=12)
        ax2.set_title('Secondary Criterion: Effect Magnitude', fontsize=14, fontweight='bold')
        ax2.axhline(delta_r_threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold: {delta_r_threshold}')
        ax2.legend()
        ax2.set_ylim(0, max(gate_result['delta_r'], delta_r_threshold) * 1.2)

        # Add value labels
        for i, v in enumerate(values2):
            ax2.text(i, v + 0.01, f'{v:.4f}', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        output_path = self.output_dir / 'gate_metrics_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_path}")

    def plot_forest_plot(
        self,
        r_factual: float,
        r_misinfo: float,
        ci_factual: Tuple[float, float],
        ci_misinfo: Tuple[float, float],
        n_factual: int,
        n_misinfo: int,
        p_value: float
    ) -> None:
        """
        Forest plot with correlation coefficients and 95% CI error bars.

        Args:
            r_factual: Factual stratum correlation
            r_misinfo: Misinformation stratum correlation
            ci_factual: Factual CI (lower, upper)
            ci_misinfo: Misinformation CI (lower, upper)
            n_factual: Factual sample size
            n_misinfo: Misinformation sample size
            p_value: Fisher z-test p-value
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        strata = ['Factual', 'Misinformation']
        correlations = [r_factual, r_misinfo]
        ci_lower = [ci_factual[0], ci_misinfo[0]]
        ci_upper = [ci_factual[1], ci_misinfo[1]]
        sample_sizes = [n_factual, n_misinfo]

        y_positions = [0, 1]

        # Plot error bars
        for i, (y, r, ci_l, ci_u, n) in enumerate(zip(y_positions, correlations, ci_lower, ci_upper, sample_sizes)):
            color = 'steelblue' if i == 0 else 'coral'
            ax.errorbar(r, y, xerr=[[r - ci_l], [ci_u - r]], fmt='o', markersize=10,
                       color=color, ecolor=color, capsize=8, capthick=2, linewidth=2,
                       label=f'{strata[i]} (n={n})')

            # Add text annotation
            ax.text(r, y + 0.08, f'r={r:.4f}\n95% CI: [{ci_l:.3f}, {ci_u:.3f}]',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Vertical line at r=0
        ax.axvline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)

        # Labels and title
        ax.set_yticks(y_positions)
        ax.set_yticklabels(strata)
        ax.set_xlabel('Pearson Correlation Coefficient (r)', fontsize=12, fontweight='bold')
        ax.set_title(f'Stratified Correlation Comparison\n(Fisher z-test p={p_value:.4f})',
                    fontsize=14, fontweight='bold')
        ax.set_xlim(-1, 1)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / 'forest_plot.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_path}")

    def plot_effect_size(self, effect_size: Dict) -> None:
        """
        Bar chart showing Cohen's q effect size.

        Args:
            effect_size: Effect size results dict
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Thresholds
        thresholds = {
            'Small': 0.1,
            'Medium': 0.3,
            'Large': 0.5
        }

        # Plot observed Cohen's q
        cohens_q = effect_size['cohens_q']
        ax.barh(['Observed\nCohen\'s q'], [cohens_q], color='steelblue', alpha=0.7, edgecolor='black')

        # Add threshold lines
        for label, threshold in thresholds.items():
            ax.axvline(threshold, linestyle='--', linewidth=2, alpha=0.7, label=f'{label}: {threshold}')

        ax.set_xlabel('Cohen\'s q (Effect Size)', fontsize=12, fontweight='bold')
        ax.set_title(f'Effect Size Classification: {effect_size["magnitude"].upper()}',
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.set_xlim(0, max(cohens_q, 0.5) * 1.2)

        # Add value label
        ax.text(cohens_q + 0.02, 0, f'{cohens_q:.4f}', va='center', fontweight='bold', fontsize=12)

        plt.tight_layout()
        output_path = self.output_dir / 'effect_size.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_path}")

    def generate_all_figures(self, results: Dict) -> None:
        """
        Generate all 3 figures.

        Args:
            results: {
                "fisher": dict,
                "factual": {"r": float, "ci": tuple, "n": int},
                "misinfo": {"r": float, "ci": tuple, "n": int},
                "effect_size": dict,
                "gate": dict
            }
        """
        print("\n" + "="*80)
        print("GENERATING VISUALIZATIONS")
        print("="*80)

        # Mandatory gate metrics comparison
        self.plot_gate_metrics_comparison(
            results['fisher'],
            results['gate']
        )

        # Forest plot
        self.plot_forest_plot(
            r_factual=results['factual']['r'],
            r_misinfo=results['misinfo']['r'],
            ci_factual=results['factual']['ci'],
            ci_misinfo=results['misinfo']['ci'],
            n_factual=results['factual']['n'],
            n_misinfo=results['misinfo']['n'],
            p_value=results['fisher']['p_value']
        )

        # Effect size
        self.plot_effect_size(results['effect_size'])

        print("="*80)
