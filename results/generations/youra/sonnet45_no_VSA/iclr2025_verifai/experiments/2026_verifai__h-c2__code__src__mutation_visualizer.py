import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import List
from comparison_analyzer import ComparisonResult
from mutation_tester import KillRateResult
from dataset_loader import Program

class MutationVisualizer:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_style("whitegrid")

    def plot_kill_rate_comparison(self, comparisons: List[ComparisonResult], output_path: str):
        fig, ax = plt.subplots(figsize=(10, 6))

        synth_rates = [c.synthesized_kill_rate for c in comparisons]
        gold_rates = [c.gold_kill_rate for c in comparisons]

        mean_synth = np.mean(synth_rates)
        mean_gold = np.mean(gold_rates)

        x = np.arange(2)
        rates = [mean_synth, mean_gold]
        labels = ['Synthesized', 'Gold']

        bars = ax.bar(x, rates, color=['steelblue', 'darkorange'])
        ax.axhline(y=70, color='r', linestyle='--', label='70% Threshold')

        ax.set_ylabel('Mutation Kill Rate (%)', fontsize=12)
        ax.set_title('Mutation Kill Rate Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        for i, (bar, rate) in enumerate(zip(bars, rates)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{rate:.1f}%',
                   ha='center', va='bottom', fontsize=11)

        plt.tight_layout()
        plt.savefig(self.output_dir / output_path, dpi=300)
        plt.close()

    def plot_kill_rate_distribution(self, results: List[KillRateResult], output_path: str):
        fig, ax = plt.subplots(figsize=(10, 6))

        kill_rates = [r.kill_rate for r in results]

        ax.hist(kill_rates, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
        ax.axvline(x=np.mean(kill_rates), color='r', linestyle='--',
                  label=f'Mean: {np.mean(kill_rates):.1f}%')

        ax.set_xlabel('Kill Rate (%)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Kill Rate Distribution', fontsize=14, fontweight='bold')
        ax.legend()

        plt.tight_layout()
        plt.savefig(self.output_dir / output_path, dpi=300)
        plt.close()

    def plot_operator_effectiveness(self, results: List[KillRateResult], output_path: str):
        fig, ax = plt.subplots(figsize=(12, 6))

        operator_stats = {}
        for result in results:
            for op_type, stats in result.operator_breakdown.items():
                if op_type not in operator_stats:
                    operator_stats[op_type] = []
                operator_stats[op_type].append(stats.get("kill_rate", 0.0))

        operators = list(operator_stats.keys())
        mean_rates = [np.mean(rates) for rates in operator_stats.values()]

        bars = ax.bar(range(len(operators)), mean_rates, color='steelblue')
        ax.set_ylabel('Kill Rate (%)', fontsize=12)
        ax.set_title('Mutation Operator Effectiveness', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(operators)))
        ax.set_xticklabels(operators, rotation=45, ha='right')

        for bar, rate in zip(bars, mean_rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{rate:.1f}%',
                   ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig(self.output_dir / output_path, dpi=300)
        plt.close()

    def plot_strength_vs_discharge(self, results: List[KillRateResult],
                                   discharge_data: dict, output_path: str):
        fig, ax = plt.subplots(figsize=(10, 6))

        kill_rates = [r.kill_rate for r in results]
        discharge_rates = [discharge_data.get(r.program_id, 70.0) for r in results]

        ax.scatter(discharge_rates, kill_rates, alpha=0.6, s=100, color='steelblue')

        ax.set_xlabel('Proof Discharge Rate (%)', fontsize=12)
        ax.set_ylabel('Mutation Kill Rate (%)', fontsize=12)
        ax.set_title('Specification Strength vs Proof Discharge', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(self.output_dir / output_path, dpi=300)
        plt.close()

    def plot_complexity_analysis(self, results: List[KillRateResult],
                                programs: List[Program], output_path: str):
        fig, ax = plt.subplots(figsize=(10, 6))

        locs = [p.loc for p in programs]
        kill_rates = [r.kill_rate for r in results]

        ax.scatter(locs, kill_rates, alpha=0.6, s=100, color='steelblue')

        ax.set_xlabel('Lines of Code', fontsize=12)
        ax.set_ylabel('Mutation Kill Rate (%)', fontsize=12)
        ax.set_title('Program Complexity vs Kill Rate', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(self.output_dir / output_path, dpi=300)
        plt.close()

    def generate_all_figures(self, comparisons: List[ComparisonResult],
                            programs: List[Program]):
        synthesized_results = [c.synthesized_result for c in comparisons]
        gold_results = [c.gold_result for c in comparisons]

        self.plot_kill_rate_comparison(comparisons, "gate_comparison.png")
        self.plot_kill_rate_distribution(synthesized_results, "kill_rate_distribution.png")

        if synthesized_results and synthesized_results[0].operator_breakdown:
            self.plot_operator_effectiveness(synthesized_results, "operator_effectiveness.png")

        discharge_data = {p.program_id: 70.0 for p in programs}
        self.plot_strength_vs_discharge(synthesized_results, discharge_data,
                                       "strength_vs_discharge.png")
        self.plot_complexity_analysis(synthesized_results, programs,
                                     "complexity_vs_kill_rate.png")
