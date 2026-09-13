#!/usr/bin/env python3
"""Visualization for H-M1 validation report"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def plot_gate_metrics():
    """Generate required gate metrics bar chart"""
    conditions = ['FullKV', 'H2O', 'ProvenanceCache', 'Random']
    f1_means = [0.6977, 0.6497, 0.6897, 0.4478]
    f1_stds = [0.0345, 0.0340, 0.0353, 0.0359]

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(conditions))
    bars = ax.bar(x, f1_means, yerr=f1_stds, capsize=5, alpha=0.8,
                  color=['gray', 'steelblue', 'forestgreen', 'coral'])

    # Gate threshold line
    h2o_threshold = f1_means[1] * 1.05
    ax.axhline(h2o_threshold, color='red', linestyle='--', linewidth=2,
               label=f'Gate Threshold (H2O × 1.05 = {h2o_threshold:.4f})')

    # Annotations
    for i, (bar, mean, std) in enumerate(zip(bars, f1_means, f1_stds)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std + 0.01,
                f'{mean:.4f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

        if conditions[i] == 'ProvenanceCache':
            gain = (mean / f1_means[1] - 1) * 100
            ax.text(bar.get_x() + bar.get_width()/2., height/2,
                    f'+{gain:.2f}%\nvs H2O',
                    ha='center', va='center', fontsize=9, color='white', fontweight='bold')

    ax.set_xlabel('Cache Policy', fontsize=12)
    ax.set_ylabel('F1 Score', fontsize=12)
    ax.set_title('H-M1 Gate Metrics: ProvenanceCache vs Baselines (25% Cache Budget)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontsize=11)
    ax.set_ylim(0, 0.85)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle=':')

    fig.tight_layout()
    output_dir = Path(__file__).parent.parent / 'figures'
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'gate_metrics.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

if __name__ == '__main__':
    plot_gate_metrics()
