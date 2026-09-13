"""Correlation analysis and gate decision logic."""
from scipy.stats import pearsonr, spearmanr
import pandas as pd
import numpy as np

def compute_pearson(x: np.ndarray, y: np.ndarray) -> tuple:
    """Returns: (r, p_value)."""
    return pearsonr(x, y)

def compute_spearman(x: np.ndarray, y: np.ndarray) -> tuple:
    """Returns: (rho, p_value)."""
    return spearmanr(x, y)

def correlate_all_components(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """
    Correlate Q(D) components with info_density.

    Args:
        metrics_df: DataFrame with columns ['dedup', 'diversity', 'perplexity',
                    'efficiency', 'info_density'], 12 rows

    Returns:
        results_df: columns ['component', 'pearson_r', 'pearson_p',
                    'spearman_rho', 'spearman_p']
    """
    components = ['dedup', 'diversity', 'perplexity', 'efficiency']
    results = []

    for component in components:
        x = metrics_df[component].values
        y = metrics_df['info_density'].values

        r, p_pearson = pearsonr(x, y)
        rho, p_spearman = spearmanr(x, y)

        results.append({
            'component': component,
            'pearson_r': r,
            'pearson_p': p_pearson,
            'spearman_rho': rho,
            'spearman_p': p_spearman
        })

    return pd.DataFrame(results)

def check_gate(correlation_results: pd.DataFrame, r_threshold: float = 0.5, p_threshold: float = 0.01) -> str:
    """MUST_WORK gate decision logic."""
    passing_components = 0

    for _, row in correlation_results.iterrows():
        r = row['pearson_r']
        p = row['pearson_p']
        rho = row['spearman_rho']

        if r > r_threshold and p < p_threshold and rho > r_threshold:
            passing_components += 1

    if passing_components >= 4:
        return "PASS"
    elif passing_components >= 2:
        return "PARTIAL"
    else:
        return "FAIL"

def save_results(results: pd.DataFrame, path: str):
    """Save correlation results to CSV."""
    results.to_csv(path, index=False)
