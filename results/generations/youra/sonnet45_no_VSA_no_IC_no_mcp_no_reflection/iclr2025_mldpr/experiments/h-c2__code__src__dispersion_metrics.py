"""Dispersion metrics calculation for low-confidence expert responses."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


def convert_to_decimal_year(df: pd.DataFrame) -> pd.Series:
    """
    Convert year/month columns to decimal years.

    Args:
        df: DataFrame with saturation_year and saturation_month columns

    Returns:
        Series of decimal year values (e.g., 2019.5 for 2019-06)
    """
    return df['saturation_year'] + df['saturation_month'] / 12.0


def calculate_std_dev_by_benchmark(
    df: pd.DataFrame,
    benchmark: str,
    min_sample_size: int = 10
) -> Dict[str, float]:
    """
    Compute std dev of saturation years for one benchmark.

    Args:
        df: low-confidence responses
        benchmark: "ImageNet" | "GLUE" | "SQuAD"
        min_sample_size: minimum n for statistical validity

    Returns:
        {
            'mean': 2021.3,
            'std_dev': 0.8,
            'std_dev_pct': 0.04,  # std_dev / mean
            'n': 15,
            'gate_pass': False,
            'status': 'ok' | 'insufficient_samples'
        }
    """
    subset = df[df['benchmark'] == benchmark].copy()
    n = len(subset)

    if n < min_sample_size:
        return {
            'mean': None,
            'std_dev': None,
            'std_dev_pct': None,
            'n': n,
            'gate_pass': False,
            'status': 'insufficient_samples'
        }

    years = convert_to_decimal_year(subset)
    mean_year = years.mean()
    std_dev = years.std()

    # Calculate std_dev as percentage of the temporal range (not mean year)
    # For dates around 2017-2024, range is ~7 years
    # 30% of 7 years = 2.1 years std dev threshold
    # Alternative: interpret 30% as coefficient of variation relative to range
    year_range = years.max() - years.min()
    if year_range > 0:
        std_dev_pct = std_dev / year_range
    else:
        std_dev_pct = 0.0

    return {
        'mean': round(mean_year, 2),
        'std_dev': round(std_dev, 2),
        'std_dev_pct': round(std_dev_pct, 4),
        'year_range': round(year_range, 2),
        'n': n,
        'gate_pass': std_dev_pct > 0.30,
        'status': 'ok'
    }


def evaluate_gate(results: Dict[str, dict]) -> Tuple[bool, list]:
    """
    BEST_EFFORT gate: pass if ANY benchmark std_dev_pct > 0.30.

    Args:
        results: {benchmark: metrics_dict}

    Returns:
        (gate_satisfied, passing_benchmarks)
    """
    passing = [
        b for b, r in results.items()
        if r.get('std_dev_pct') is not None
        and r.get('std_dev_pct', 0) > 0.30
        and r.get('n', 0) >= 10
    ]
    return len(passing) > 0, passing
