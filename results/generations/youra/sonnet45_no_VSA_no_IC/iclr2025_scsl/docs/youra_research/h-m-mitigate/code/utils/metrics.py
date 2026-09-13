"""Evaluation metrics for spurious correlation benchmarks."""

import numpy as np
from scipy import stats


def compute_worst_group_accuracy(
    predictions: np.ndarray, labels: np.ndarray, groups: np.ndarray
) -> dict:
    """Compute worst-group accuracy (WGA) and per-group accuracies.

    Args:
        predictions: Model predictions (N,)
        labels: Ground truth labels (N,)
        groups: Group IDs (N,) in range [0, num_groups-1]

    Returns:
        {
            "wga": float,
            "avg_acc": float,
            "group_accs": list of floats,
        }
    """
    unique_groups = np.unique(groups)
    group_accs = []

    for g in unique_groups:
        mask = groups == g
        if mask.sum() > 0:
            acc = (predictions[mask] == labels[mask]).mean()
        else:
            acc = 0.0
        group_accs.append(acc)

    wga = min(group_accs) if group_accs else 0.0
    avg_acc = (predictions == labels).mean()

    return {"wga": wga, "avg_acc": avg_acc, "group_accs": group_accs}


def bootstrap_comparison(
    method1_wga: np.ndarray, method2_wga: np.ndarray, n_resamples: int = 1000
) -> dict:
    """Bootstrap test for pairwise WGA comparison.

    Args:
        method1_wga: WGA values for method 1 (typically 5 seeds)
        method2_wga: WGA values for method 2 (typically 5 seeds)
        n_resamples: Number of bootstrap resamples

    Returns:
        {
            "mean_diff": float (method1 - method2),
            "p_value": float (one-sided test: method1 > method2),
            "ci_lower": float (95% CI lower bound),
            "ci_upper": float (95% CI upper bound),
        }
    """
    n = len(method1_wga)
    assert len(method2_wga) == n, "Methods must have same number of seeds"

    diff_samples = []
    rng = np.random.default_rng(seed=0)

    for _ in range(n_resamples):
        # Resample with replacement
        idx = rng.choice(n, size=n, replace=True)
        diff = method1_wga[idx].mean() - method2_wga[idx].mean()
        diff_samples.append(diff)

    diff_samples = np.array(diff_samples)

    # Mean difference
    mean_diff = method1_wga.mean() - method2_wga.mean()

    # P-value (one-sided: method1 > method2)
    # H0: diff <= 0, p = P(diff_samples <= 0)
    p_value = (diff_samples <= 0).sum() / n_resamples

    # 95% confidence interval
    ci_lower = np.percentile(diff_samples, 2.5)
    ci_upper = np.percentile(diff_samples, 97.5)

    return {
        "mean_diff": mean_diff,
        "p_value": p_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


def compute_group_statistics(results_df):
    """Compute statistics across seeds for each method.

    Args:
        results_df: DataFrame with columns [method, seed, wga, avg_acc]

    Returns:
        DataFrame with columns [method, wga_mean, wga_std, avg_acc_mean, avg_acc_std]
    """
    import pandas as pd

    stats_df = (
        results_df.groupby("method")
        .agg({"wga": ["mean", "std"], "avg_acc": ["mean", "std"]})
        .reset_index()
    )

    stats_df.columns = [
        "method",
        "wga_mean",
        "wga_std",
        "avg_acc_mean",
        "avg_acc_std",
    ]

    return stats_df
