"""Statistical analysis for H-C1 comparison."""

import numpy as np
from scipy import stats


def compute_ensemble_mean(scores: dict, tasks: list) -> float:
    """Compute mean accuracy across tasks."""
    return float(np.mean([scores[t] for t in tasks]))


def paired_ttest(cpdr_scores: list, rp_scores: list) -> dict:
    """Paired t-test across seeds."""
    if len(cpdr_scores) < 2:
        return {"t_stat": float("nan"), "p_value": 1.0}
    t_stat, p_value = stats.ttest_rel(cpdr_scores, rp_scores)
    return {"t_stat": float(t_stat), "p_value": float(p_value)}


def gate_check(cpdr_mean: float, rp_mean: float, threshold: float = 0.01) -> dict:
    """Check if improvement exceeds threshold."""
    improvement = cpdr_mean - rp_mean
    return {"improvement": improvement, "passed": improvement > threshold}


def cohens_d(cpdr_scores: list, rp_scores: list) -> float:
    """Effect size for paired samples."""
    diff = np.array(cpdr_scores) - np.array(rp_scores)
    return float(np.mean(diff) / (np.std(diff, ddof=1) + 1e-8))
