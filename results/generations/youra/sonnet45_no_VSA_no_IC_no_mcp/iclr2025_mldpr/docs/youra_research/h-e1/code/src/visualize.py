import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from typing import List, Dict

class Visualizer:
    def __init__(self, figures_dir: Path):
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(exist_ok=True)

    def plot_gate_metrics(self, report: Dict):
        fig, ax = plt.subplots(figsize=(10, 6))

        metrics = ['Overhead (%)', 'Capture Rate (%)', 'Event Count']
        targets = [10, 95, 100]
        actuals = [report['overhead_max'], report['capture_rate'], report['event_count']]

        x = range(len(metrics))
        width = 0.35

        ax.bar([i - width/2 for i in x], targets, width, label='Target', alpha=0.8)
        ax.bar([i + width/2 for i in x], actuals, width, label='Actual', alpha=0.8)

        ax.set_xlabel('Metrics')
        ax.set_ylabel('Value')
        ax.set_title('Gate Metrics: Target vs Actual')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.figures_dir / "gate_metrics.png", dpi=100)
        plt.close()

    def plot_load_time_comparison(self, df: pd.DataFrame):
        fig, ax = plt.subplots(figsize=(10, 6))

        grouped = df.groupby('dataset').mean()
        datasets = grouped.index
        x = range(len(datasets))
        width = 0.35

        ax.bar([i - width/2 for i in x], grouped['baseline_ms'], width, label='Baseline', alpha=0.8)
        ax.bar([i + width/2 for i in x], grouped['instrumented_ms'], width, label='Instrumented', alpha=0.8)

        ax.set_xlabel('Dataset')
        ax.set_ylabel('Load Time (ms)')
        ax.set_title('Load Time Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(datasets)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.figures_dir / "load_time_comparison.png", dpi=100)
        plt.close()

    def plot_overhead_distribution(self, df: pd.DataFrame):
        fig, ax = plt.subplots(figsize=(10, 6))

        data = [df[df['dataset'] == ds]['overhead_pct'] for ds in df['dataset'].unique()]

        ax.boxplot(data, labels=df['dataset'].unique())
        ax.axhline(y=10, color='r', linestyle='--', label='Threshold (10%)')

        ax.set_xlabel('Dataset')
        ax.set_ylabel('Overhead (%)')
        ax.set_title('Overhead Distribution Across Runs')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.figures_dir / "overhead_distribution.png", dpi=100)
        plt.close()

    def plot_capture_rate(self, events: List[Dict]):
        fig, ax = plt.subplots(figsize=(10, 6))

        timestamps = sorted([e['timestamp'] for e in events])
        cumulative = list(range(1, len(timestamps) + 1))

        ax.plot(cumulative, linewidth=2)

        ax.set_xlabel('Time (Event Index)')
        ax.set_ylabel('Cumulative Events Captured')
        ax.set_title('Cumulative Event Capture Over Time')
        ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.figures_dir / "capture_rate.png", dpi=100)
        plt.close()
