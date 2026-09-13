"""StatsTester: Wilcoxon test and secondary statistical checks for H-M1."""

import numpy as np
import pandas as pd
from scipy import stats

from loader import compute_early_phase_density, compute_late_phase_density


def run_wilcoxon_test(
    curriculum_vals: np.ndarray,
    uniform_vals: np.ndarray,
) -> dict:
    """One-tailed Wilcoxon signed-rank test: H1 = curriculum > uniform.
    Returns {statistic, p_value, passed, curriculum_mean, uniform_mean, delta}."""
    result = stats.wilcoxon(curriculum_vals, uniform_vals, alternative="greater")
    curriculum_mean = float(np.mean(curriculum_vals))
    uniform_mean = float(np.mean(uniform_vals))
    delta = curriculum_mean - uniform_mean
    passed = bool(result.pvalue < 0.05)
    return {
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "passed": passed,
        "curriculum_mean": curriculum_mean,
        "uniform_mean": uniform_mean,
        "delta": delta,
    }


def check_assumption_a1(
    easy_only_vals: np.ndarray,
    curriculum_vals: np.ndarray,
) -> dict:
    """Check if easy_only_mean >= curriculum_mean (easy-only baseline check).
    Returns {passed, easy_only_mean, curriculum_mean, delta}."""
    easy_only_mean = float(np.mean(easy_only_vals))
    curriculum_mean = float(np.mean(curriculum_vals))
    delta = easy_only_mean - curriculum_mean
    passed = bool(easy_only_mean >= curriculum_mean)
    return {
        "passed": passed,
        "easy_only_mean": easy_only_mean,
        "curriculum_mean": curriculum_mean,
        "delta": delta,
    }


def compute_phase_stats(logs: dict) -> dict:
    """Compute early and late phase stats for all conditions.
    Returns {condition: {early: {mean, std}, late: {mean, std}}}."""
    phase_stats = {}
    for condition, df in logs.items():
        early_vals = compute_early_phase_density(df)
        late_vals = compute_late_phase_density(df)
        phase_stats[condition] = {
            "early": {
                "mean": float(np.nanmean(early_vals)),
                "std": float(np.nanstd(early_vals)),
            },
            "late": {
                "mean": float(np.nanmean(late_vals)),
                "std": float(np.nanstd(late_vals)),
            },
        }
    return phase_stats
