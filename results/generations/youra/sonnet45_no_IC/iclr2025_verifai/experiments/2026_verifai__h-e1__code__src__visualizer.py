"""Visualizer - Generate all 4 required figures."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Dict
from .completeness_validator import CompletenessValidator


class Visualizer:
    """Generate visualization figures."""

    def __init__(self, output_dir: Path, dpi: int = 300):
        """Initialize with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

    def plot_gate_metrics(self, results: Dict) -> None:
        """Generate Figure 1: Gate metrics comparison.

        Args:
            results: Evaluation results dict
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        metrics = ['Completeness Rate']
        target = [results['threshold']]
        actual = [results['completeness_rate']]

        x = np.arange(len(metrics))
        width = 0.35

        # Color based on pass/fail
        color = 'green' if results['primary_pass'] else 'red'

        bars1 = ax.bar(x - width/2, target, width, label='Target', color='blue', alpha=0.7)
        bars2 = ax.bar(x + width/2, actual, width, label='Actual', color=color, alpha=0.7)

        # Threshold line
        ax.axhline(y=results['threshold'], color='black', linestyle='--', linewidth=1, label='Threshold')

        ax.set_ylabel('Rate')
        ax.set_title('Figure 1: Gate Metrics Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.set_ylim([0, 1.1])
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar in bars1 + bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1%}',
                   ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        output_path = self.output_dir / "fig1_gate_metrics.png"
        plt.savefig(output_path, dpi=self.dpi)
        plt.close()
        print(f"  ✓ Figure 1 saved: {output_path.name}")

    def plot_per_file_distribution(self, traces: List[Dict], validator: CompletenessValidator) -> None:
        """Generate Figure 2: Per-file completeness distribution.

        Args:
            traces: List of trace dicts
            validator: CompletenessValidator instance
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Calculate per-file rates with outcome
        file_data = []
        for trace in traces:
            if len(trace['tool_calls']) == 0:
                continue

            complete = sum(1 for tc in trace['tool_calls'] if validator.validate_tool_call(tc))
            rate = complete / len(trace['tool_calls'])
            file_data.append({
                'file': trace['file'],
                'rate': rate,
                'outcome': trace['outcome']
            })

        # Sort by rate for better visualization
        file_data.sort(key=lambda x: x['rate'])

        # Extract data
        x_pos = np.arange(len(file_data))
        rates = [d['rate'] for d in file_data]
        colors = ['green' if d['outcome'] == 'success' else 'red' for d in file_data]

        # Plot bars
        bars = ax.bar(x_pos, rates, color=colors, alpha=0.7)

        # Mean line
        mean_rate = np.mean(rates)
        ax.axhline(y=mean_rate, color='blue', linestyle='--', linewidth=2, label=f'Mean: {mean_rate:.2%}')

        ax.set_xlabel('Trace File Index')
        ax.set_ylabel('Completeness Rate')
        ax.set_title('Figure 2: Per-File Completeness Distribution')
        ax.set_ylim([0, 1.1])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / "fig2_per_file.png"
        plt.savefig(output_path, dpi=self.dpi)
        plt.close()
        print(f"  ✓ Figure 2 saved: {output_path.name}")

    def plot_completeness_breakdown(self, traces: List[Dict], validator: CompletenessValidator) -> None:
        """Generate Figure 3: Completeness breakdown by outcome.

        Args:
            traces: List of trace dicts
            validator: CompletenessValidator instance
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Calculate complete/incomplete by outcome
        success_complete = 0
        success_incomplete = 0
        fail_complete = 0
        fail_incomplete = 0

        for trace in traces:
            for tc in trace['tool_calls']:
                if validator.validate_tool_call(tc):
                    if trace['outcome'] == 'success':
                        success_complete += 1
                    else:
                        fail_complete += 1
                else:
                    if trace['outcome'] == 'success':
                        success_incomplete += 1
                    else:
                        fail_incomplete += 1

        # Data for stacked bars
        categories = ['Successful\nExecutions', 'Failed\nExecutions']
        complete = [success_complete, fail_complete]
        incomplete = [success_incomplete, fail_incomplete]

        x_pos = np.arange(len(categories))
        width = 0.5

        # Stacked bars
        p1 = ax.bar(x_pos, complete, width, label='Complete', color='green', alpha=0.7)
        p2 = ax.bar(x_pos, incomplete, width, bottom=complete, label='Incomplete', color='red', alpha=0.7)

        ax.set_ylabel('Tool Call Count')
        ax.set_title('Figure 3: Tool Call Completeness Breakdown')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for i, (comp, incomp) in enumerate(zip(complete, incomplete)):
            total = comp + incomp
            ax.text(i, total, f'{total}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.tight_layout()
        output_path = self.output_dir / "fig3_breakdown.png"
        plt.savefig(output_path, dpi=self.dpi)
        plt.close()
        print(f"  ✓ Figure 3 saved: {output_path.name}")

    def plot_nl_content_analysis(self, traces: List[Dict], validator: CompletenessValidator) -> None:
        """Generate Figure 4: NL content word count scatter.

        Args:
            traces: List of trace dicts
            validator: CompletenessValidator instance
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Extract word counts
        word_counts = []
        statuses = []

        for trace in traces:
            for tc in trace['tool_calls']:
                params_text = validator.extract_nl_content(tc.get('parameters', {}))
                result_text = validator.extract_nl_content(tc.get('result', {}))
                total_words = validator.count_words(params_text) + validator.count_words(result_text)

                word_counts.append(total_words)
                statuses.append(validator.validate_tool_call(tc))

        # Create scatter plot
        x_pos = np.arange(len(word_counts))
        colors = ['green' if s else 'red' for s in statuses]

        ax.scatter(x_pos, word_counts, c=colors, alpha=0.5, s=10)

        # Threshold line
        ax.axhline(y=validator.min_word_count, color='black', linestyle='--', linewidth=2,
                  label=f'Threshold: {validator.min_word_count} words')

        ax.set_xlabel('Tool Call Index')
        ax.set_ylabel('Word Count (Parameters + Results)')
        ax.set_title('Figure 4: Natural Language Content Analysis')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / "fig4_nl_content.png"
        plt.savefig(output_path, dpi=self.dpi)
        plt.close()
        print(f"  ✓ Figure 4 saved: {output_path.name}")

    def generate_all_figures(self, traces: List[Dict], results: Dict, validator: CompletenessValidator) -> None:
        """Generate all 4 figures.

        Args:
            traces: List of trace dicts
            results: Evaluation results dict
            validator: CompletenessValidator instance
        """
        print("\n📊 Generating figures...")
        self.plot_gate_metrics(results)
        self.plot_per_file_distribution(traces, validator)
        self.plot_completeness_breakdown(traces, validator)
        self.plot_nl_content_analysis(traces, validator)
        print("✓ All figures generated")
