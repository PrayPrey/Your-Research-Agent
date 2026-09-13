"""H-M5 Correlation: Period correlation, rolling correlation, Fisher z-test"""
import numpy as np
import pandas as pd
from scipy import stats
from config import CONFIG


def period_correlation(
    gini_df: pd.DataFrame, col_a: str, col_b: str,
    start: str = None, end: str = None
) -> tuple:
    """Pearson r between col_a, col_b in [start, end). Returns (r, n_obs)."""
    sub = gini_df.copy()

    if start is not None:
        sub = sub[sub.index >= pd.Timestamp(start)]
    if end is not None:
        sub = sub[sub.index < pd.Timestamp(end)]

    sub = sub[[col_a, col_b]].dropna()

    if len(sub) < 3:
        return np.nan, len(sub)

    r, _ = stats.pearsonr(sub[col_a], sub[col_b])
    return float(r), len(sub)


def rolling_correlation(
    gini_df: pd.DataFrame, col_a: str, col_b: str, window: int = None
) -> pd.Series:
    """Rolling Pearson correlation. Returns Series indexed like gini_df."""
    if window is None:
        window = CONFIG.rolling_window

    return gini_df[col_a].rolling(window, min_periods=3).corr(gini_df[col_b])


def fisher_z_test(r1: float, n1: int, r2: float, n2: int) -> tuple:
    """Fisher z-test comparing two correlations. Returns (z_stat, p_value)."""
    if np.isnan(r1) or np.isnan(r2):
        return np.nan, np.nan
    if n1 < 4 or n2 < 4:
        return np.nan, np.nan

    r1 = np.clip(r1, -0.9999, 0.9999)
    r2 = np.clip(r2, -0.9999, 0.9999)

    z1 = np.arctanh(r1)
    z2 = np.arctanh(r2)

    se = np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))
    z_stat = (z1 - z2) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    return float(z_stat), float(p_value)


def modality_pair_correlations(gini_df: pd.DataFrame, period: str) -> pd.DataFrame:
    """Correlation matrix for all modality pairs in given period."""
    modalities = ["CV", "NLP", "Audio", "Tabular"]

    if period == "pre":
        start, end = None, CONFIG.pre_cutoff
    else:
        start, end = CONFIG.post_cutoff, None

    sub = gini_df.copy()
    if start:
        sub = sub[sub.index >= pd.Timestamp(start)]
    if end:
        sub = sub[sub.index < pd.Timestamp(end)]

    sub = sub[modalities].dropna()

    if len(sub) < 3:
        return pd.DataFrame(np.nan, index=modalities, columns=modalities)

    return sub.corr()
