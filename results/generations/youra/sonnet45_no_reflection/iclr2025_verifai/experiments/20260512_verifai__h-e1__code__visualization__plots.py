"""Visualization functions for heterogeneity analysis."""
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict
from pathlib import Path


def plot_gate_comparison(metrics: Dict[str, float], save_path: str):
    """Mandatory gate metrics bar chart."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = ['d/n Range', 'Entropy Range']
    targets = [0.20, 2.0]
    actuals = [metrics['d_n_range'], metrics['entropy_range']]

    x_pos = np.arange(len(x))
    width = 0.35

    ax.bar(x_pos - width/2, targets, width, label='Target', color='red', alpha=0.6)
    ax.bar(x_pos + width/2, actuals, width, label='Actual', color='blue', alpha=0.6)

    ax.set_ylabel('Metric Value')
    ax.set_title('Gate Criteria Validation')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x)
    ax.legend()

    # Pass/Fail annotation
    status = 'PASS' if metrics.get('pass_criteria', False) else 'FAIL'
    color = 'green' if metrics.get('pass_criteria', False) else 'red'
    ax.text(0.5, 0.95, status, transform=ax.transAxes,
            fontsize=20, fontweight='bold', color=color,
            ha='center', va='top')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_dn_distribution(dn_values: List[float], save_path: str):
    """Histogram of d/n values with quartile markers."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(dn_values, bins=30, alpha=0.7, edgecolor='black')

    # Add quartile markers
    q1, q2, q3 = np.percentile(dn_values, [25, 50, 75])
    ax.axvline(q1, color='red', linestyle='--', label=f'Q1={q1:.3f}')
    ax.axvline(q2, color='green', linestyle='--', label=f'Q2={q2:.3f}')
    ax.axvline(q3, color='blue', linestyle='--', label=f'Q3={q3:.3f}')

    # Target range indicator
    ax.axhline(0, color='orange', linestyle='-', linewidth=2, alpha=0.3,
              label=f'Target range > 0.20')

    ax.set_xlabel('Normalized Hamming Distance (d/n)')
    ax.set_ylabel('Frequency')
    ax.set_title('d/n Distribution')
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_entropy_distribution(entropy_values: List[float], save_path: str):
    """Histogram of entropy H values."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(entropy_values, bins=30, alpha=0.7, edgecolor='black')

    # Add mean and std
    mean = np.mean(entropy_values)
    std = np.std(entropy_values)
    ax.axvline(mean, color='red', linestyle='--', label=f'Mean={mean:.3f}')
    ax.axvline(mean - std, color='orange', linestyle=':', label=f'±1σ')
    ax.axvline(mean + std, color='orange', linestyle=':')

    ax.set_xlabel('Violation Entropy (H)')
    ax.set_ylabel('Frequency')
    ax.set_title('Entropy Distribution')
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_dn_vs_entropy_scatter(dn_values: List[float], entropy_values: List[float], save_path: str):
    """Scatter plot of d/n vs entropy."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(dn_values, entropy_values, alpha=0.6, edgecolor='black')

    # Basin entry criteria boundary (d/n < 0.15, H > 2.5)
    ax.axvline(0.15, color='red', linestyle='--', alpha=0.5, label='Basin boundary (d/n=0.15)')
    ax.axhline(2.5, color='blue', linestyle='--', alpha=0.5, label='Basin boundary (H=2.5)')

    ax.set_xlabel('Normalized Hamming Distance (d/n)')
    ax.set_ylabel('Violation Entropy (H)')
    ax.set_title('d/n vs Entropy Correlation')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_quartile_boxplot(dn_values: List[float], entropy_values: List[float], save_path: str):
    """Box plots for d/n and entropy distributions."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # d/n box plot
    axes[0].boxplot([dn_values], labels=['d/n'])
    axes[0].set_ylabel('Value')
    axes[0].set_title('d/n Distribution')
    axes[0].grid(True, alpha=0.3)

    # Entropy box plot
    axes[1].boxplot([entropy_values], labels=['H'])
    axes[1].set_ylabel('Value')
    axes[1].set_title('Entropy Distribution')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def generate_all_figures(metrics: Dict[str, float], output_dir: str):
    """Generate all required figures."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    dn_values = metrics.get('dn_values', [])
    entropy_values = metrics.get('entropy_values', [])

    # Mandatory figure
    plot_gate_comparison(metrics, str(output_path / 'gate_comparison.png'))

    # Additional figures
    if dn_values:
        plot_dn_distribution(dn_values, str(output_path / 'dn_distribution.png'))
    if entropy_values:
        plot_entropy_distribution(entropy_values, str(output_path / 'entropy_distribution.png'))
    if dn_values and entropy_values:
        plot_dn_vs_entropy_scatter(dn_values, entropy_values, str(output_path / 'dn_entropy_scatter.png'))
        plot_quartile_boxplot(dn_values, entropy_values, str(output_path / 'quartile_boxplot.png'))

    print(f"✅ Generated {5 if dn_values else 1} figures in {output_dir}")
