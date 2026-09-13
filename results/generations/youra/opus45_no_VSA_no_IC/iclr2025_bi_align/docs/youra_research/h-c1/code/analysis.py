"""Statistical analysis: z-test, ratio CI, effect size."""

import math
import numpy as np
import pandas as pd
from scipy import stats


def category_mode3_counts(df: pd.DataFrame) -> dict:
    """Compute mode3 and total counts per category.
    Returns {'subjective': {'mode3': int, 'total': int},
             'objective':  {'mode3': int, 'total': int}}
    """
    result = {}
    for cat in ["subjective", "objective"]:
        subset = df[df["category"] == cat]
        total = len(subset)
        mode3 = int((subset["mode"] == 3).sum())
        result[cat] = {"mode3": mode3, "total": total}
    return result


def two_proportion_ztest(a: int, n_subj: int, c: int, n_obj: int) -> dict:
    """One-sided z-test: p_subj > p_obj (pooled proportion SE).
    Returns {'p_subj': float, 'p_obj': float, 'z': float, 'p_value': float}
    """
    p_subj = a / n_subj
    p_obj = c / n_obj
    p_pool = (a + c) / (n_subj + n_obj)
    se = math.sqrt(p_pool * (1 - p_pool) * (1/n_subj + 1/n_obj))
    z = (p_subj - p_obj) / se if se > 0 else 0.0
    p_value = 1 - stats.norm.cdf(z)
    return {"p_subj": p_subj, "p_obj": p_obj, "z": z, "p_value": p_value}


def ratio_ci_log(a: int, n_subj: int, c: int, n_obj: int) -> dict:
    """Log-transform 95% CI for ratio p_subj/p_obj.
    Returns {'ratio': float, 'ci_95_lower': float, 'ci_95_upper': float}
    """
    p_subj = a / n_subj
    p_obj = c / n_obj
    if p_obj == 0:
        return {"ratio": float("inf"), "ci_95_lower": float("nan"), "ci_95_upper": float("nan")}
    ratio = p_subj / p_obj
    if a == 0 or c == 0:
        return {"ratio": ratio, "ci_95_lower": float("nan"), "ci_95_upper": float("nan")}
    se_log = math.sqrt((1 - p_subj) / a + (1 - p_obj) / c)
    log_ratio = math.log(ratio)
    ci_lower = math.exp(log_ratio - 1.96 * se_log)
    ci_upper = math.exp(log_ratio + 1.96 * se_log)
    return {"ratio": ratio, "ci_95_lower": ci_lower, "ci_95_upper": ci_upper}


def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h effect size: 2 * (arcsin(sqrt(p1)) - arcsin(sqrt(p2)))"""
    return 2 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p2)))


def classify_result(ratio: float, p_value: float, alpha: float = 0.05) -> str:
    """Classify outcome: 'CONFIRMED' | 'FALSIFIED' | 'INCONCLUSIVE'."""
    if ratio > 1.5 and p_value < alpha:
        return "CONFIRMED"
    if ratio < 1.0:
        return "FALSIFIED"
    return "INCONCLUSIVE"
