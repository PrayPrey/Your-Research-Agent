"""
statistics.py - Statistical tests for h-e1 experiment.

Includes bootstrap CI, Mann-Whitney, Cohen's d, and mechanism verification.
"""
import numpy as np
from scipy import stats
from typing import Dict, Tuple

MIN_N_PAIRS = 1000


def bootstrap_c_sem(
    cos_actual: np.ndarray,
    cos_random: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Tuple[float, np.ndarray]:
    """Bootstrap confidence interval for C_sem.

    Args:
        cos_actual: shape (N,) - actual cosine similarities
        cos_random: shape (N,) - random control cosine similarities
        n_bootstrap: number of bootstrap samples
        seed: random seed

    Returns:
        Tuple of (c_sem, ci_array) where ci_array shape (2,) = [lower, upper] at 95% CI.
    """
    rng = np.random.default_rng(seed)
    n = len(cos_actual)
    c_sem = float(np.mean(cos_actual) - np.mean(cos_random))

    boot_samples = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        boot_samples[i] = np.mean(cos_actual[idx]) - np.mean(cos_random[idx])

    ci_array = np.array([
        np.percentile(boot_samples, 2.5),
        np.percentile(boot_samples, 97.5),
    ])
    return c_sem, ci_array


def bootstrap_cohen_d(
    arr_a: np.ndarray,
    arr_b: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Tuple[float, np.ndarray]:
    """Bootstrap confidence interval for Cohen's d using pooled std.

    Pooled std formula: sqrt(((N-1)*var_a + (M-1)*var_b) / (N+M-2))
    Zero-division guard: if pooled_std == 0, d = 0.

    Args:
        arr_a: shape (N,) - first array
        arr_b: shape (M,) - second array
        n_bootstrap: number of bootstrap samples
        seed: random seed

    Returns:
        Tuple of (cohen_d, ci_array) where ci_array shape (2,).
    """
    rng = np.random.default_rng(seed)

    def _cohen_d(a, b):
        na, nb = len(a), len(b)
        pooled_var = ((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2)
        pooled_std = np.sqrt(pooled_var)
        if pooled_std == 0:
            return 0.0
        return float((np.mean(a) - np.mean(b)) / pooled_std)

    d = _cohen_d(arr_a, arr_b)

    na, nb = len(arr_a), len(arr_b)
    boot_samples = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx_a = rng.integers(0, na, size=na)
        idx_b = rng.integers(0, nb, size=nb)
        boot_samples[i] = _cohen_d(arr_a[idx_a], arr_b[idx_b])

    ci_array = np.array([
        np.percentile(boot_samples, 2.5),
        np.percentile(boot_samples, 97.5),
    ])
    return d, ci_array


def mann_whitney_test(arr_a: np.ndarray, arr_b: np.ndarray) -> Dict:
    """Mann-Whitney U test.

    Returns:
        dict with 'statistic' and 'p_value'.
    """
    result = stats.mannwhitneyu(arr_a, arr_b, alternative="two-sided")
    return {
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
    }


def run_all_tests(
    cos_actual: np.ndarray,
    cos_topic: np.ndarray,
    cos_random: np.ndarray,
    n_pairs: int,
) -> Dict:
    """Run all statistical tests for h-e1.

    Args:
        cos_actual: shape (N,) - actual cosine similarities
        cos_topic: shape (N,) - topic-matched control cosine similarities
        cos_random: shape (N,) - random control cosine similarities
        n_pairs: number of pairs (must be >= MIN_N_PAIRS)

    Returns:
        Flat dict with all results.
    """
    assert n_pairs >= MIN_N_PAIRS, f"n_pairs={n_pairs} < MIN_N_PAIRS={MIN_N_PAIRS}"

    c_sem, c_sem_ci = bootstrap_c_sem(cos_actual, cos_random)
    mw_actual_vs_topic = mann_whitney_test(cos_actual, cos_topic)
    mw_topic_vs_random = mann_whitney_test(cos_topic, cos_random)
    cohen_d_actual_vs_topic, _ = bootstrap_cohen_d(cos_actual, cos_topic)
    cohen_d_actual_vs_random, _ = bootstrap_cohen_d(cos_actual, cos_random)
    cohen_d_topic_vs_random, _ = bootstrap_cohen_d(cos_topic, cos_random)

    return {
        "n_pairs": n_pairs,
        "c_sem": c_sem,
        "c_sem_ci": c_sem_ci,
        "cos_actual_mean": float(np.mean(cos_actual)),
        "cos_topic_mean": float(np.mean(cos_topic)),
        "cos_random_mean": float(np.mean(cos_random)),
        "mann_whitney_actual_vs_topic": mw_actual_vs_topic,
        "mann_whitney_topic_vs_random": mw_topic_vs_random,
        "cohen_d_actual_vs_topic": cohen_d_actual_vs_topic,
        "cohen_d_actual_vs_random": cohen_d_actual_vs_random,
        "cohen_d_topic_vs_random": cohen_d_topic_vs_random,
    }


def verify_mechanism_activated(
    results: Dict,
    embeddings_computed: bool,
) -> Tuple[bool, Dict]:
    """Verify mechanism activation via 5 indicators.

    Indicators:
      1. embeddings_computed: embeddings were successfully computed
      2. c_sem_positive: c_sem > 0
      3. ci_lower_positive: c_sem_ci[0] > 0
      4. ordering_holds: cos_actual_mean > cos_topic_mean > cos_random_mean
      5. sufficient_pairs: n_pairs >= 1000

    Returns:
        Tuple of (all_activated: bool, indicators: dict).
    """
    indicators = {
        "embeddings_computed": embeddings_computed,
        "c_sem_positive": results["c_sem"] > 0,
        "ci_lower_positive": results["c_sem_ci"][0] > 0,
        "ordering_holds": (
            results["cos_actual_mean"] > results["cos_topic_mean"] > results["cos_random_mean"]
        ),
        "sufficient_pairs": results["n_pairs"] >= 1000,
    }
    all_activated = all(indicators.values())
    return all_activated, indicators
