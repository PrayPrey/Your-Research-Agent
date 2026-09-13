"""Visualization generation for variance measurement results."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict
from pathlib import Path

# Set seaborn style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


def plot_gate_metrics_comparison(
    variance_summary: Dict[str, Dict[str, float]],
    threshold: float,
    save_path: str
) -> None:
    """Bar chart: target vs actual variance with CI error bars.

    Args:
        variance_summary: Variance metrics per condition
        threshold: Target threshold (0.3%)
        save_path: Path to save figure
    """
    conditions = list(variance_summary.keys())
    variances = [variance_summary[c]["variance"] for c in conditions]
    ci_lower = [variance_summary[c]["ci_lower"] for c in conditions]
    ci_upper = [variance_summary[c]["ci_upper"] for c in conditions]

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(conditions))
    width = 0.35

    # Target threshold bars
    ax.bar(x - width/2, [threshold] * len(conditions), width, label='Target (≥0.3%)', color='lightcoral')

    # Actual variance bars with error bars (use absolute values to avoid negative)
    yerr_lower = [abs(variances[i] - ci_lower[i]) for i in range(len(conditions))]
    yerr_upper = [abs(ci_upper[i] - variances[i]) for i in range(len(conditions))]
    ax.bar(x + width/2, variances, width, label='Actual Variance',
           yerr=[yerr_lower, yerr_upper], capsize=5, color='steelblue')

    ax.set_xlabel('Condition (Dataset, Architecture)')
    ax.set_ylabel('Test Accuracy Variance (%)')
    ax.set_title('Gate Metrics: Target vs Actual Variance')
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, rotation=45, ha='right')
    ax.legend()
    ax.axhline(y=threshold, color='r', linestyle='--', alpha=0.5, label=f'Threshold ({threshold}%)')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_variance_by_condition(variance_summary: Dict[str, Dict[str, float]], save_path: str) -> None:
    """Bar chart: variance for all 4 conditions.

    Args:
        variance_summary: Variance metrics per condition
        save_path: Path to save figure
    """
    conditions = list(variance_summary.keys())
    variances = [variance_summary[c]["variance"] for c in conditions]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(conditions, variances, color='steelblue', edgecolor='black')

    ax.set_xlabel('Condition (Dataset, Architecture)')
    ax.set_ylabel('Test Accuracy Variance (%²)')
    ax.set_title('Variance by Condition (30 seeds per condition)')
    ax.set_xticklabels(conditions, rotation=45, ha='right')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}%', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_accuracy_distributions(results_df: pd.DataFrame, save_path: str) -> None:
    """2×2 histogram grid for test accuracies.

    Args:
        results_df: Experiment results DataFrame
        save_path: Path to save figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Test Accuracy Distributions (30 seeds each)', fontsize=14)

    conditions = results_df.groupby(['dataset', 'architecture'])

    for idx, ((dataset, arch), group) in enumerate(conditions):
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]

        ax.hist(group['test_accuracy'], bins=20, edgecolor='black', color='steelblue', alpha=0.7)
        ax.set_xlabel('Test Accuracy (%)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'{dataset}, {arch}')
        ax.axvline(group['test_accuracy'].mean(), color='red', linestyle='--',
                   label=f'Mean: {group["test_accuracy"].mean():.2f}%')
        ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_cv_comparison(variance_summary: Dict[str, Dict[str, float]], save_path: str) -> None:
    """Bar chart: coefficient of variation.

    Args:
        variance_summary: Variance metrics per condition
        save_path: Path to save figure
    """
    conditions = list(variance_summary.keys())
    cv_values = [variance_summary[c]["cv_percent"] for c in conditions]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(conditions, cv_values, color='coral', edgecolor='black')

    ax.set_xlabel('Condition (Dataset, Architecture)')
    ax.set_ylabel('Coefficient of Variation (%)')
    ax.set_title('CV% Comparison Across Conditions')
    ax.set_xticklabels(conditions, rotation=45, ha='right')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}%', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_accuracy_ranges(variance_summary: Dict[str, Dict[str, float]], save_path: str) -> None:
    """Error bar plot showing min/max/mean per condition.

    Args:
        variance_summary: Variance metrics per condition (must include min/max)
        save_path: Path to save figure
    """
    conditions = list(variance_summary.keys())
    means = [variance_summary[c]["mean"] for c in conditions]

    # Note: min/max would need to be added to variance_summary
    # For now, use CI bounds as proxy
    ci_lower = [variance_summary[c]["ci_lower"] for c in conditions]
    ci_upper = [variance_summary[c]["ci_upper"] for c in conditions]

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(conditions))
    yerr_lower = [means[i] - ci_lower[i] for i in range(len(conditions))]
    yerr_upper = [ci_upper[i] - means[i] for i in range(len(conditions))]

    ax.errorbar(x, means, yerr=[yerr_lower, yerr_upper], fmt='o',
                capsize=5, capthick=2, markersize=8, color='steelblue', label='Mean ± 95% CI')

    ax.set_xlabel('Condition (Dataset, Architecture)')
    ax.set_ylabel('Test Accuracy (%)')
    ax.set_title('Accuracy Ranges with 95% Confidence Intervals')
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def generate_all_figures(
    results_df: pd.DataFrame,
    variance_summary: Dict,
    threshold: float,
    figures_dir: str
) -> None:
    """Generate all 5 required figures.

    Args:
        results_df: Experiment results DataFrame
        variance_summary: Variance metrics per condition
        threshold: Variance threshold
        figures_dir: Directory to save figures
    """
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    print("Generating figures...")

    plot_gate_metrics_comparison(
        variance_summary, threshold,
        f"{figures_dir}/01_gate_metrics_comparison.png"
    )
    print("  ✓ Gate metrics comparison")

    plot_variance_by_condition(
        variance_summary,
        f"{figures_dir}/02_variance_by_condition.png"
    )
    print("  ✓ Variance by condition")

    plot_accuracy_distributions(
        results_df,
        f"{figures_dir}/03_accuracy_distributions.png"
    )
    print("  ✓ Accuracy distributions")

    plot_cv_comparison(
        variance_summary,
        f"{figures_dir}/04_cv_comparison.png"
    )
    print("  ✓ CV% comparison")

    plot_accuracy_ranges(
        variance_summary,
        f"{figures_dir}/05_accuracy_ranges.png"
    )
    print("  ✓ Accuracy ranges")

    print(f"All figures saved to {figures_dir}/")
