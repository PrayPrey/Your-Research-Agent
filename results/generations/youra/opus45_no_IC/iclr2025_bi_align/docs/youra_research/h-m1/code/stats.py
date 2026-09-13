"""Statistical testing for H-M1."""

import numpy as np
from scipy import stats
from typing import List, Dict, Tuple

from config import LENGTH_BINS


def one_sample_ttest(values: List[float]) -> Dict:
    """One-sample t-test against 0. Returns stats dict with 95% CI."""
    arr = np.array([v for v in values if not np.isnan(v)])
    n = len(arr)

    if n < 2:
        return {
            'n': n,
            'mean': np.nan,
            'std': np.nan,
            't_statistic': np.nan,
            'p_value': 1.0,
            'ci95': (np.nan, np.nan)
        }

    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1))
    t_stat, p_value = stats.ttest_1samp(arr, 0)

    se = std / np.sqrt(n)
    t_crit = stats.t.ppf(0.975, df=n-1)
    ci_low = mean - t_crit * se
    ci_high = mean + t_crit * se

    return {
        'n': n,
        'mean': mean,
        'std': std,
        'median': float(np.median(arr)),
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'ci95': (ci_low, ci_high)
    }


def cohens_d(values: List[float]) -> float:
    """Cohen's d = mean / std. Returns 0 if std==0."""
    arr = np.array([v for v in values if not np.isnan(v)])
    if len(arr) < 2:
        return 0.0
    std = np.std(arr, ddof=1)
    if std == 0:
        return 0.0
    return float(np.mean(arr) / std)


def check_gate(real_stats: Dict, baseline_stats: Dict) -> Dict:
    """Check gate criteria: real p<0.05 AND mean>0 AND baseline p>0.10."""
    real_p = real_stats.get('p_value', 1.0)
    real_mean = real_stats.get('mean', 0.0)
    baseline_p = baseline_stats.get('null_p', 0.0)

    p_passed = real_p < 0.05
    mean_positive = real_mean > 0
    baseline_null = baseline_p > 0.10

    gate_passed = p_passed and mean_positive and baseline_null

    return {
        'gate_passed': gate_passed,
        'criteria': {
            'p_value_lt_0.05': {'passed': p_passed, 'value': real_p},
            'mean_positive': {'passed': mean_positive, 'value': real_mean},
            'baseline_p_gt_0.10': {'passed': baseline_null, 'value': baseline_p}
        }
    }


def stratify_by_length(
    trajectories: List[Tuple[List[float], List[float]]],
    lag1_rs: List[float],
    bins: Dict = None
) -> Dict[str, Dict]:
    """Stratify conversations by length, run t-test per bin."""
    if bins is None:
        bins = LENGTH_BINS

    if len(trajectories) != len(lag1_rs):
        return {}

    binned = {name: [] for name in bins}

    for (user, ai), r in zip(trajectories, lag1_rs):
        if np.isnan(r):
            continue
        length = len(user)
        for name, (lo, hi) in bins.items():
            if hi is None:
                if length >= lo:
                    binned[name].append(r)
                    break
            elif lo <= length <= hi:
                binned[name].append(r)
                break

    results = {}
    for name, rs in binned.items():
        if len(rs) >= 10:
            results[name] = one_sample_ttest(rs)
        else:
            results[name] = {'n': len(rs), 'mean': np.nan, 'p_value': np.nan}

    return results
