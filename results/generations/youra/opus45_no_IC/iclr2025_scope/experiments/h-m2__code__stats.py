"""H-M2: Statistics - t-test, Mann-Whitney, Cohen's d."""

import numpy as np
from scipy import stats


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Compute Cohen's d effect size with pooled std."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(ddof=1), group2.var(ddof=1)

    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0

    return (group1.mean() - group2.mean()) / pooled_std


def compare_groups(high_retention: np.ndarray, low_retention: np.ndarray) -> dict:
    """Compare high vs low entropy groups."""
    _, p_high = stats.shapiro(high_retention[:50] if len(high_retention) > 50 else high_retention)
    _, p_low = stats.shapiro(low_retention[:50] if len(low_retention) > 50 else low_retention)

    normal = p_high > 0.05 and p_low > 0.05

    if normal:
        t_stat, p_value = stats.ttest_ind(high_retention, low_retention)
        test_used = "t-test"
    else:
        stat, p_value = stats.mannwhitneyu(high_retention, low_retention, alternative='greater')
        t_stat = stat
        test_used = "mann-whitney-u"

    d = cohens_d(high_retention, low_retention)

    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "cohens_d": float(d),
        "test_used": test_used,
        "normal": normal,
        "high_mean": float(high_retention.mean()),
        "low_mean": float(low_retention.mean()),
        "high_std": float(high_retention.std()),
        "low_std": float(low_retention.std()),
    }


def evaluate_gate(p_value: float, high_mean: float, low_mean: float,
                  d: float, threshold: float = 0.05, min_d: float = 0.5) -> bool:
    """PASS if p<threshold AND high_mean>low_mean AND |d|>min_d."""
    return p_value < threshold and high_mean > low_mean and abs(d) > min_d
