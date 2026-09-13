"""Partial correlation analysis controlling for difficulty."""

import pandas as pd
import pingouin as pg


def compute_partial_correlation(
    df: pd.DataFrame,
    dim1: str,
    dim2: str,
    covar: str = 'difficulty_score'
) -> tuple[float, float, tuple[float, float]]:
    """Compute partial correlation controlling for difficulty.

    Args:
        df: DataFrame with binary dimension columns + difficulty_score
        dim1, dim2: Dimension names
        covar: Covariate column name

    Returns:
        (partial_r, p_value, (ci_lower, ci_upper))
    """
    result = pg.partial_corr(data=df, x=dim1, y=dim2, covar=covar)

    partial_r = result['r'].values[0]
    p_value = result['p_val'].values[0]
    ci_lower = result['CI95'].values[0][0]
    ci_upper = result['CI95'].values[0][1]

    return (partial_r, p_value, (ci_lower, ci_upper))


def analyze_all_pairs(
    df: pd.DataFrame,
    dimension_pairs: list[tuple[str, str]]
) -> pd.DataFrame:
    """Compute partial correlation for all dimension pairs.

    Args:
        df: DataFrame with all dimensions + difficulty_score
        dimension_pairs: List of (dim1, dim2) tuples (6 pairs from h-e1)

    Returns:
        DataFrame with columns [dim1, dim2, partial_r, p_value, ci_lower, ci_upper]
    """
    results = []
    for dim1, dim2 in dimension_pairs:
        partial_r, p_value, (ci_lower, ci_upper) = compute_partial_correlation(df, dim1, dim2)
        results.append({
            'dim1': dim1,
            'dim2': dim2,
            'partial_r': partial_r,
            'p_value': p_value,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper
        })
    return pd.DataFrame(results)
