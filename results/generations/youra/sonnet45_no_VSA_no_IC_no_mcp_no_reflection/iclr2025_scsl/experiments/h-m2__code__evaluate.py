"""
Evaluation and visualization for h-m2.
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import ttest_ind


def compute_temporal_gap_stats(results: list) -> dict:
    """Compute mean/std of delta across seeds."""
    deltas = [r['delta'] for r in results if r['delta'] is not None]
    return {
        'mean': np.mean(deltas) if deltas else None,
        'std': np.std(deltas) if deltas else None,
        'count': len(deltas)
    }


def test_architecture_difference(
    gaps_resnet: list,
    gaps_vit: list,
    alpha: float = 0.05
) -> dict:
    """
    Test if ResNet gaps are larger than ViT gaps.

    Args:
        gaps_resnet: Temporal gaps for ResNet-50 across seeds
        gaps_vit: Temporal gaps for ViT-B/16 across seeds
        alpha: Significance level (default 0.05)

    Returns:
        {
            'mean_delta_resnet': float,
            'mean_delta_vit': float,
            'diff': float,
            'p_value': float,
            'significant': bool,
            'gate_passed': bool
        }
    """
    mean_resnet = np.mean(gaps_resnet)
    mean_vit = np.mean(gaps_vit)
    diff = mean_resnet - mean_vit

    # One-tailed test: H1: ResNet > ViT
    t_stat, p_value_two_tailed = ttest_ind(gaps_resnet, gaps_vit)
    p_value = p_value_two_tailed / 2 if t_stat > 0 else 1 - p_value_two_tailed / 2

    significant = p_value < alpha
    gate_passed = (diff >= 2.0) and significant

    return {
        'mean_delta_resnet': mean_resnet,
        'mean_delta_vit': mean_vit,
        'diff': diff,
        'p_value': p_value,
        'significant': significant,
        'gate_passed': gate_passed
    }


def plot_comparison(results_path: str, output_path: str):
    """Generate comparison bar plot for gate visualization."""
    with open(results_path, 'r') as f:
        results = json.load(f)

    delta_resnet = results['resnet50']['delta']
    delta_vit = results['vit_b16']['delta']

    if delta_resnet is None or delta_vit is None:
        print("Cannot plot: missing convergence data")
        return

    fig, ax = plt.subplots(figsize=(8, 5))

    architectures = ['ResNet-50', 'ViT-B/16']
    deltas = [delta_resnet, delta_vit]
    colors = ['#E74C3C', '#3498DB']

    bars = ax.bar(architectures, deltas, color=colors, alpha=0.7, edgecolor='black')

    # Annotate values
    for bar, val in zip(bars, deltas):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f'{val:.1f}', ha='center', va='bottom', fontsize=12)

    # Gate threshold line
    ax.axhline(y=2, color='green', linestyle='--', linewidth=2, label='Gate threshold (Δ≥2)')

    ax.set_ylabel('Temporal Gap Δ (epochs)', fontsize=12)
    ax.set_title('Temporal Gap Comparison: ResNet-50 vs ViT-B/16', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Comparison plot saved to {output_path}")


if __name__ == '__main__':
    # Generate comparison plot from results
    plot_comparison(
        '../results/full_results.json',
        '../figures/resnet_vs_vit_comparison.png'
    )
