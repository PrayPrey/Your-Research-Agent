"""Visualization module for H-M3 Bootstrap CI Stability.

Task: T-EPIC-06 (A-6: Visualization)
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict
from pathlib import Path


def plot_bootstrap_distributions(
    conditions_data: Dict[str, np.ndarray],
    bootstrap_results: Dict[str, Dict[str, float]],
    config,
    save_path: str
) -> None:
    """4 subplots: histograms with CI bounds and threshold marker.

    Args:
        conditions_data: Dictionary mapping condition names to test accuracy arrays
        bootstrap_results: Dictionary of bootstrap analysis results
        config: BootstrapConfig instance
        save_path: Path to save figure
    """
    fig, axes = plt.subplots(2, 2, figsize=config.figsize_distributions)
    fig.suptitle('Bootstrap Variance Distributions with 95% CI', fontsize=16, fontweight='bold')

    conditions = list(bootstrap_results.keys())

    for idx, (ax, condition) in enumerate(zip(axes.flat, conditions)):
        data = conditions_data[condition]
        metrics = bootstrap_results[condition]

        # Regenerate bootstrap distribution for visualization
        np.random.seed(config.random_seed)
        n = len(data)
        variance_estimates = []
        for _ in range(config.n_resamples):
            bootstrap_sample = np.random.choice(data, size=n, replace=True)
            variance_estimates.append(np.var(bootstrap_sample, ddof=1))
        variance_estimates = np.array(variance_estimates)

        # Plot histogram
        ax.hist(variance_estimates, bins=50, alpha=0.7, color='skyblue', edgecolor='black')

        # Add CI bounds
        ci_lower = metrics['ci_lower']
        ci_upper = metrics['ci_upper']
        variance_point = metrics['variance_point']

        ax.axvline(variance_point, color='red', linestyle='-', linewidth=2, label='Point Estimate')
        ax.axvline(ci_lower, color='blue', linestyle='--', linewidth=2, label='CI Lower (2.5%)')
        ax.axvline(ci_upper, color='blue', linestyle='--', linewidth=2, label='CI Upper (97.5%)')

        # Color-code title based on gate result
        ci_width_pct = metrics['ci_width_pct']
        passed = ci_width_pct <= config.ci_width_threshold_pct
        title_color = 'green' if passed else 'red'

        ax.set_title(
            f"{condition}\nCI Width: {ci_width_pct:.2f}% ({'PASS' if passed else 'FAIL'})",
            fontsize=12,
            fontweight='bold',
            color=title_color
        )
        ax.set_xlabel('Variance', fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.dpi)
    plt.close()

    print(f"✓ Bootstrap distributions figure saved to {save_path}")


def plot_ci_width_comparison(
    bootstrap_results: Dict[str, Dict[str, float]],
    threshold: float,
    config,
    save_path: str
) -> None:
    """Bar chart: CI width % vs 50% threshold (color-coded pass/fail).

    Args:
        bootstrap_results: Dictionary of bootstrap analysis results
        threshold: CI width threshold percentage
        config: BootstrapConfig instance
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=config.figsize_ci_width)

    conditions = list(bootstrap_results.keys())
    ci_widths = [bootstrap_results[c]['ci_width_pct'] for c in conditions]

    # Color-code bars based on pass/fail
    colors = ['green' if w <= threshold else 'red' for w in ci_widths]

    # Bar chart
    bars = ax.bar(range(len(conditions)), ci_widths, color=colors, alpha=0.7, edgecolor='black')

    # Threshold line
    ax.axhline(threshold, color='black', linestyle='--', linewidth=2, label=f'Threshold ({threshold}%)')

    # Labels and formatting
    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels(conditions, rotation=45, ha='right')
    ax.set_ylabel('CI Width (%)', fontsize=12, fontweight='bold')
    ax.set_title('Bootstrap CI Width Comparison Across Conditions', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, axis='y', alpha=0.3)

    # Add value labels on bars
    for bar, width in zip(bars, ci_widths):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 1,
                f'{width:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.dpi)
    plt.close()

    print(f"✓ CI width comparison figure saved to {save_path}")


def plot_variance_vs_ci_width(
    bootstrap_results: Dict[str, Dict[str, float]],
    config,
    save_path: str
) -> None:
    """Scatter: variance point estimate vs CI width %.

    Args:
        bootstrap_results: Dictionary of bootstrap analysis results
        config: BootstrapConfig instance
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=config.figsize_scatter)

    conditions = list(bootstrap_results.keys())
    variances = [bootstrap_results[c]['variance_point'] for c in conditions]
    ci_widths = [bootstrap_results[c]['ci_width_pct'] for c in conditions]

    # Color-code points based on pass/fail
    colors = ['green' if w <= config.ci_width_threshold_pct else 'red' for w in ci_widths]

    # Scatter plot
    ax.scatter(variances, ci_widths, c=colors, s=200, alpha=0.7, edgecolor='black', linewidth=2)

    # Add labels for each point
    for condition, var, width in zip(conditions, variances, ci_widths):
        ax.annotate(condition, (var, width), fontsize=9, ha='right', va='bottom')

    # Threshold line
    ax.axhline(config.ci_width_threshold_pct, color='black', linestyle='--', linewidth=2,
               label=f'Threshold ({config.ci_width_threshold_pct}%)')

    # Labels and formatting
    ax.set_xlabel('Variance Point Estimate', fontsize=12, fontweight='bold')
    ax.set_ylabel('CI Width (%)', fontsize=12, fontweight='bold')
    ax.set_title('Variance vs CI Width Scatter Plot', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.dpi)
    plt.close()

    print(f"✓ Variance vs CI width scatter figure saved to {save_path}")


def generate_all_figures(
    conditions_data: Dict[str, np.ndarray],
    bootstrap_results: Dict[str, Dict[str, float]],
    config
) -> None:
    """Generate all visualization figures.

    Args:
        conditions_data: Dictionary mapping condition names to test accuracy arrays
        bootstrap_results: Dictionary of bootstrap analysis results
        config: BootstrapConfig instance
    """
    print("\n" + "=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)

    # Figure 1: Bootstrap distributions
    fig1_path = f"{config.figures_dir}/bootstrap_distributions.png"
    plot_bootstrap_distributions(conditions_data, bootstrap_results, config, fig1_path)

    # Figure 2: CI width comparison
    fig2_path = f"{config.figures_dir}/ci_width_comparison.png"
    plot_ci_width_comparison(bootstrap_results, config.ci_width_threshold_pct, config, fig2_path)

    # Figure 3: Variance vs CI width
    fig3_path = f"{config.figures_dir}/variance_vs_ci_width.png"
    plot_variance_vs_ci_width(bootstrap_results, config, fig3_path)

    print("=" * 60)
    print(f"✓ All visualizations completed ({config.figures_dir}/)")
    print("=" * 60)
