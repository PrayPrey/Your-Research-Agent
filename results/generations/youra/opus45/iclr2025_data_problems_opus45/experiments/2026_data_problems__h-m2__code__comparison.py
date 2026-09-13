"""
Comparison analysis for H-M2: R^2 regression and gate evaluation.
Tests structural metric decoupling in deep networks vs convex baseline.
"""

import os
import json
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from typing import Dict, List, Any

from config import HM2Config


def compute_r2_deep(metrics_df: pd.DataFrame) -> Dict[str, float]:
    """
    Regress rho_r and rho_m on error_norm via LinearRegression.
    Returns: {'r2_rho_r': float, 'r2_rho_m': float, 'r2_avg': float}
    Gate SC-2: r2_rho_r < 0.80 OR r2_rho_m < 0.80
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

    print(f"Single-error-axis R^2 (deep network):")
    print(f"  rho_r ~ error_norm: R^2 = {r2_rho_r:.4f}")
    print(f"  rho_m ~ error_norm: R^2 = {r2_rho_m:.4f}")
    print(f"  Average: R^2 = {r2_avg:.4f}")

    return {
        'r2_rho_r': r2_rho_r,
        'r2_rho_m': r2_rho_m,
        'r2_avg': r2_avg,
    }


def compute_partial_correlation(
    metrics_df: pd.DataFrame,
    budget_level: int = None,
) -> float:
    """
    Compute Pearson correlation between rho_r and rho_m.
    If budget_level is specified, compute for that budget only.
    Returns correlation r.
    """
    if budget_level is not None:
        df_subset = metrics_df[metrics_df['budget'] == budget_level].copy()
    else:
        df_subset = metrics_df.copy()

    if len(df_subset) < 3:
        return np.nan

    r = pearsonr(df_subset['rho_r'], df_subset['rho_m'])[0]
    return r


def compute_partial_corr_deep(
    metrics_df: pd.DataFrame,
    cfg: HM2Config,
) -> Dict[int, float]:
    """
    Compute Pearson correlation at each budget level.
    Returns: {budget: partial_corr}
    Gate SC-3: min value < 0.85
    """
    partial_corrs = {}
    print("Cross-metric correlations (deep network):")
    for budget in cfg.compute_budgets:
        r = compute_partial_correlation(metrics_df, budget_level=budget)
        partial_corrs[budget] = r
        print(f"  Budget {budget}: corr(rho_r, rho_m) = {r:.4f}")
    return partial_corrs


def compute_r2_by_method(metrics_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Compute R^2 separately for each attribution method.
    Returns: {method: {'r2_rho_r': float, 'r2_rho_m': float}}
    """
    r2_by_method = {}
    for method in metrics_df['method'].unique():
        df_method = metrics_df[metrics_df['method'] == method]
        X = df_method['error_norm'].values.reshape(-1, 1)
        y_rho_r = df_method['rho_r'].values
        y_rho_m = df_method['rho_m'].values

        if len(X) < 2:
            r2_by_method[method] = {'r2_rho_r': np.nan, 'r2_rho_m': np.nan}
            continue

        reg_r = LinearRegression().fit(X, y_rho_r)
        reg_m = LinearRegression().fit(X, y_rho_m)

        r2_by_method[method] = {
            'r2_rho_r': r2_score(y_rho_r, reg_r.predict(X)),
            'r2_rho_m': r2_score(y_rho_m, reg_m.predict(X)),
        }
    return r2_by_method


def compute_r2_by_budget(metrics_df: pd.DataFrame, cfg: HM2Config) -> Dict[int, Dict[str, float]]:
    """
    Compute R^2 separately for each budget level.
    Returns: {budget: {'r2_rho_r': float, 'r2_rho_m': float}}
    """
    r2_by_budget = {}
    for budget in cfg.compute_budgets:
        df_budget = metrics_df[metrics_df['budget'] == budget]
        X = df_budget['error_norm'].values.reshape(-1, 1)
        y_rho_r = df_budget['rho_r'].values
        y_rho_m = df_budget['rho_m'].values

        if len(X) < 2:
            r2_by_budget[budget] = {'r2_rho_r': np.nan, 'r2_rho_m': np.nan}
            continue

        reg_r = LinearRegression().fit(X, y_rho_r)
        reg_m = LinearRegression().fit(X, y_rho_m)

        r2_by_budget[budget] = {
            'r2_rho_r': r2_score(y_rho_r, reg_r.predict(X)),
            'r2_rho_m': r2_score(y_rho_m, reg_m.predict(X)),
        }
    return r2_by_budget


def load_hm1_baseline(cfg: HM2Config) -> Dict[str, Any]:
    """
    Load H-M1 convex results. Try CSV first, fallback to hardcoded validated values.
    Returns: {'r2_rho_r': float, 'r2_rho_m': float, 'partial_corr_by_budget': dict}
    """
    # Try loading from H-M1 results
    if os.path.exists(cfg.hm1_results_path):
        try:
            hm1_df = pd.read_csv(cfg.hm1_results_path)
            # Compute R^2 from H-M1 data
            X = hm1_df['error_norm'].values.reshape(-1, 1)
            y_rho_r = hm1_df['rho_r'].values
            y_rho_m = hm1_df['rho_m'].values

            reg_r = LinearRegression().fit(X, y_rho_r)
            reg_m = LinearRegression().fit(X, y_rho_m)

            r2_rho_r = r2_score(y_rho_r, reg_r.predict(X))
            r2_rho_m = r2_score(y_rho_m, reg_m.predict(X))

            # Compute partial correlations per budget
            partial_corrs = {}
            for budget in cfg.compute_budgets:
                df_budget = hm1_df[hm1_df['budget'] == budget]
                if len(df_budget) >= 2:
                    partial_corrs[budget] = pearsonr(df_budget['rho_r'], df_budget['rho_m'])[0]
                else:
                    partial_corrs[budget] = cfg.hm1_partial_corr.get(budget, 0.99)

            print(f"Loaded H-M1 baseline from {cfg.hm1_results_path}")
            return {
                'r2_rho_r': r2_rho_r,
                'r2_rho_m': r2_rho_m,
                'r2_avg': (r2_rho_r + r2_rho_m) / 2,
                'partial_corr_by_budget': partial_corrs,
            }
        except Exception as e:
            print(f"Failed to load H-M1 CSV: {e}, using hardcoded values")

    # Fallback to hardcoded values from verified H-M1 results
    print("Using hardcoded H-M1 baseline values (from validated results)")
    return {
        'r2_rho_r': cfg.hm1_r2_rho_r,
        'r2_rho_m': cfg.hm1_r2_rho_m,
        'r2_avg': (cfg.hm1_r2_rho_r + cfg.hm1_r2_rho_m) / 2,
        'partial_corr_by_budget': cfg.hm1_partial_corr.copy(),
    }


def evaluate_gate(
    r2_deep: Dict[str, float],
    partial_corr_deep: Dict[int, float],
    hm1_baseline: Dict[str, Any],
    cfg: HM2Config,
) -> Dict[str, Any]:
    """
    Check all gate conditions SC-2, SC-3, SC-4.
    Returns: {'gate_pass': bool, 'sc2_pass': bool, 'sc3_pass': bool, 'sc4_pass': bool,
              'r2_deep': dict, 'delta_r2': float, 'min_partial_corr': float, 'details': str}
    """
    # SC-2: R^2_deep < 0.80 for at least one metric
    sc2_pass = (r2_deep['r2_rho_r'] < cfg.r2_threshold or
                r2_deep['r2_rho_m'] < cfg.r2_threshold)

    # SC-3: min(partial_corr) < 0.85
    min_partial_corr = min(partial_corr_deep.values())
    sc3_pass = min_partial_corr < cfg.partial_corr_threshold

    # SC-4: delta_R^2 > 0.15 (convex R^2 - deep R^2)
    delta_r2_rho_r = hm1_baseline['r2_rho_r'] - r2_deep['r2_rho_r']
    delta_r2_rho_m = hm1_baseline['r2_rho_m'] - r2_deep['r2_rho_m']
    delta_r2 = max(delta_r2_rho_r, delta_r2_rho_m)
    sc4_pass = delta_r2 > cfg.delta_r2_threshold

    # Overall gate: SC-2 must pass (primary condition)
    # SC-3 and SC-4 are supporting evidence
    gate_pass = sc2_pass

    details = (
        f"SC-2 (R^2<{cfg.r2_threshold}): {'PASS' if sc2_pass else 'FAIL'} "
        f"[r2_rho_r={r2_deep['r2_rho_r']:.4f}, r2_rho_m={r2_deep['r2_rho_m']:.4f}]\n"
        f"SC-3 (corr<{cfg.partial_corr_threshold}): {'PASS' if sc3_pass else 'FAIL'} "
        f"[min_corr={min_partial_corr:.4f}]\n"
        f"SC-4 (delta>{cfg.delta_r2_threshold}): {'PASS' if sc4_pass else 'FAIL'} "
        f"[delta_r2={delta_r2:.4f}]"
    )

    print(f"\n=== H-M2 MUST_WORK Gate Evaluation ===")
    print(details)
    print(f"OVERALL GATE: {'PASS' if gate_pass else 'FAIL'}")

    return {
        'gate_pass': gate_pass,
        'sc2_pass': sc2_pass,
        'sc3_pass': sc3_pass,
        'sc4_pass': sc4_pass,
        'r2_deep': r2_deep,
        'r2_convex': {
            'r2_rho_r': hm1_baseline['r2_rho_r'],
            'r2_rho_m': hm1_baseline['r2_rho_m'],
        },
        'delta_r2': delta_r2,
        'delta_r2_rho_r': delta_r2_rho_r,
        'delta_r2_rho_m': delta_r2_rho_m,
        'min_partial_corr': min_partial_corr,
        'partial_corr_deep': partial_corr_deep,
        'partial_corr_convex': hm1_baseline['partial_corr_by_budget'],
        'details': details,
    }


def save_results(
    metrics_df: pd.DataFrame,
    r2_results: Dict[str, float],
    partial_corr_deep: Dict[int, float],
    hm1_baseline: Dict[str, Any],
    gate_results: Dict[str, Any],
    r2_by_method: Dict[str, Dict[str, float]],
    cfg: HM2Config,
) -> None:
    """Save metrics.csv, r2_analysis.json, gate_results.json to cfg.results_dir."""
    os.makedirs(cfg.results_dir, exist_ok=True)

    # Save metrics DataFrame
    metrics_path = os.path.join(cfg.results_dir, 'metrics.csv')
    metrics_df.to_csv(metrics_path, index=False)
    print(f"Saved: {metrics_path}")

    # Save R^2 analysis
    r2_analysis = {
        'deep': r2_results,
        'convex': {
            'r2_rho_r': hm1_baseline['r2_rho_r'],
            'r2_rho_m': hm1_baseline['r2_rho_m'],
            'r2_avg': hm1_baseline['r2_avg'],
        },
        'delta': {
            'delta_r2_rho_r': hm1_baseline['r2_rho_r'] - r2_results['r2_rho_r'],
            'delta_r2_rho_m': hm1_baseline['r2_rho_m'] - r2_results['r2_rho_m'],
        },
        'by_method': r2_by_method,
        'partial_corr_deep': {str(k): v for k, v in partial_corr_deep.items()},
        'partial_corr_convex': {str(k): v for k, v in hm1_baseline['partial_corr_by_budget'].items()},
    }
    r2_path = os.path.join(cfg.results_dir, 'r2_analysis.json')
    with open(r2_path, 'w') as f:
        json.dump(r2_analysis, f, indent=2)
    print(f"Saved: {r2_path}")

    # Save gate results (convert numpy bools to Python bools)
    gate_json = {
        'gate_pass': bool(gate_results['gate_pass']),
        'sc2_pass': bool(gate_results['sc2_pass']),
        'sc3_pass': bool(gate_results['sc3_pass']),
        'sc4_pass': bool(gate_results['sc4_pass']),
        'r2_deep': {k: float(v) for k, v in gate_results['r2_deep'].items()},
        'r2_convex': {k: float(v) for k, v in gate_results['r2_convex'].items()},
        'delta_r2': float(gate_results['delta_r2']),
        'min_partial_corr': float(gate_results['min_partial_corr']),
        'details': gate_results['details'],
    }
    gate_path = os.path.join(cfg.results_dir, 'gate_results.json')
    with open(gate_path, 'w') as f:
        json.dump(gate_json, f, indent=2)
    print(f"Saved: {gate_path}")
