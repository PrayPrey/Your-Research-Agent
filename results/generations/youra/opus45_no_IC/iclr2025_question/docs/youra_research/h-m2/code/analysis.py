"""H-M2 Analysis - Mann-Whitney U test and Cliff's delta"""
import numpy as np
from scipy import stats
from config import FACTUAL_FAMILY, ENTITY_FAMILY, BENCHMARK_NAMES


def extract_pairs(js_matrix: np.ndarray, names: list = BENCHMARK_NAMES) -> tuple:
    """Split upper-triangle of 6x6 matrix into same-family and cross-family pairs.

    Returns:
        tuple: (same_family_js[6], cross_family_js[9])
    """
    same_family = []
    cross_family = []
    n = len(names)

    for i in range(n):
        for j in range(i + 1, n):
            val = js_matrix[i, j]
            b1, b2 = names[i], names[j]

            both_factual = b1 in FACTUAL_FAMILY and b2 in FACTUAL_FAMILY
            both_entity = b1 in ENTITY_FAMILY and b2 in ENTITY_FAMILY

            if both_factual or both_entity:
                same_family.append(val)
            else:
                cross_family.append(val)

    assert len(same_family) == 6, f"Expected 6 same-family pairs, got {len(same_family)}"
    assert len(cross_family) == 9, f"Expected 9 cross-family pairs, got {len(cross_family)}"

    return same_family, cross_family


def cliffs_delta(x: list, y: list) -> float:
    """Compute Cliff's delta effect size.

    Range: [-1, 1]
    -1: all x < y (large effect)
    0: no difference
    1: all x > y
    """
    n1, n2 = len(x), len(y)
    count = sum(
        1 if xi < yj else (-1 if xi > yj else 0)
        for xi in x for yj in y
    )
    return count / (n1 * n2)


def cliffs_delta_ci(x: list, y: list, alpha: float = 0.05, n_bootstrap: int = 1000) -> tuple:
    """Bootstrap confidence interval for Cliff's delta."""
    np.random.seed(42)
    deltas = []
    x_arr, y_arr = np.array(x), np.array(y)

    for _ in range(n_bootstrap):
        x_boot = np.random.choice(x_arr, size=len(x), replace=True)
        y_boot = np.random.choice(y_arr, size=len(y), replace=True)
        deltas.append(cliffs_delta(x_boot.tolist(), y_boot.tolist()))

    lower = np.percentile(deltas, 100 * alpha / 2)
    upper = np.percentile(deltas, 100 * (1 - alpha / 2))
    return lower, upper


def test_error_family_hypothesis(js_matrix: np.ndarray, names: list = BENCHMARK_NAMES) -> dict:
    """Test H-M2: Same-family benchmarks have lower JS-divergence than cross-family.

    Returns:
        dict with p_value, same_family_mean, cross_family_mean, effect_size, etc.
    """
    same_family, cross_family = extract_pairs(js_matrix, names)

    # Mann-Whitney U test (one-sided: same < cross)
    statistic, p_value = stats.mannwhitneyu(
        same_family, cross_family, alternative='less'
    )

    # Cliff's delta effect size
    effect_size = cliffs_delta(same_family, cross_family)
    ci_lower, ci_upper = cliffs_delta_ci(same_family, cross_family)

    return {
        "p_value": p_value,
        "statistic": statistic,
        "same_family_mean": float(np.mean(same_family)),
        "same_family_std": float(np.std(same_family)),
        "cross_family_mean": float(np.mean(cross_family)),
        "cross_family_std": float(np.std(cross_family)),
        "same_family_values": same_family,
        "cross_family_values": cross_family,
        "effect_size_cliffs_d": effect_size,
        "effect_size_ci": (ci_lower, ci_upper),
        "n_same": len(same_family),
        "n_cross": len(cross_family),
    }
