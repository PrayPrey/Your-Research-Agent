"""H-M2 Mann-Whitney U analysis and OLS standardized regression."""
import logging
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

logger = logging.getLogger(__name__)


def compute_effect_size_r(U: float, n1: int, n2: int) -> float:
    """Rank-biserial r = 1 - (2*U)/(n1*n2)."""
    denom = n1 * n2
    if denom == 0:
        return 0.0
    return 1.0 - (2.0 * U) / denom


def run_mwu_unadjusted(df: pd.DataFrame, dv_col: str = "run_count_12m") -> dict:
    """Run MWU on unmatched data."""
    high = df[df["high_accessible"] == 1][dv_col].values
    low = df[df["high_accessible"] == 0][dv_col].values
    stat, p = stats.mannwhitneyu(high, low, alternative="two-sided")
    return {
        "mwu_stat": float(stat),
        "p_value": float(p),
        "n_high": len(high),
        "n_low": len(low),
        "high_mean": float(np.mean(high)),
        "low_mean": float(np.mean(low)),
    }


def run_mwu_matched(matched_df: pd.DataFrame, dv_col: str = "run_count_12m") -> dict:
    """Run MWU on matched data with effect size."""
    high = matched_df[matched_df["high_accessible"] == 1][dv_col].values
    low = matched_df[matched_df["high_accessible"] == 0][dv_col].values
    if len(high) == 0 or len(low) == 0:
        return {"mwu_stat": 0.0, "p_value": 1.0, "n_high": 0, "n_low": 0,
                "high_mean": 0.0, "low_mean": 0.0, "effect_size_r": 0.0, "direction_pass": False}
    stat, p = stats.mannwhitneyu(high, low, alternative="two-sided")
    r = compute_effect_size_r(stat, len(high), len(low))
    direction_pass = float(np.mean(high)) >= float(np.mean(low))
    return {
        "mwu_stat": float(stat),
        "p_value": float(p),
        "n_high": len(high),
        "n_low": len(low),
        "high_mean": float(np.mean(high)),
        "low_mean": float(np.mean(low)),
        "effect_size_r": float(r),
        "direction_pass": bool(direction_pass),
    }


def run_ols_standardized(df: pd.DataFrame, fair_cols: list, dv_col: str = "run_count_12m") -> dict:
    """OLS with standardized coefficients."""
    available = [c for c in fair_cols if c in df.columns]
    if not available:
        return {"accessible_beta": 0.0, "r_squared": 0.0, "params": {}, "pvalues": {}}
    X = df[available].copy()
    y = df[dv_col].copy()
    # Standardize
    X = (X - X.mean()) / X.std().replace(0, 1)
    y = (y - y.mean()) / y.std() if y.std() > 0 else y
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()
    accessible_beta = float(model.params.get("fair_A", 0.0))
    return {
        "accessible_beta": accessible_beta,
        "r_squared": float(model.rsquared),
        "params": {k: float(v) for k, v in model.params.items()},
        "pvalues": {k: float(v) for k, v in model.pvalues.items()},
    }


def run_mechanism_check(results: dict) -> dict:
    """Assert mechanism validity."""
    checks = {}
    n_pairs = results.get("n_matched_pairs", 0)
    checks["sufficient_pairs"] = n_pairs >= 30
    checks["smd_ok"] = results.get("smd_max", 1.0) < 0.1
    checks["high_mean_ge_zero"] = results.get("high_mean", -1) >= 0
    all_pass = all(checks.values())
    checks["all_pass"] = all_pass
    return checks
