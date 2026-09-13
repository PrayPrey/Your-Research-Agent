"""Core statistical metrics for consensus measurement."""

from typing import Tuple
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.inter_rater import fleiss_kappa


def calculate_modal_date(df: pd.DataFrame) -> Tuple[int, int]:
    """
    Compute mode of (year, month) pairs. If tie, select earliest.
    Args:
        df: DataFrame with columns [saturation_year, saturation_month]
    Returns:
        (modal_year, modal_month)
    """
    date_counts = df.groupby(['saturation_year', 'saturation_month']).size()
    max_count = date_counts.max()
    modes = date_counts[date_counts == max_count].index.tolist()
    # Select earliest if tie
    modes.sort()
    return modes[0]


def calculate_agreement_rate(
    df: pd.DataFrame,
    modal_date: Tuple[int, int],
    window_months: int = 12
) -> float:
    """
    % of dates within ±window_months of modal_date.
    Args:
        df: DataFrame with [saturation_year, saturation_month]
        modal_date: (year, month)
        window_months: tolerance (default 12)
    Returns:
        agreement_rate (0-100%)

    Algorithm:
        1. Convert dates to months since epoch: m = year*12 + month
        2. modal_m = modal_year*12 + modal_month
        3. count dates where |m - modal_m| <= window_months
        4. agreement = count / total * 100
    """
    df = df.copy()
    df['months_since_epoch'] = df['saturation_year'] * 12 + df['saturation_month']
    modal_months = modal_date[0] * 12 + modal_date[1]

    df['within_window'] = abs(df['months_since_epoch'] - modal_months) <= window_months
    agreement = (df['within_window'].sum() / len(df)) * 100
    return agreement


def prepare_kappa_matrix(df: pd.DataFrame) -> np.ndarray:
    """
    Convert dates to N×K matrix for Fleiss kappa.
    Args:
        df: DataFrame with [saturation_year, saturation_month]
    Returns:
        matrix [n_items, n_categories] where matrix[i,j] = 1 if rater i selected category j, else 0

    Note: Treat year buckets as categories (2017-2024 = 8 categories).
    Each response is a separate rater (row), category is year bucket.
    """
    year_range = list(range(2017, 2025))
    n_categories = len(year_range)
    n_raters = len(df)

    # Create matrix: rows = raters, cols = categories
    matrix = np.zeros((n_raters, n_categories), dtype=int)

    for i, year in enumerate(df['saturation_year'].values):
        if year in year_range:
            idx = year_range.index(year)
            matrix[i, idx] = 1

    return matrix


def calculate_fleiss_kappa(df: pd.DataFrame) -> float:
    """
    Chance-adjusted agreement (manual calculation).
    Args:
        df: DataFrame with [saturation_year, saturation_month]
    Returns:
        kappa (0-1, can be negative if worse than chance)

    Algorithm:
        κ = (P̄ - P̄e) / (1 - P̄e)
        P̄ = mean observed agreement
        P̄e = expected agreement by chance
    """
    year_range = list(range(2017, 2025))
    n_raters = len(df)
    n_categories = len(year_range)

    # Count responses per category
    category_counts = [0] * n_categories
    for year in df['saturation_year'].values:
        if year in year_range:
            idx = year_range.index(year)
            category_counts[idx] += 1

    # All agree edge case
    if max(category_counts) == n_raters:
        return 1.0

    # Calculate P̄ (observed agreement)
    # For single subject (benchmark), P = sum(pi^2) where pi = proportion in category i
    p_observed = sum((count / n_raters) ** 2 for count in category_counts)

    # Calculate P̄e (expected agreement by chance)
    # For uniform distribution: 1/k where k = n_categories
    p_expected = 1.0 / n_categories

    # Kappa
    if p_expected == 1.0:
        return 1.0
    kappa = (p_observed - p_expected) / (1.0 - p_expected)
    return kappa
