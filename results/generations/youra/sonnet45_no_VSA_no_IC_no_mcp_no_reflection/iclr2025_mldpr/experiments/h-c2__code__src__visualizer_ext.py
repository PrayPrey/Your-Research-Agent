"""Extended visualization for h-c2 dispersion analysis."""

import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict
import numpy as np


def plot_std_dev_bars(
    results: Dict[str, dict],
    threshold: float,
    output_path: str
) -> None:
    """
    Bar chart with 30% threshold line.

    Args:
        results: {benchmark: {'std_dev_pct': 0.35, 'n': 15}}
        threshold: gate threshold (0.30)
        output_path: save path (PNG)
    """
    benchmarks = list(results.keys())
    std_devs = [(r.get('std_dev_pct') or 0) * 100 for r in results.values()]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(benchmarks, std_devs, alpha=0.7, edgecolor='black', color='steelblue')

    # Color bars that pass threshold
    for i, (b, r) in enumerate(results.items()):
        if r.get('gate_pass', False):
            bars[i].set_color('green')
            bars[i].set_alpha(0.8)

    plt.axhline(threshold * 100, color='red', linestyle='--',
                label=f'Gate Threshold ({threshold*100:.0f}%)', linewidth=2)
    plt.xlabel('Benchmark', fontsize=12)
    plt.ylabel('Standard Deviation (%)', fontsize=12)
    plt.title('Low-Confidence Response Dispersion\n(Saturation Year Estimates)',
              fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3, axis='y')

    # Add sample size annotations
    for i, (b, r) in enumerate(results.items()):
        n = r.get('n', 0)
        y_pos = r.get('std_dev_pct', 0) * 100 + 2
        plt.text(i, y_pos, f'n={n}', ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_confidence_stratification(
    df: pd.DataFrame,
    output_path: str
) -> None:
    """
    Box plot comparing std dev across confidence bins (1, 2, 3, 4, 5).

    Args:
        df: full survey data (all confidence levels)
        output_path: save path (PNG)
    """
    # Calculate decimal years
    df['year_decimal'] = df['saturation_year'] + df['saturation_month'] / 12.0

    # Group by benchmark and confidence
    grouped = df.groupby(['benchmark', 'confidence'])['year_decimal'].apply(list).reset_index()

    # Prepare data for box plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    benchmarks = ['ImageNet', 'GLUE', 'SQuAD']

    for idx, benchmark in enumerate(benchmarks):
        ax = axes[idx]
        subset = grouped[grouped['benchmark'] == benchmark]

        # Create box plot data
        data_by_conf = []
        labels = []
        for conf in [1, 2, 3, 4, 5]:
            conf_data = subset[subset['confidence'] == conf]['year_decimal']
            if len(conf_data) > 0:
                data_by_conf.append(conf_data.iloc[0])
                labels.append(str(conf))

        if data_by_conf:
            bp = ax.boxplot(data_by_conf, labels=labels, patch_artist=True)

            # Color low-confidence (<3) differently
            for i, box in enumerate(bp['boxes']):
                if i < 2:  # confidence 1, 2
                    box.set_facecolor('lightcoral')
                else:
                    box.set_facecolor('lightblue')

        ax.set_title(f'{benchmark}', fontweight='bold')
        ax.set_xlabel('Confidence Score')
        if idx == 0:
            ax.set_ylabel('Saturation Year (Decimal)')
        ax.grid(True, alpha=0.3, axis='y')

    plt.suptitle('Temporal Dispersion by Confidence Level', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_sample_sizes(
    results: Dict[str, dict],
    min_n: int,
    output_path: str
) -> None:
    """
    Bar chart showing sample sizes with threshold line.

    Args:
        results: {benchmark: metrics_dict}
        min_n: minimum sample size threshold (10)
        output_path: save path (PNG)
    """
    benchmarks = list(results.keys())
    sample_sizes = [r.get('n', 0) for r in results.values()]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(benchmarks, sample_sizes, alpha=0.7, edgecolor='black', color='steelblue')

    # Color bars below threshold
    for i, n in enumerate(sample_sizes):
        if n < min_n:
            bars[i].set_color('red')
            bars[i].set_alpha(0.6)

    plt.axhline(min_n, color='orange', linestyle='--',
                label=f'Min Sample Size (n={min_n})', linewidth=2)
    plt.xlabel('Benchmark', fontsize=12)
    plt.ylabel('Sample Size (n)', fontsize=12)
    plt.title('Low-Confidence Response Sample Sizes', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3, axis='y')

    # Add value annotations
    for i, n in enumerate(sample_sizes):
        plt.text(i, n + 1, f'{n}', ha='center', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_distribution_faceted(
    df: pd.DataFrame,
    output_path: str
) -> None:
    """
    Histogram of saturation year estimates faceted by benchmark.

    Args:
        df: low-confidence responses with year_decimal
        output_path: save path (PNG)
    """
    df['year_decimal'] = df['saturation_year'] + df['saturation_month'] / 12.0

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    benchmarks = ['ImageNet', 'GLUE', 'SQuAD']

    for idx, benchmark in enumerate(benchmarks):
        ax = axes[idx]
        subset = df[df['benchmark'] == benchmark]

        if len(subset) > 0:
            ax.hist(subset['year_decimal'], bins=10, alpha=0.7, edgecolor='black', color='steelblue')
            ax.axvline(subset['year_decimal'].mean(), color='red', linestyle='--',
                      label=f'Mean: {subset["year_decimal"].mean():.2f}', linewidth=2)
            ax.set_title(f'{benchmark} (n={len(subset)})', fontweight='bold')
            ax.set_xlabel('Saturation Year (Decimal)')
            if idx == 0:
                ax.set_ylabel('Frequency')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3, axis='y')

    plt.suptitle('Low-Confidence Response Distribution', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")
