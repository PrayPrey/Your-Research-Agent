"""Statistical analysis: contingency tables and chi-square test."""

import pandas as pd
from scipy import stats

from config import P_VALUE_THRESHOLD, MIN_SAMPLE_SIZE


def build_contingency(results: pd.DataFrame) -> pd.DataFrame:
    """Build scale x error_type contingency table."""
    contingency = pd.crosstab(results['scale'], results['error_type'])
    expected_cols = ['TP', 'TN', 'FP', 'FN']
    for col in expected_cols:
        if col not in contingency.columns:
            contingency[col] = 0
    return contingency[expected_cols]


def chi_square_test(contingency: pd.DataFrame) -> dict:
    """Run chi-square test for independence."""
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    return {
        "chi2": chi2,
        "p_value": p_value,
        "dof": dof,
        "expected": expected,
        "significant": p_value < P_VALUE_THRESHOLD,
    }


def verify_mechanism_active(results: pd.DataFrame) -> dict:
    """Verify sample size and chi-square gate."""
    sample_size = len(results)
    contingency = build_contingency(results)
    chi2_result = chi_square_test(contingency)
    sample_ok = sample_size >= MIN_SAMPLE_SIZE
    chi2_ok = chi2_result["significant"]
    return {
        "sample_size": sample_size,
        "sample_size_ok": sample_ok,
        "chi2_statistic": chi2_result["chi2"],
        "p_value": chi2_result["p_value"],
        "p_value_ok": chi2_ok,
        "dof": chi2_result["dof"],
        "gate_passed": sample_ok and chi2_ok,
        "contingency": contingency,
    }


def compute_error_rates(results: pd.DataFrame) -> pd.DataFrame:
    """Compute FPR, FNR, accuracy per scale."""
    metrics = []
    for scale in results['scale'].unique():
        scale_df = results[results['scale'] == scale]
        tp = (scale_df['error_type'] == 'TP').sum()
        tn = (scale_df['error_type'] == 'TN').sum()
        fp = (scale_df['error_type'] == 'FP').sum()
        fn = (scale_df['error_type'] == 'FN').sum()
        total = tp + tn + fp + fn
        accuracy = (tp + tn) / total if total > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        metrics.append({
            "scale": scale,
            "TP": tp,
            "TN": tn,
            "FP": fp,
            "FN": fn,
            "accuracy": accuracy,
            "FPR": fpr,
            "FNR": fnr,
            "total": total,
        })
    return pd.DataFrame(metrics)
