"""Visualization module for generating figures."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List


class FigureGenerator:
    """Generate required and supplementary figures."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        sns.set_theme(style="whitegrid")

    def plot_gate_metrics(self, metrics: Dict, targets: Dict, save_path: str = "gate_metrics.png"):
        """Generate required gate metrics bar chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = ['Security %', 'KL-Divergence', 'Jaccard']
        actual_values = [
            metrics['security_percentage'],
            metrics['kl_divergence'],
            metrics['jaccard_agreement']
        ]
        target_values = [
            targets['security_percentage'],
            targets['kl_divergence'],
            targets['jaccard_agreement']
        ]

        x = range(len(categories))
        width = 0.35

        ax.bar([i - width/2 for i in x], actual_values, width, label='Actual', color='#95a5a6')
        ax.bar([i + width/2 for i in x], target_values, width, label='Target', color='#2ecc71')

        ax.set_xlabel('Metrics')
        ax.set_ylabel('Value')
        ax.set_title('Gate Metrics Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, save_path), dpi=300, bbox_inches='tight')
        plt.close()

    def plot_cwe_distribution(self, observed_dist: Dict, target_dist: Dict, save_path: str = "cwe_comparison.png"):
        """Compare CWE distributions."""
        fig, ax = plt.subplots(figsize=(12, 6))

        all_cwes = sorted(set(list(observed_dist.keys()) + list(target_dist.keys())))
        obs_values = [observed_dist.get(cwe, 0) for cwe in all_cwes]
        target_values = [target_dist.get(cwe, 0) * 100 for cwe in all_cwes]  # Scale targets

        x = range(len(all_cwes))
        width = 0.35

        ax.bar([i - width/2 for i in x], obs_values, width, label='Observed', color='#3498db', alpha=0.8)
        ax.bar([i + width/2 for i in x], target_values, width, label='Target', color='#e74c3c', alpha=0.8)

        ax.set_xlabel('CWE Category')
        ax.set_ylabel('Count')
        ax.set_title('CWE Distribution Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(all_cwes, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, save_path), dpi=300, bbox_inches='tight')
        plt.close()

    def plot_revision_timeline(self, traces: List[Dict], save_path: str = "revision_timeline.png"):
        """Show security signal density across tasks."""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Group by task
        from collections import defaultdict
        task_revisions = defaultdict(lambda: {'security': 0, 'runtime': 0})

        for trace in traces:
            task_id = trace.get('task_id', 'unknown')
            if trace.get('analyzer_triggered', False):
                task_revisions[task_id]['security'] += 1
            else:
                task_revisions[task_id]['runtime'] += 1

        tasks = sorted(task_revisions.keys())
        security_counts = [task_revisions[t]['security'] for t in tasks]
        runtime_counts = [task_revisions[t]['runtime'] for t in tasks]

        x = range(len(tasks))
        ax.scatter([i for i in x], security_counts, c='#e74c3c', alpha=0.7, label='Security', s=50)
        ax.scatter([i for i in x], runtime_counts, c='#3498db', alpha=0.7, label='Runtime', s=50)

        ax.set_xlabel('Task Index')
        ax.set_ylabel('Revision Count')
        ax.set_title('Revision Timeline by Task')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, save_path), dpi=300, bbox_inches='tight')
        plt.close()

    def save_all_figures(self, metrics: Dict, targets: Dict, traces: List[Dict]):
        """Generate all figures."""
        self.plot_gate_metrics(metrics, targets)
        self.plot_cwe_distribution(metrics['cwe_distribution'], targets['cwe_distribution'])
        self.plot_revision_timeline(traces)
        print(f"All figures saved to {self.output_dir}")
