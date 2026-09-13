"""Visualization for H-M4 SNR comparison."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple
from snr_analysis import SNRResult


def plot_snr_comparison(
    snr_always: SNRResult,
    snr_gated: SNRResult,
    ci_always: Tuple[float, float],
    ci_gated: Tuple[float, float],
    path: str
) -> None:
    """Bar chart: SNR for each policy with error bars."""
    fig, ax = plt.subplots(figsize=(8, 6))

    policies = ['Fine-Always', 'Fine-Gated']
    snrs = [snr_always.snr, snr_gated.snr]
    errors = [
        [snr_always.snr - ci_always[0], snr_gated.snr - ci_gated[0]],
        [ci_always[1] - snr_always.snr, ci_gated[1] - snr_gated.snr]
    ]

    bars = ax.bar(policies, snrs, color=['#1f77b4', '#2ca02c'], edgecolor='black')
    ax.errorbar(policies, snrs, yerr=errors, fmt='none', color='black', capsize=5)

    ax.set_ylabel('Signal-to-Noise Ratio (SNR)')
    ax.set_title('H-M4: SNR Comparison by Policy')
    ax.set_ylim(0, max(snrs) * 1.3)

    for bar, snr in zip(bars, snrs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{snr:.3f}', ha='center', va='bottom', fontsize=12)

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_snr_bootstrap_distribution(
    always_dist: List[float],
    gated_dist: List[float],
    path: str
) -> None:
    """Boxplot of bootstrap SNR distributions."""
    fig, ax = plt.subplots(figsize=(8, 6))

    data = [always_dist, gated_dist]
    bp = ax.boxplot(data, patch_artist=True)
    ax.set_xticklabels(['Fine-Always', 'Fine-Gated'])

    colors = ['#1f77b4', '#2ca02c']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel('Bootstrap SNR Distribution')
    ax.set_title('H-M4: Bootstrap SNR Distributions')

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_signal_noise_scatter(
    u_line: List[Dict],
    u_ignore: List[Dict],
    path: str
) -> None:
    """Scatter: signal vs noise, colored by error type."""
    fig, ax = plt.subplots(figsize=(8, 6))

    u_line_signals = [r['gt_grad'] for r in u_line if r]
    u_line_noises = [r['other_grad'] for r in u_line if r]
    u_ignore_signals = [r['gt_grad'] for r in u_ignore if r]
    u_ignore_noises = [r['other_grad'] for r in u_ignore if r]

    ax.scatter(u_line_signals, u_line_noises, alpha=0.6, label='U_line', c='#2ca02c', s=30)
    ax.scatter(u_ignore_signals, u_ignore_noises, alpha=0.6, label='U_ignore', c='#d62728', s=30)

    ax.set_xlabel('Signal (GT Gradient)')
    ax.set_ylabel('Noise (Other Gradient)')
    ax.set_title('H-M4: Signal vs Noise by Error Type')
    ax.legend()

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_error_type_contribution(
    u_line: List[Dict],
    u_ignore: List[Dict],
    path: str
) -> None:
    """Stacked bar: contribution of each error type to aggregate SNR."""
    fig, ax = plt.subplots(figsize=(8, 6))

    u_line_signal = np.mean([r['gt_grad'] for r in u_line if r]) if u_line else 0
    u_line_noise = np.mean([r['other_grad'] for r in u_line if r]) if u_line else 1e-8
    u_ignore_signal = np.mean([r['gt_grad'] for r in u_ignore if r]) if u_ignore else 0
    u_ignore_noise = np.mean([r['other_grad'] for r in u_ignore if r]) if u_ignore else 1e-8

    categories = ['Signal', 'Noise']
    u_line_vals = [u_line_signal, u_line_noise]
    u_ignore_vals = [u_ignore_signal, u_ignore_noise]

    x = np.arange(len(categories))
    width = 0.35

    ax.bar(x - width/2, u_line_vals, width, label='U_line', color='#2ca02c')
    ax.bar(x + width/2, u_ignore_vals, width, label='U_ignore', color='#d62728')

    ax.set_xlabel('Component')
    ax.set_ylabel('Mean Gradient Magnitude')
    ax.set_title('H-M4: Error Type Contribution')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
