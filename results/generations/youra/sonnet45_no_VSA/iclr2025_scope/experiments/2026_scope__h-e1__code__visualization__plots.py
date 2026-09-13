"""
Visualizer - T-06
Generate all required visualizations for hypothesis validation.
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import pandas as pd
import numpy as np
from typing import List, Dict
import os
import seaborn as sns


class Visualizer:
    """Generate visualizations for contractability analysis."""

    def __init__(self, output_dir: str = "figures"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Configuration from 03_config.md
        self.config = {
            "dpi": 300,
            "colors": {
                "pass_threshold": "#2ecc71",
                "fail_threshold": "#e74c3c",
                "structural": "#3498db",
                "metamorphic": "#f39c12",
                "composition": "#9b59b6",
                "overall": "#34495e"
            },
            "gate_threshold": 40.0,
            "font_sizes": {
                "title": 14,
                "axis_label": 12,
                "tick_label": 10,
                "legend": 10
            }
        }

    def plot_gate_metrics(self, metrics: 'ContractabilityMetrics') -> None:
        """Mandatory: Bar chart with threshold line at 40%."""
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = ['Structural', 'Metamorphic', 'Composition', 'Overall']
        rates = [
            metrics.structural_rate,
            metrics.metamorphic_rate,
            metrics.composition_rate,
            metrics.overall_rate
        ]

        colors = [
            self.config["colors"]["structural"],
            self.config["colors"]["metamorphic"],
            self.config["colors"]["composition"],
            self.config["colors"]["overall"]
        ]

        # Bar chart
        bars = ax.bar(categories, rates, color=colors, alpha=0.7, edgecolor='black')

        # Error bars (only for Overall, using CI)
        ci_errors = [[metrics.overall_rate - metrics.ci_lower], [metrics.ci_upper - metrics.overall_rate]]
        ax.errorbar(
            [3],  # Overall is 4th bar (index 3)
            [metrics.overall_rate],
            yerr=ci_errors,
            fmt='none',
            ecolor='black',
            capsize=5,
            capthick=2
        )

        # Threshold line
        ax.axhline(
            y=self.config["gate_threshold"],
            color=self.config["colors"]["fail_threshold"],
            linestyle='--',
            linewidth=2,
            label=f'{self.config["gate_threshold"]:.0f}% Threshold'
        )

        # Labels and formatting
        ax.set_ylabel('Contractability Rate (%)', fontsize=self.config["font_sizes"]["axis_label"])
        ax.set_title('Gate Metrics: Contractability Rate by Defect Category',
                     fontsize=self.config["font_sizes"]["title"], fontweight='bold')
        ax.set_ylim(0, 100)
        ax.legend(fontsize=self.config["font_sizes"]["legend"])
        ax.tick_params(labelsize=self.config["font_sizes"]["tick_label"])
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar, rate in zip(bars, rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{rate:.1f}%',
                   ha='center', va='bottom',
                   fontsize=self.config["font_sizes"]["tick_label"])

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'gate_metrics_comparison.png')
        plt.savefig(output_path, dpi=self.config["dpi"], bbox_inches='tight')
        plt.close()
        print(f"Saved: {output_path}")

    def plot_defect_distribution(self, defects: pd.DataFrame) -> None:
        """Pie chart of defect type distribution."""
        fig, ax = plt.subplots(figsize=(8, 8))

        type_counts = defects['type'].value_counts()
        colors = [
            self.config["colors"]["structural"],
            self.config["colors"]["metamorphic"],
            self.config["colors"]["composition"]
        ]

        ax.pie(
            type_counts.values,
            labels=type_counts.index,
            autopct='%1.1f%%',
            colors=colors[:len(type_counts)],
            startangle=90,
            textprops={'fontsize': self.config["font_sizes"]["tick_label"]}
        )

        ax.set_title('Defect Type Distribution',
                     fontsize=self.config["font_sizes"]["title"], fontweight='bold')

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'defect_distribution.png')
        plt.savefig(output_path, dpi=self.config["dpi"], bbox_inches='tight')
        plt.close()
        print(f"Saved: {output_path}")

    def plot_execution_times(self, validation_results: List['ValidationResult']) -> None:
        """Histogram of contract execution times."""
        fig, ax = plt.subplots(figsize=(10, 6))

        times = [r.execution_time for r in validation_results if r.status in ["PASS", "FAIL"]]

        if not times:
            print("No execution times to plot")
            return

        ax.hist(times, bins=30, color=self.config["colors"]["structural"],
                alpha=0.7, edgecolor='black')

        # 10-second threshold line
        ax.axvline(x=10, color=self.config["colors"]["fail_threshold"],
                   linestyle='--', linewidth=2, label='10s Threshold')

        ax.set_xlabel('Execution Time (seconds)', fontsize=self.config["font_sizes"]["axis_label"])
        ax.set_ylabel('Frequency', fontsize=self.config["font_sizes"]["axis_label"])
        ax.set_title('Contract Execution Time Distribution',
                     fontsize=self.config["font_sizes"]["title"], fontweight='bold')
        ax.legend(fontsize=self.config["font_sizes"]["legend"])
        ax.tick_params(labelsize=self.config["font_sizes"]["tick_label"])
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'execution_time_histogram.png')
        plt.savefig(output_path, dpi=self.config["dpi"], bbox_inches='tight')
        plt.close()
        print(f"Saved: {output_path}")

    def plot_version_stability(self, stability_matrix: Dict[str, List[bool]]) -> None:
        """Line chart showing success rate across library versions."""
        fig, ax = plt.subplots(figsize=(10, 6))

        if not stability_matrix:
            print("No stability data to plot")
            return

        # Aggregate stability across all contracts
        versions = list(next(iter(stability_matrix.values())).keys()) if stability_matrix else []

        if not versions:
            print("No version data available")
            return

        stability_rates = []
        for version in versions:
            success_count = sum(
                1 for contract_stability in stability_matrix.values()
                if contract_stability.get(version, False)
            )
            total = len(stability_matrix)
            rate = (success_count / total * 100) if total > 0 else 0
            stability_rates.append(rate)

        ax.plot(versions, stability_rates, marker='o', linewidth=2,
                markersize=8, color=self.config["colors"]["structural"])

        ax.set_xlabel('PyTorch Version', fontsize=self.config["font_sizes"]["axis_label"])
        ax.set_ylabel('Stability Rate (%)', fontsize=self.config["font_sizes"]["axis_label"])
        ax.set_title('Contract Version Stability Across PyTorch Versions',
                     fontsize=self.config["font_sizes"]["title"], fontweight='bold')
        ax.set_ylim(0, 100)
        ax.tick_params(labelsize=self.config["font_sizes"]["tick_label"])
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'version_stability.png')
        plt.savefig(output_path, dpi=self.config["dpi"], bbox_inches='tight')
        plt.close()
        print(f"Saved: {output_path}")

    def plot_kappa_heatmap(self, coder1: List[bool], coder2: List[bool]) -> None:
        """2x2 agreement matrix between coders."""
        fig, ax = plt.subplots(figsize=(6, 6))

        # Create confusion matrix
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(coder1, coder2)

        # Normalize to percentages
        cm_pct = cm.astype('float') / cm.sum() * 100

        # Plot heatmap
        sns.heatmap(
            cm_pct,
            annot=True,
            fmt='.1f',
            cmap='Blues',
            xticklabels=['Not Contractable', 'Contractable'],
            yticklabels=['Not Contractable', 'Contractable'],
            ax=ax,
            cbar_kws={'label': 'Percentage (%)'}
        )

        ax.set_xlabel('Coder 2', fontsize=self.config["font_sizes"]["axis_label"])
        ax.set_ylabel('Coder 1', fontsize=self.config["font_sizes"]["axis_label"])
        ax.set_title('Inter-Rater Agreement Matrix',
                     fontsize=self.config["font_sizes"]["title"], fontweight='bold')

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'kappa_heatmap.png')
        plt.savefig(output_path, dpi=self.config["dpi"], bbox_inches='tight')
        plt.close()
        print(f"Saved: {output_path}")


if __name__ == "__main__":
    # Test visualization
    import sys
    sys.path.append('..')
    from analysis.metrics import ContractabilityMetrics

    # Mock metrics
    metrics = ContractabilityMetrics(
        overall_rate=45.5,
        structural_rate=62.3,
        metamorphic_rate=38.1,
        composition_rate=25.7,
        ci_lower=39.2,
        ci_upper=51.8,
        kappa=0.78,
        gate_status="PASS"
    )

    viz = Visualizer(output_dir="../figures")
    viz.plot_gate_metrics(metrics)

    # Mock defect data
    defects = pd.DataFrame({
        'type': ['structural'] * 175 + ['metamorphic'] * 105 + ['composition'] * 68
    })
    viz.plot_defect_distribution(defects)

    print("\nVisualization test complete")
