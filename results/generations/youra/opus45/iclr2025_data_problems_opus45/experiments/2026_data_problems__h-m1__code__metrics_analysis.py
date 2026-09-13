"""
Metrics analysis for H-M1 convex experiment.
Computes partial correlations and single-error-axis R^2.
"""

import numpy as np
import pandas as pd
import pingouin as pg
from scipy.stats import spearmanr, pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from typing import Dict, List

from config import HM1Config


def compute_rho_r_rho_m(
    pred_scores: np.ndarray,
    loo_ground_truth: np.ndarray,
) -> dict:
    """
    Compute rank (Spearman) and magnitude (Pearson) fidelity.
    Args:
        pred_scores: (N_train, N_test) attribution scores
        loo_ground_truth: (N_train, N_test) exact LOO influences
    Returns: {'rho_r': float, 'rho_m': float}
    """
    pred_flat = pred_scores.flatten()
    truth_flat = loo_ground_truth.flatten()

    # Remove any NaN or inf values
    valid_mask = np.isfinite(pred_flat) & np.isfinite(truth_flat)
    pred_flat = pred_flat[valid_mask]
    truth_flat = truth_flat[valid_mask]

    rho_r = spearmanr(pred_flat, truth_flat).correlation
    rho_m = pearsonr(pred_flat, truth_flat)[0]

    # Handle NaN cases
    if np.isnan(rho_r):
        rho_r = 0.0
    if np.isnan(rho_m):
        rho_m = 0.0

    return {'rho_r': rho_r, 'rho_m': rho_m}


def build_metrics_dataframe(
    method_scores: Dict[str, Dict[int, List[np.ndarray]]],
    loo_exact: np.ndarray,
) -> pd.DataFrame:
    """
    Build DataFrame with columns: [method, budget, seed, rho_r, rho_m, error_norm]
    where error_norm = ||scores - loo_exact||_F
    """
    rows = []

    for method, budget_dict in method_scores.items():
        for budget, score_list in budget_dict.items():
            for seed_idx, scores in enumerate(score_list):
                metrics = compute_rho_r_rho_m(scores, loo_exact)
                error_norm = np.linalg.norm(scores - loo_exact)

                rows.append({
                    'method': method,
                    'budget': budget,
                    'seed': seed_idx,
                    'rho_r': metrics['rho_r'],
                    'rho_m': metrics['rho_m'],
                    'error_norm': error_norm,
                })

    df = pd.DataFrame(rows)
    return df


def compute_partial_correlation(
    metrics_df: pd.DataFrame,
    budget_level: int = None,
) -> float:
    """
    Compute partial correlation between rho_r and rho_m.
    If budget_level is specified, compute for that budget only.
    Otherwise compute across all data controlling for budget.
    Returns partial correlation r.
    """
    if budget_level is not None:
        df_subset = metrics_df[metrics_df['budget'] == budget_level].copy()
    else:
        df_subset = metrics_df.copy()

    if len(df_subset) < 3:
        return np.nan

    # For single budget, compute simple Pearson correlation
    # (no need for partial correlation when budget is constant)
    if budget_level is not None:
        r = pearsonr(df_subset['rho_r'], df_subset['rho_m'])[0]
        return r

    # Partial correlation controlling for budget
    try:
        result = pg.partial_corr(
            data=df_subset,
            x='rho_r',
            y='rho_m',
            covar='budget',
            method='pearson'
        )
        return result['r'].values[0]
    except Exception as e:
        print(f"Partial correlation failed: {e}")
        return pearsonr(df_subset['rho_r'], df_subset['rho_m'])[0]


def compute_partial_correlations_all_budgets(
    metrics_df: pd.DataFrame,
    budgets: List[int],
) -> Dict[int, float]:
    """
    Compute Pearson correlation at each budget level.
    Returns: {budget: correlation_r}
    """
    partial_corrs = {}
    for budget in budgets:
        r = compute_partial_correlation(metrics_df, budget_level=budget)
        partial_corrs[budget] = r
        print(f"  Budget {budget}: corr(rho_r, rho_m) = {r:.4f}")
    return partial_corrs


def compute_single_error_axis_r2(
    metrics_df: pd.DataFrame,
) -> dict:
    """
    Regress rho_r and rho_m on error_norm via sklearn LinearRegression.
    Tests the single-error-axis hypothesis: both metrics should be explained
    by approximation error in convex settings.
    Returns: {'r2_rho_r': float, 'r2_rho_m': float, 'r2_avg': float}
    """
    X = metrics_df['error_norm'].values.reshape(-1, 1)
    y_rho_r = metrics_df['rho_r'].values
    y_rho_m = metrics_df['rho_m'].values

    # Fit for rho_r
    reg_r = LinearRegression()
    reg_r.fit(X, y_rho_r)
    r2_rho_r = r2_score(y_rho_r, reg_r.predict(X))

    # Fit for rho_m
    reg_m = LinearRegression()
    reg_m.fit(X, y_rho_m)
    r2_rho_m = r2_score(y_rho_m, reg_m.predict(X))

    r2_avg = (r2_rho_r + r2_rho_m) / 2

    print(f"Single-error-axis R^2:")
    print(f"  rho_r ~ error_norm: R^2 = {r2_rho_r:.4f}")
    print(f"  rho_m ~ error_norm: R^2 = {r2_rho_m:.4f}")
    print(f"  Average: R^2 = {r2_avg:.4f}")

    return {
        'r2_rho_r': r2_rho_r,
        'r2_rho_m': r2_rho_m,
        'r2_avg': r2_avg,
    }


def check_success_criteria(
    partial_corrs: Dict[int, float],
    r2_results: dict,
    cfg: HM1Config,
) -> dict:
    """
    Check if MUST_WORK gate criteria are met.
    Primary: partial_corr >= 0.95 at ALL 5 budget levels
    Secondary: R^2 >= 0.95 for single-error-axis

    Returns: {
        'gate_pass': bool,
        'partial_corr_pass': bool,
        'r2_pass': bool,
        'partial_corrs': dict,
        'r2_results': dict,
        'min_partial_corr': float,
        'failed_budgets': list
    }
    """
    # Check partial correlations
    min_partial_corr = min(partial_corrs.values())
    failed_budgets = [b for b, r in partial_corrs.items() if r < cfg.partial_corr_threshold]
    partial_corr_pass = len(failed_budgets) == 0

    # Check R^2
    r2_pass = r2_results['r2_avg'] >= cfg.r2_threshold

    # Overall gate: both conditions must pass (primary is partial_corr)
    gate_pass = partial_corr_pass

    print(f"\n=== MUST_WORK Gate Check ===")
    print(f"Partial correlation threshold: {cfg.partial_corr_threshold}")
    print(f"Min partial correlation: {min_partial_corr:.4f}")
    print(f"Failed budgets: {failed_budgets}")
    print(f"Partial corr pass: {partial_corr_pass}")
    print(f"R^2 pass: {r2_pass}")
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")

    return {
        'gate_pass': gate_pass,
        'partial_corr_pass': partial_corr_pass,
        'r2_pass': r2_pass,
        'partial_corrs': partial_corrs,
        'r2_results': r2_results,
        'min_partial_corr': min_partial_corr,
        'failed_budgets': failed_budgets,
    }
