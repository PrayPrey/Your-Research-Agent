"""Statistical analysis and hypothesis testing."""

from typing import List, Tuple, Dict
import numpy as np
from scipy import stats


def test_slope_significance(slopes: List[float], alpha: float = 0.05) -> Tuple[float, float]:
    """
    Test if slopes are significantly negative.

    H0: mean slope = 0
    H1: mean slope < 0

    Args:
        slopes: List of slope values
        alpha: Significance level

    Returns:
        (t_statistic, p_value)
    """
    # One-sample t-test against 0
    t_stat, p_value = stats.ttest_1samp(slopes, 0.0)

    # One-tailed p-value (testing for negative slope)
    p_value_one_tailed = p_value / 2 if t_stat < 0 else 1 - (p_value / 2)

    return t_stat, p_value_one_tailed


def compute_effect_size(slopes: List[float], baseline_mean: float = 0.0) -> float:
    """
    Compute Cohen's d effect size.

    d = (mean - baseline) / std

    Args:
        slopes: List of slope values
        baseline_mean: Expected baseline mean (default: 0 for random)

    Returns:
        Cohen's d
    """
    mean = np.mean(slopes)
    std = np.std(slopes, ddof=1)

    if std == 0:
        return 0.0

    cohens_d = (mean - baseline_mean) / std

    return cohens_d


def report_statistics(slopes: List[float], alpha: float = 0.05) -> Dict:
    """
    Generate statistical summary report.

    Args:
        slopes: List of slope values
        alpha: Significance level

    Returns:
        Dictionary with statistical results
    """
    t_stat, p_value = test_slope_significance(slopes, alpha)
    effect_size = compute_effect_size(slopes)

    mean_slope = np.mean(slopes)
    median_slope = np.median(slopes)
    std_slope = np.std(slopes, ddof=1)

    # Count negative slopes
    negative_count = sum(1 for s in slopes if s < 0)
    negative_percentage = (negative_count / len(slopes)) * 100

    return {
        "mean_slope": mean_slope,
        "median_slope": median_slope,
        "std_slope": std_slope,
        "t_statistic": t_stat,
        "p_value": p_value,
        "cohens_d": effect_size,
        "alpha": alpha,
        "significant": p_value < alpha,
        "negative_count": negative_count,
        "total_count": len(slopes),
        "negative_percentage": negative_percentage
    }
