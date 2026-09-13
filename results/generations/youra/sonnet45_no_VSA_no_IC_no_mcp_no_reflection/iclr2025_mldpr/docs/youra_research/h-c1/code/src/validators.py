"""Data quality validation checks."""

from typing import Tuple, Dict, List
import pandas as pd


def check_sample_size(df: pd.DataFrame, min_size: int = 30) -> Tuple[bool, Dict[str, int]]:
    """
    Verify >=min_size responses per benchmark.
    Args:
        df: filtered high-confidence df
        min_size: threshold (default 30)
    Returns:
        (all_pass, counts_dict)

    Example:
        all_pass=True, {"ImageNet": 42, "GLUE": 38, "SQuAD": 35}
    """
    counts = df['benchmark'].value_counts().to_dict()
    all_pass = all(count >= min_size for count in counts.values())
    return all_pass, counts


def check_domain_balance(
    df: pd.DataFrame,
    min_ratio: float = 0.4,
    max_ratio: float = 0.6
) -> Tuple[bool, Dict[str, float]]:
    """
    Check vision:NLP split in acceptable range.
    Args:
        df: full df (all benchmarks)
        min_ratio: min acceptable proportion (0.4 = 40%)
        max_ratio: max acceptable proportion (0.6 = 60%)
    Returns:
        (is_balanced, ratios_dict)

    Example:
        is_balanced=True, {"vision": 0.52, "nlp": 0.45, "other": 0.03}
    """
    domain_counts = df['domain'].value_counts()
    total = len(df)
    ratios = {domain: count / total for domain, count in domain_counts.items()}

    # Check if any domain exceeds max_ratio or falls below min_ratio
    is_balanced = all(min_ratio <= ratio <= max_ratio for ratio in ratios.values() if ratio > 0.1)
    return is_balanced, ratios


def check_date_validity(
    df: pd.DataFrame,
    min_year: int = 2017,
    max_year: int = 2024
) -> Tuple[bool, List[int]]:
    """
    Flag dates outside valid range.
    Args:
        df: df with saturation_year column
        min_year: earliest valid year
        max_year: latest valid year
    Returns:
        (all_valid, invalid_row_indices)
    """
    invalid_mask = (df['saturation_year'] < min_year) | (df['saturation_year'] > max_year)
    invalid_indices = df[invalid_mask].index.tolist()
    all_valid = len(invalid_indices) == 0
    return all_valid, invalid_indices
