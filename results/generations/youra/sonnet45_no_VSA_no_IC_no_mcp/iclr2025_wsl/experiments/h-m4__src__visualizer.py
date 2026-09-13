"""Visualization for results."""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict
import os


class Visualizer:
    """Generate required figures for Phase 4 report."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_gate_comparison(self, baseline: float, proposed: float, threshold: float, gate_passed: bool) -> str:
        """Figure 1: Gate metrics comparison (mandatory).

        Returns: path to saved figure
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        categories = ['Random Baseline', 'Proposed System', 'Gate Threshold']
        values = [baseline * 100, proposed * 100, threshold * 100]
        colors = ['red', 'green' if gate_passed else 'red', 'blue']

        bars = ax.bar(categories, values, color=colors, alpha=0.7)
        ax.axhline(y=threshold * 100, color='blue', linestyle='--', label='Gate Threshold')
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Gate Metrics Comparison: Experimental Success Rate')
        ax.set_ylim([0, 100])
        ax.legend()

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom')

        path = os.path.join(self.output_dir, 'gate_metrics_comparison.png')
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    def plot_success_by_domain(self, results: List[Dict], hypotheses: List[Dict]) -> str:
        """Figure 2: Success rate breakdown by domain.

        Returns: path to saved figure
        """
        # Map hypothesis_id to domain
        hyp_domains = {h['id']: h['domain'] for h in hypotheses}

        # Count successes by domain
        domain_stats = {}
        for result in results:
            hyp_id = result['hypothesis_id']
            domain = hyp_domains.get(hyp_id, 'unknown')

            if domain not in domain_stats:
                domain_stats[domain] = {'success': 0, 'total': 0}

            domain_stats[domain]['total'] += 1
            if result['success']:
                domain_stats[domain]['success'] += 1

        # Calculate rates
        domains = list(domain_stats.keys())
        rates = [domain_stats[d]['success'] / domain_stats[d]['total'] * 100 for d in domains]

        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(domains, rates, alpha=0.7, color='steelblue')
        ax.set_ylabel('Success Rate (%)')
        ax.set_xlabel('Domain')
        ax.set_title('Experimental Success Rate by Domain')
        ax.set_ylim([0, 100])
        ax.axhline(y=65, color='red', linestyle='--', label='Gate Threshold (65%)')
        ax.legend()

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom')

        path = os.path.join(self.output_dir, 'success_rate_by_domain.png')
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    def plot_classification_dist(self, hypotheses: List[Dict]) -> str:
        """Figure 3: Classification distribution pie chart.

        Returns: path to saved figure
        """
        testable = sum(1 for h in hypotheses if h['system_classification'] == 'testable')
        not_testable = sum(1 for h in hypotheses if h['system_classification'] == 'not-testable')

        fig, ax = plt.subplots(figsize=(6, 6))
        labels = ['Testable', 'Not Testable']
        sizes = [testable, not_testable]
        colors = ['green', 'red']
        explode = (0.05, 0)

        ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
               shadow=True, startangle=90)
        ax.set_title(f'Classification Distribution (n={len(hypotheses)})')

        path = os.path.join(self.output_dir, 'classification_distribution.png')
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    def plot_pvalue_dist(self, p_values: List[float]) -> str:
        """Figure 4: P-value distribution histogram.

        Returns: path to saved figure
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        ax.hist(p_values, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
        ax.axvline(x=0.05, color='red', linestyle='--', label='α = 0.05')
        ax.set_xlabel('P-value')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Experimental P-values')
        ax.legend()

        # Add count annotations
        significant = sum(1 for p in p_values if p < 0.05)
        not_significant = len(p_values) - significant
        ax.text(0.6, ax.get_ylim()[1] * 0.9,
               f'p < 0.05: {significant}\np ≥ 0.05: {not_significant}',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        path = os.path.join(self.output_dir, 'pvalue_distribution.png')
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path
