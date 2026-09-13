"""Correlation analysis between task features and error modes."""
import pandas as pd
from scipy.stats import pearsonr
from typing import Tuple, Dict


def analyze_correlation(
    features_df: pd.DataFrame,
    errors_df: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, Tuple[float, float]]]:
    """Merge and compute correlations. Returns (corr_matrix, p_values_dict)."""
    merged = pd.merge(features_df, errors_df, on='problem_id')

    feature_cols = ['ast_depth', 'function_count', 'control_flow_density', 'complexity_score']
    error_cols = ['syntax_pct', 'type_pct', 'semantic_pct']
    all_cols = feature_cols + error_cols
    corr_matrix = merged[all_cols].corr(method='pearson')

    p_values = {}
    for feat in feature_cols:
        for err in error_cols:
            r, p = pearsonr(merged[feat], merged[err])
            p_values[f'{feat}_vs_{err}'] = (r, p)

    return corr_matrix, p_values
