"""Statistical tests for H-M3 gradient noise comparison."""
import numpy as np
from scipy import stats
from typing import List, Dict


def compare_concentration(u_line: List[float], u_ignore: List[float]) -> Dict[str, float]:
    """Compare GT concentration between U_line and U_ignore samples."""
    u_line = np.array(u_line)
    u_ignore = np.array(u_ignore)

    t_stat, t_p = stats.ttest_ind(u_line, u_ignore, alternative='greater')

    u_stat, u_p = stats.mannwhitneyu(u_line, u_ignore, alternative='greater')

    n1, n2 = len(u_line), len(u_ignore)
    var1, var2 = np.var(u_line, ddof=1), np.var(u_ignore, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    cohens_d = (np.mean(u_line) - np.mean(u_ignore)) / (pooled_std + 1e-8)

    ci_low, ci_high = bootstrap_ci_diff(u_line, u_ignore)

    return {
        "u_line_mean": float(np.mean(u_line)),
        "u_line_std": float(np.std(u_line)),
        "u_ignore_mean": float(np.mean(u_ignore)),
        "u_ignore_std": float(np.std(u_ignore)),
        "t_stat": float(t_stat),
        "t_p": float(t_p),
        "u_stat": float(u_stat),
        "u_p": float(u_p),
        "cohens_d": float(cohens_d),
        "ci_95_low": float(ci_low),
        "ci_95_high": float(ci_high),
    }


def bootstrap_ci_diff(
    a: np.ndarray,
    b: np.ndarray,
    n_boot: int = 10000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple:
    """Bootstrap 95% CI for mean difference (a - b)."""
    rng = np.random.RandomState(seed)
    diffs = []

    for _ in range(n_boot):
        a_sample = rng.choice(a, size=len(a), replace=True)
        b_sample = rng.choice(b, size=len(b), replace=True)
        diffs.append(np.mean(a_sample) - np.mean(b_sample))

    diffs = np.array(diffs)
    ci_low = np.percentile(diffs, 100 * alpha / 2)
    ci_high = np.percentile(diffs, 100 * (1 - alpha / 2))

    return ci_low, ci_high


def summarize_noise_ratio(noise_ratios: List[float]) -> Dict[str, float]:
    """Summarize noise ratio distribution for U_ignore samples."""
    arr = np.array(noise_ratios)

    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "pct_above_1": float(np.mean(arr > 1.0) * 100),
        "ci_95_low": float(np.percentile(arr, 2.5)),
        "ci_95_high": float(np.percentile(arr, 97.5)),
    }
