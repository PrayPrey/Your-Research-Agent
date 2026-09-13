"""Metrics computation for H-M2 temperature variation analysis."""

import numpy as np
from scipy.stats import bootstrap
from config import CV_GATE_THRESHOLD, RANGE_GATE_THRESHOLD, N_BOOTSTRAP, SEED


def compute_cv_and_range(optimal_temps):
    """Compute coefficient of variation and range of optimal temperatures.

    Args:
        optimal_temps: dict[int, float] - {cluster_id: optimal_T}

    Returns:
        tuple[float, float]: (cv, t_range)
    """
    temps = np.array(list(optimal_temps.values()))
    if len(temps) == 0:
        return 0.0, 0.0

    cv = np.std(temps) / np.mean(temps) if np.mean(temps) > 0 else 0.0
    t_range = np.max(temps) - np.min(temps)
    return float(cv), float(t_range)


def bootstrap_ci(temps, statistic_fn, n_resamples=N_BOOTSTRAP, seed=SEED):
    """Compute bootstrap 95% confidence interval for a statistic.

    Args:
        temps: array of temperatures
        statistic_fn: function to compute statistic (e.g., np.std)
        n_resamples: number of bootstrap resamples
        seed: random seed

    Returns:
        tuple[float, float]: (low, high) CI bounds
    """
    if len(temps) < 2:
        val = statistic_fn(temps)
        return float(val), float(val)

    result = bootstrap(
        (temps,),
        statistic_fn,
        n_resamples=n_resamples,
        random_state=seed,
        method='percentile'
    )
    return float(result.confidence_interval.low), float(result.confidence_interval.high)


def evaluate_gate(cv, t_range):
    """Evaluate whether gate thresholds are met.

    Returns:
        tuple[bool, bool]: (primary_pass, secondary_pass)
    """
    primary_pass = cv > CV_GATE_THRESHOLD
    secondary_pass = t_range > RANGE_GATE_THRESHOLD
    return primary_pass, secondary_pass
