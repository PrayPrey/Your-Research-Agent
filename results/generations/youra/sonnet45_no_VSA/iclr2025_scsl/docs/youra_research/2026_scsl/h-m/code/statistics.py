"""Statistical testing module for dose-response validation."""
from scipy.stats import spearmanr
import numpy as np
import pandas as pd
from typing import Dict


def compute_spearman_correlation(results_df: pd.DataFrame) -> Dict:
    """
    Test dose-response relationship (flip conditions only).

    Args:
        results_df: DataFrame with columns [condition, seed, asymmetric_acc]

    Returns:
        {rho: float, p_value: float, significant: bool, interpretation: str}
    """
    # Filter to flip conditions only (exclude rotation)
    flip_conditions = results_df[results_df['condition'].isin(['baseline', 'flip30', 'flip50', 'flip90'])]

    # Map conditions to flip probabilities
    prob_map = {'baseline': 0.0, 'flip30': 0.3, 'flip50': 0.5, 'flip90': 0.9}
    flip_conditions = flip_conditions.copy()
    flip_conditions['flip_prob'] = flip_conditions['condition'].map(prob_map)

    # Compute Spearman correlation (n=20: 4 conditions × 5 seeds)
    rho, p_value = spearmanr(flip_conditions['flip_prob'], flip_conditions['asymmetric_acc'])

    interpretation = ""
    if p_value < 0.05:
        if rho < -0.7:
            interpretation = "Strong negative monotonic relationship"
        elif rho < -0.4:
            interpretation = "Moderate negative monotonic relationship"
        else:
            interpretation = "Weak negative monotonic relationship"
    else:
        interpretation = "No significant monotonic relationship"

    return {
        'rho': float(rho),
        'p_value': float(p_value),
        'significant': bool(p_value < 0.05),
        'interpretation': interpretation
    }


def aggregate_seed_results(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate results across seeds.

    Args:
        results_df: DataFrame with columns [condition, seed, overall_acc, asymmetric_acc, symmetric_acc]

    Returns:
        DataFrame with columns [condition, mean_overall, std_overall, mean_asym, std_asym, mean_sym, std_sym, n]
    """
    aggregated = results_df.groupby('condition').agg({
        'overall_acc': ['mean', 'std', 'count'],
        'asymmetric_acc': ['mean', 'std'],
        'symmetric_acc': ['mean', 'std']
    }).reset_index()

    # Flatten column names
    aggregated.columns = [
        'condition',
        'mean_overall', 'std_overall', 'n',
        'mean_asym', 'std_asym',
        'mean_sym', 'std_sym'
    ]

    return aggregated


def test_rotation_control(results_df: pd.DataFrame) -> Dict:
    """
    Validate rotation shows no differential effect.

    Args:
        results_df: DataFrame with results

    Returns:
        {mean_diff: float, within_threshold: bool, passed: bool}
    """
    baseline = results_df[results_df['condition'] == 'baseline']['asymmetric_acc'].mean()
    rotation = results_df[results_df['condition'] == 'rotation']['asymmetric_acc'].mean()

    mean_diff = abs(rotation - baseline)
    within_threshold = mean_diff < 1.0  # <1% difference

    return {
        'baseline_asym': float(baseline),
        'rotation_asym': float(rotation),
        'mean_diff': float(mean_diff),
        'within_threshold': bool(within_threshold),
        'passed': bool(within_threshold)
    }
