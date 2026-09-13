"""Stratified quartile analysis for difficulty-controlled coupling."""

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency


def bin_by_quartiles(
    df: pd.DataFrame,
    difficulty_col: str = 'difficulty_score',
    n_quartiles: int = 4
) -> pd.DataFrame:
    """Bin instances into difficulty quartiles.

    Args:
        df: DataFrame with difficulty_score column
        difficulty_col: Name of difficulty column
        n_quartiles: Number of quartiles (default 4)

    Returns:
        df with added 'quartile' column (values: 0, 1, 2, 3)
    """
    df = df.copy()
    df['quartile'] = pd.qcut(df[difficulty_col], q=n_quartiles, labels=False, duplicates='drop')
    return df


def compute_phi_coefficient(labels_d1: np.ndarray, labels_d2: np.ndarray) -> tuple[float, float]:
    """Compute phi coefficient from 2x2 contingency table.

    Args:
        labels_d1: [N] binary array (dimension 1)
        labels_d2: [N] binary array (dimension 2)

    Returns:
        (phi_coefficient, p_value)
    """
    contingency = pd.crosstab(labels_d1, labels_d2)
    chi2, p_value, dof, _ = chi2_contingency(contingency)
    n = len(labels_d1)
    phi = np.sqrt(chi2 / n) if n > 0 else 0.0
    return phi, p_value


def compute_quartile_phi(
    df: pd.DataFrame,
    dim1: str,
    dim2: str,
    quartile_col: str = 'quartile'
) -> pd.DataFrame:
    """Compute phi coefficient within each quartile.

    Args:
        df: DataFrame with dimensions and quartile column
        dim1, dim2: Dimension names
        quartile_col: Name of quartile column

    Returns:
        DataFrame with columns [quartile, phi, p_value, n_samples]
    """
    results = []
    for quartile in sorted(df[quartile_col].dropna().unique()):
        subset = df[df[quartile_col] == quartile]
        phi, p_value = compute_phi_coefficient(subset[dim1].values, subset[dim2].values)
        results.append({
            'quartile': int(quartile),
            'phi': phi,
            'p_value': p_value,
            'n_samples': len(subset)
        })
    return pd.DataFrame(results)


def validate_persistence(
    quartile_results: pd.DataFrame,
    threshold: float = 0.25,
    min_quartiles: int = 3
) -> bool:
    """Check if coupling persists across quartiles.

    Args:
        quartile_results: DataFrame with phi column
        threshold: Min phi threshold
        min_quartiles: Min number of quartiles where phi >= threshold

    Returns:
        True if phi >= threshold in >= min_quartiles quartiles
    """
    passing_quartiles = (quartile_results['phi'] >= threshold).sum()
    return passing_quartiles >= min_quartiles


def compare_validation_methods(
    partial_results: pd.DataFrame,
    quartile_results: pd.DataFrame,
    threshold: float = 0.25
) -> dict:
    """Compare partial correlation vs stratified results.

    Args:
        partial_results: DataFrame with partial_r column
        quartile_results: DataFrame with quartile phi results
        threshold: Min threshold for both methods

    Returns:
        {
            'agreement': list of (dim1, dim2) pairs where both methods agree,
            'partial_only': pairs passing partial threshold only,
            'quartile_only': pairs passing quartile persistence only
        }
    """
    agreement = []
    partial_only = []
    quartile_only = []

    for _, row in partial_results.iterrows():
        dim_pair = (row['dim1'], row['dim2'])
        partial_pass = abs(row['partial_r']) >= threshold

        # Check quartile persistence for this pair
        pair_quartiles = quartile_results[
            (quartile_results['dim1'] == row['dim1']) &
            (quartile_results['dim2'] == row['dim2'])
        ]
        quartile_pass = validate_persistence(pair_quartiles, threshold)

        if partial_pass and quartile_pass:
            agreement.append(dim_pair)
        elif partial_pass:
            partial_only.append(dim_pair)
        elif quartile_pass:
            quartile_only.append(dim_pair)

    return {
        'agreement': agreement,
        'partial_only': partial_only,
        'quartile_only': quartile_only
    }
