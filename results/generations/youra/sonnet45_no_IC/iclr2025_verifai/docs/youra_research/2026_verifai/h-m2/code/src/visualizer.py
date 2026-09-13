"""Visualizer for H-M1 - Generate NL content figures."""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Dict
from .nl_content_validator import NLContentValidator


class Visualizer:
    """Generate visualization figures."""

    def __init__(self, output_dir: Path, dpi: int = 300):
        """Initialize with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

    def plot_gate_metrics(self, results: Dict) -> None:
        """Generate Figure 1: Gate metrics comparison."""
        fig, ax = plt.subplots(figsize=(8, 6))

        metrics = ['NL Presence Rate']
        target = [results['threshold'] * 100]
        actual = [results['nl_presence_rate'] * 100]

        x = np.arange(len(metrics))
        width = 0.35

        color = 'green' if results['gate_passed'] else 'red'

        ax.bar(x - width/2, target, width, label='Threshold (90%)', color='blue', alpha=0.7)
        ax.bar(x + width/2, actual, width, label='Actual', color=color, alpha=0.7)

        ax.axhline(y=90, color='black', linestyle='--', linewidth=1, label='Gate: 90%')

        ax.set_ylabel('Percentage (%)')
        ax.set_title('Figure 1: Gate Metrics Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.set_ylim([0, 110])
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / "fig1_gate_metrics.png"
        plt.savefig(output_path, dpi=self.dpi)
        plt.close()
        print(f"  ✓ Figure 1 saved: {output_path.name}")

    def plot_word_count_distribution(self, traces: List[Dict], validator: NLContentValidator) -> None:
        """Generate Figure 2: Word count histogram."""
        fig, ax = plt.subplots(figsize=(10, 6))

        word_counts = []
        for trace in traces:
            for tc in trace['tool_calls']:
                _, query_words, result_words = validator.validate_nl_presence(tc)
                word_counts.append(query_words + result_words)

        if not word_counts:
            word_counts = [0]

        ax.hist(word_counts, bins=[0, 5, 10, 20, 50, 100, 200], edgecolor='black', alpha=0.7)
        ax.axvline(x=10, color='red', linestyle='--', linewidth=2, label='Threshold: 10 words')

        ax.set_xlabel('Total Word Count')
        ax.set_ylabel('Number of Tool Calls')
        ax.set_title('Figure 2: Word Count Distribution')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / "fig2_word_count_distribution.png"
        plt.savefig(output_path, dpi=self.dpi)
        plt.close()
        print(f"  ✓ Figure 2 saved: {output_path.name}")

    def plot_nl_source_breakdown(self, results: Dict) -> None:
        """Generate Figure 3: NL source breakdown."""
        fig, ax = plt.subplots(figsize=(8, 6))

        breakdown = results['source_breakdown']
        labels = list(breakdown.keys())
        sizes = list(breakdown.values())

        colors = ['#4CAF50', '#2196F3', '#FFC107', '#F44336']
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title('Figure 3: NL Source Breakdown')

        plt.tight_layout()
        output_path = self.output_dir / "fig3_nl_source_breakdown.png"
        plt.savefig(output_path, dpi=self.dpi)
        plt.close()
        print(f"  ✓ Figure 3 saved: {output_path.name}")

    def plot_nl_by_tool_type(self, results: Dict) -> None:
        """Generate Figure 4: NL rate by tool type."""
        fig, ax = plt.subplots(figsize=(8, 6))

        tool_breakdown = results['tool_type_breakdown']
        categories = list(tool_breakdown.keys())
        rates = [tool_breakdown[cat]['rate'] * 100 for cat in categories]

        x_pos = np.arange(len(categories))
        bars = ax.bar(x_pos, rates, color=['#2196F3', '#4CAF50'], alpha=0.7)

        ax.set_xlabel('Tool Type')
        ax.set_ylabel('NL Presence Rate (%)')
        ax.set_title('Figure 4: NL Presence by Tool Type')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories)
        ax.set_ylim([0, 110])
        ax.grid(axis='y', alpha=0.3)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        output_path = self.output_dir / "fig4_nl_by_tool_type.png"
        plt.savefig(output_path, dpi=self.dpi)
        plt.close()
        print(f"  ✓ Figure 4 saved: {output_path.name}")

    def generate_all_figures(self, traces: List[Dict], results: Dict, validator: NLContentValidator) -> None:
        """Generate all 4 figures."""
        print("\n📊 Generating figures...")
        self.plot_gate_metrics(results)
        self.plot_word_count_distribution(traces, validator)
        self.plot_nl_source_breakdown(results)
        self.plot_nl_by_tool_type(results)
        print("✓ All figures generated")
