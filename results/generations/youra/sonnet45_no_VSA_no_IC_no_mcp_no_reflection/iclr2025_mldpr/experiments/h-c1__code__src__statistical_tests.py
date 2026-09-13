"""Bootstrap and permutation tests for statistical validation."""

from typing import Tuple
import numpy as np
import pandas as pd
from src.metrics import calculate_modal_date, calculate_agreement_rate


def bootstrap_confidence_interval(
    df: pd.DataFrame,
    modal_date: Tuple[int, int],
    window_months: int = 12,
    n_iterations: int = 1000,
    random_seed: int = 42
) -> Tuple[float, float]:
    """
    95% CI for agreement rate via bootstrap.
    Args:
        df: DataFrame with [saturation_year, saturation_month]
        modal_date: (year, month)
        window_months: tolerance
        n_iterations: bootstrap samples
        random_seed: for reproducibility
    Returns:
        (ci_lower, ci_upper) as percentages

    Algorithm:
        1. Set random seed
        2. For i in 1..n_iterations:
            a. Resample df with replacement (same size as original)
            b. Compute agreement_rate for resampled data
            c. Store rate
        3. ci_lower = 2.5th percentile of rates
        4. ci_upper = 97.5th percentile of rates
    """
    np.random.seed(random_seed)
    agreement_rates = []

    for _ in range(n_iterations):
        # Resample with replacement
        sample = df.sample(n=len(df), replace=True)
        rate = calculate_agreement_rate(sample, modal_date, window_months)
        agreement_rates.append(rate)

    ci_lower = np.percentile(agreement_rates, 2.5)
    ci_upper = np.percentile(agreement_rates, 97.5)
    return ci_lower, ci_upper


def permutation_test(
    df: pd.DataFrame,
    observed_agreement: float,
    window_months: int = 12,
    n_permutations: int = 1000,
    random_seed: int = 42
) -> float:
    """
    Test if agreement > random chance (null hypothesis).
    Args:
        df: DataFrame with [saturation_year, saturation_month]
        observed_agreement: actual agreement %
        window_months: tolerance
        n_permutations: shuffle iterations
        random_seed: for reproducibility
    Returns:
        p_value: proportion of permutations with agreement >= observed

    Algorithm:
        1. Set random seed
        2. For i in 1..n_permutations:
            a. Shuffle dates randomly
            b. Compute modal_date from shuffled data
            c. Compute agreement_rate for shuffled data
            d. Store rate
        3. p_value = (# permuted rates >= observed_agreement) / n_permutations

    Expected null agreement: <30% (random chance)
    Threshold: p<0.05 for significance
    """
    np.random.seed(random_seed)
    permuted_rates = []

    for _ in range(n_permutations):
        # Shuffle years and months independently
        shuffled = df.copy()
        shuffled['saturation_year'] = np.random.permutation(df['saturation_year'].values)
        shuffled['saturation_month'] = np.random.permutation(df['saturation_month'].values)

        # Compute modal date and agreement for shuffled data
        modal = calculate_modal_date(shuffled)
        rate = calculate_agreement_rate(shuffled, modal, window_months)
        permuted_rates.append(rate)

    # p-value: proportion of permuted rates >= observed
    p_value = np.sum(np.array(permuted_rates) >= observed_agreement) / n_permutations
    return p_value
