"""Visualization functions for consensus data."""

import matplotlib.pyplot as plt
from typing import Dict, Tuple
import pandas as pd


def plot_date_distribution(
    df: pd.DataFrame,
    benchmark: str,
    modal_date: Tuple[int, int],
    output_path: str
) -> None:
    """
    Histogram of saturation dates with modal marker.
    Args:
        df: subset for one benchmark
        benchmark: name for title
        modal_date: (year, month) for vertical line
        output_path: save path (PNG)

    Plot:
        - X-axis: year.month (e.g., 2019.5 for June 2019)
        - Y-axis: count of responses
        - Vertical red line at modal_date
        - Title: "{benchmark} Saturation Date Distribution"
    """
    # Convert to decimal year
    df = df.copy()
    df['decimal_year'] = df['saturation_year'] + df['saturation_month'] / 12.0

    plt.figure(figsize=(10, 6))
    plt.hist(df['decimal_year'], bins=20, edgecolor='black', alpha=0.7)

    # Modal date marker
    modal_decimal = modal_date[0] + modal_date[1] / 12.0
    plt.axvline(modal_decimal, color='red', linestyle='--', linewidth=2, label=f'Modal: {modal_date[0]}-{modal_date[1]:02d}')

    plt.xlabel('Saturation Date (Year)')
    plt.ylabel('Response Count')
    plt.title(f'{benchmark} Saturation Date Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_agreement_bars(results: Dict[str, dict], output_path: str) -> None:
    """
    Bar chart: agreement rate per benchmark with 95% CI error bars.
    Args:
        results: {benchmark: {"agreement_rate": 78.0, "ci_lower": 73.5, "ci_upper": 82.1}}
        output_path: save path (PNG)

    Plot:
        - X-axis: benchmark names
        - Y-axis: agreement rate (%)
        - Error bars: ci_lower to ci_upper
        - Horizontal line at 70% threshold
    """
    benchmarks = list(results.keys())
    agreement_rates = [results[b]['agreement_rate'] for b in benchmarks]
    ci_lower = [results[b]['ci_lower'] for b in benchmarks]
    ci_upper = [results[b]['ci_upper'] for b in benchmarks]

    # Calculate error bar sizes
    errors = [[agreement_rates[i] - ci_lower[i], ci_upper[i] - agreement_rates[i]] for i in range(len(benchmarks))]
    errors = list(zip(*errors))

    plt.figure(figsize=(10, 6))
    plt.bar(benchmarks, agreement_rates, alpha=0.7, edgecolor='black')
    plt.errorbar(benchmarks, agreement_rates, yerr=errors, fmt='none', ecolor='black', capsize=5)

    # Threshold line
    plt.axhline(70, color='red', linestyle='--', linewidth=2, label='70% Threshold')

    plt.xlabel('Benchmark')
    plt.ylabel('Agreement Rate (%)')
    plt.title('Expert Consensus Agreement Rates')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_kappa_comparison(results: Dict[str, dict], output_path: str) -> None:
    """
    Bar chart: Fleiss kappa per benchmark.
    Args:
        results: {benchmark: {"fleiss_kappa": 0.71}}
        output_path: save path (PNG)

    Plot:
        - X-axis: benchmark names
        - Y-axis: kappa (0-1)
        - Horizontal lines at 0.6 (substantial), 0.8 (almost perfect)
    """
    benchmarks = list(results.keys())
    kappas = [results[b]['fleiss_kappa'] for b in benchmarks]

    plt.figure(figsize=(10, 6))
    plt.bar(benchmarks, kappas, alpha=0.7, edgecolor='black')

    # Threshold lines
    plt.axhline(0.6, color='orange', linestyle='--', linewidth=2, label='Substantial (κ=0.6)')
    plt.axhline(0.8, color='green', linestyle='--', linewidth=2, label='Almost Perfect (κ=0.8)')

    plt.xlabel('Benchmark')
    plt.ylabel("Fleiss' Kappa")
    plt.title("Chance-Adjusted Agreement (Fleiss' Kappa)")
    plt.legend()
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
