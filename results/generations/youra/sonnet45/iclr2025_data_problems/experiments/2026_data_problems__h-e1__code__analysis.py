"""
Analysis module for H-E1.
Descriptive statistics, OLS regression, and comparison reporting.
"""
import json
import os
import sys

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

import config


def compute_descriptive_stats(registry_df: pd.DataFrame) -> dict:
    """Compute doc_score distribution, feature coverage, benchmark availability.

    Returns: stats dict with keys: doc_score_counts, feature_fractions, benchmark_availability.
    """
    stats = {}

    # doc_score distribution (0-4)
    if 'doc_score' in registry_df.columns:
        doc_score_counts = registry_df['doc_score'].value_counts().sort_index().to_dict()
        stats['doc_score_counts'] = {int(k): int(v) for k, v in doc_score_counts.items()}
        stats['doc_score_mean'] = float(registry_df['doc_score'].mean())
        stats['doc_score_median'] = float(registry_df['doc_score'].median())

    # Feature coverage fractions
    feature_fractions = {}
    for feat in config.FEATURE_COLS:
        if feat in registry_df.columns:
            feature_fractions[feat] = float(registry_df[feat].mean())
    stats['feature_fractions'] = feature_fractions

    # Benchmark availability
    benchmark_availability = {}
    for bench in config.BENCHMARK_COLS:
        if bench in registry_df.columns:
            benchmark_availability[bench] = float(registry_df[bench].notna().mean())
        elif 'avg_score' in registry_df.columns and bench == 'mmlu_pro':
            benchmark_availability[bench] = float(registry_df['avg_score'].notna().mean())
    stats['benchmark_availability'] = benchmark_availability

    # Summary stats
    stats['n_total'] = len(registry_df)

    return stats


def _prepare_df_for_ols(registry_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare DataFrame for OLS: ensure avg_score column and drop NaN rows."""
    df = registry_df.copy()

    # Ensure avg_score column exists (v2 leaderboard dependent variable)
    if 'avg_score' not in df.columns:
        # Fallback: compute from available benchmark cols
        bench_cols = [c for c in config.BENCHMARK_COLS if c in df.columns]
        if bench_cols:
            df['avg_score'] = df[bench_cols].mean(axis=1)
        elif 'mmlu' in df.columns:
            df['avg_score'] = df['mmlu']
        else:
            raise ValueError("No avg_score or benchmark columns found in registry_df")

    # Drop rows with missing required columns
    required = ['avg_score', 'log_params', 'arch_family']
    df = df.dropna(subset=[c for c in required if c in df.columns])

    # Also ensure doc_score present for proposed model
    if 'doc_score' not in df.columns:
        for feat in config.FEATURE_COLS:
            if feat not in df.columns:
                df[feat] = 0
        df['doc_score'] = df[config.FEATURE_COLS].sum(axis=1)

    # Fill missing log_tokens with median (for models without token data)
    if 'log_tokens' in df.columns:
        median_log_tokens = df['log_tokens'].median()
        df['log_tokens'] = df['log_tokens'].fillna(median_log_tokens)
    else:
        df['log_tokens'] = 11.0  # Default ~100B tokens

    # Ensure doc_score exists
    if 'doc_score' not in df.columns:
        for feat in config.FEATURE_COLS:
            if feat not in df.columns:
                df[feat] = 0
        df['doc_score'] = df[config.FEATURE_COLS].sum(axis=1)

    return df


def fit_ols_baseline(registry_df: pd.DataFrame) -> object:
    """Fit: avg_score ~ log_params + log_tokens + C(arch_family).

    Returns: statsmodels RegressionResultsWrapper.
    """
    df = _prepare_df_for_ols(registry_df)
    formula = "avg_score ~ log_params + log_tokens + C(arch_family)"
    result = smf.ols(formula, data=df).fit()
    return result


def fit_ols_proposed(registry_df: pd.DataFrame) -> object:
    """Fit: avg_score ~ log_params + log_tokens + doc_score + C(arch_family).

    Returns: statsmodels RegressionResultsWrapper.
    """
    df = _prepare_df_for_ols(registry_df)
    formula = "avg_score ~ log_params + log_tokens + doc_score + C(arch_family)"
    result = smf.ols(formula, data=df).fit()
    return result


def compare_models(baseline_result: object, proposed_result: object) -> dict:
    """Extract comparison metrics from two OLS results.

    Returns: {"baseline_r2": float, "proposed_r2": float, "delta_r2": float,
              "beta_docs": float, "p_value": float, "direction_check": bool}
    """
    baseline_r2 = float(baseline_result.rsquared)
    proposed_r2 = float(proposed_result.rsquared)
    delta_r2 = proposed_r2 - baseline_r2

    # Extract doc_score coefficient and p-value
    beta_docs = None
    p_value = None
    for param_name in proposed_result.params.index:
        if 'doc_score' in str(param_name):
            beta_docs = float(proposed_result.params[param_name])
            p_value = float(proposed_result.pvalues[param_name])
            break

    if beta_docs is None:
        beta_docs = 0.0
        p_value = 1.0

    direction_check = beta_docs > 0

    return {
        "baseline_r2": baseline_r2,
        "proposed_r2": proposed_r2,
        "delta_r2": delta_r2,
        "beta_docs": beta_docs,
        "p_value": p_value,
        "direction_check": direction_check,
    }


def save_summary_stats(stats: dict, output_path: str) -> None:
    """Write stats dict to output_path as JSON (json.dump, indent=2)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Make stats JSON-serializable
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [make_serializable(i) for i in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        elif hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        else:
            return str(obj)

    serializable_stats = make_serializable(stats)
    with open(output_path, 'w') as f:
        json.dump(serializable_stats, f, indent=2)
