"""Visualization module for H-M3."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import Dict, Any
from pathlib import Path


def plot_gate_comparison(metrics: Dict[str, Any], output_path: Path, dpi: int = 150) -> None:
    """Generate gate metrics comparison bar chart."""
    fig, ax = plt.subplots(figsize=(8, 6))

    labels = ['CoT Order Rate', 'Markers Precede Rate']
    values = [metrics['cot_order_rate'], metrics['markers_precede_rate']]
    thresholds = [metrics['gate_1_threshold'], metrics['gate_2_threshold']]

    x = range(len(labels))
    colors = ['#2ecc71' if v > t else '#e74c3c' for v, t in zip(values, thresholds)]
    bars = ax.bar(x, values, color=colors)

    for i, t in enumerate(thresholds):
        ax.axhline(y=t, xmin=(i/len(labels))+0.05, xmax=((i+1)/len(labels))-0.05,
                   color='red', linestyle='--', linewidth=2, label=f'Threshold {t:.0%}' if i == 0 else '')

    ax.set_ylabel('Rate')
    ax.set_title('H-M3 Gate Metrics vs Thresholds')
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.1)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.1%}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi)
    plt.close()
