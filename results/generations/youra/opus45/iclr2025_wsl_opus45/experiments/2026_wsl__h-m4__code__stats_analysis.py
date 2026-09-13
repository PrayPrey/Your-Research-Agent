"""Statistics: Cohen's d with bootstrap CI, group comparison, gate evaluation."""

from typing import TypedDict

import numpy as np
from scipy import stats

import config
from adapter_loader import AdapterRecord


class CohensDResult(TypedDict):
    """Result of Cohen's d analysis for a layer type."""
    layer_type: str
    cohens_d: float
    ci_low: float
    ci_high: float
    p_value: float
    n_within: int
    n_between: int
    mean_within: float
    mean_between: float


def split_within_between(
    distance_matrix: np.ndarray,
    records: list[AdapterRecord],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Split upper-triangle pairs by category membership.

    Args:
        distance_matrix: Symmetric (40, 40) distance matrix
        records: List of AdapterRecord with category info

    Returns:
        (within, between): 1D arrays of distances
        - within: pairs where both adapters share same category
        - between: pairs where adapters differ in category
    """
    n = len(records)
    within = []
    between = []

    for i in range(n):
        for j in range(i + 1, n):
            cat_i = records[i].category
            cat_j = records[j].category
            d = distance_matrix[i, j]

            if cat_i == cat_j:
                within.append(d)
            else:
                between.append(d)

    return np.array(within), np.array(between)


def compute_cohens_d_with_ci(
    within: np.ndarray,
    between: np.ndarray,
    n_bootstrap: int = 2000,
    random_seed: int = 42,
    ci_level: float = 0.95,
) -> tuple[float, float, float, float]:
    """
    Compute Cohen's d with bootstrap confidence interval.

    Uses pooled standard deviation formula:
    d = (mean_between - mean_within) / pooled_std

    Positive d indicates between > within (clustering signal).

    Args:
        within: 1D array of within-cluster distances
        between: 1D array of between-cluster distances
        n_bootstrap: Number of bootstrap iterations
        random_seed: Random seed for reproducibility
        ci_level: Confidence level (default 0.95 for 95% CI)

    Returns:
        (cohens_d, ci_low, ci_high, p_value)
    """
    mean_w = np.mean(within)
    mean_b = np.mean(between)
    n_w, n_b = len(within), len(between)

    # Pooled standard deviation
    var_w = np.var(within, ddof=1)
    var_b = np.var(between, ddof=1)
    pooled_std = np.sqrt(((n_w - 1) * var_w + (n_b - 1) * var_b) / (n_w + n_b - 2))

    # Cohen's d (positive = between > within = clustering signal)
    if pooled_std > 0:
        d = (mean_b - mean_w) / pooled_std
    else:
        d = 0.0

    # Bootstrap confidence interval
    rng = np.random.RandomState(random_seed)
    bootstrap_ds = []

    for _ in range(n_bootstrap):
        # Resample with replacement
        w_sample = rng.choice(within, size=n_w, replace=True)
        b_sample = rng.choice(between, size=n_b, replace=True)

        # Compute d for bootstrap sample
        mean_w_boot = np.mean(w_sample)
        mean_b_boot = np.mean(b_sample)
        var_w_boot = np.var(w_sample, ddof=1)
        var_b_boot = np.var(b_sample, ddof=1)
        pooled_boot = np.sqrt(((n_w - 1) * var_w_boot + (n_b - 1) * var_b_boot) / (n_w + n_b - 2))

        if pooled_boot > 0:
            d_boot = (mean_b_boot - mean_w_boot) / pooled_boot
        else:
            d_boot = 0.0

        bootstrap_ds.append(d_boot)

    # Percentile CI
    alpha = 1 - ci_level
    ci_low = np.percentile(bootstrap_ds, 100 * alpha / 2)
    ci_high = np.percentile(bootstrap_ds, 100 * (1 - alpha / 2))

    # Two-sample t-test for p-value
    t_stat, p_value = stats.ttest_ind(between, within, equal_var=True)

    return d, ci_low, ci_high, p_value


def analyze_all_layer_types(
    distances: dict[str, np.ndarray],
    records: list[AdapterRecord],
    n_bootstrap: int = 2000,
    random_seed: int = 42,
) -> list[CohensDResult]:
    """
    Compute Cohen's d for all layer types.

    Args:
        distances: Dict mapping layer_type -> (40, 40) distance matrix
        records: List of AdapterRecord
        n_bootstrap: Number of bootstrap iterations
        random_seed: Random seed

    Returns:
        List of CohensDResult sorted by cohens_d descending
    """
    results = []

    for layer_type, dist_matrix in distances.items():
        within, between = split_within_between(dist_matrix, records)

        d, ci_low, ci_high, p_value = compute_cohens_d_with_ci(
            within, between,
            n_bootstrap=n_bootstrap,
            random_seed=random_seed,
        )

        results.append(CohensDResult(
            layer_type=layer_type,
            cohens_d=d,
            ci_low=ci_low,
            ci_high=ci_high,
            p_value=p_value,
            n_within=len(within),
            n_between=len(between),
            mean_within=float(np.mean(within)),
            mean_between=float(np.mean(between)),
        ))

    # Sort by Cohen's d descending
    results = sorted(results, key=lambda r: r["cohens_d"], reverse=True)

    return results


def compute_group_statistics(
    results: list[CohensDResult],
    attention_types: list[str],
    mlp_types: list[str],
) -> dict:
    """
    Compare Cohen's d between attention and MLP layer groups.

    Args:
        results: List of CohensDResult from analyze_all_layer_types
        attention_types: List of attention layer type names
        mlp_types: List of MLP layer type names

    Returns:
        Dict with group statistics and Mann-Whitney U test result
    """
    # Extract Cohen's d for each group
    attn_d = [r["cohens_d"] for r in results if r["layer_type"] in attention_types]
    mlp_d = [r["cohens_d"] for r in results if r["layer_type"] in mlp_types]

    # Compute group statistics
    attention_mean = np.mean(attn_d) if attn_d else 0.0
    attention_std = np.std(attn_d, ddof=1) if len(attn_d) > 1 else 0.0
    mlp_mean = np.mean(mlp_d) if mlp_d else 0.0
    mlp_std = np.std(mlp_d, ddof=1) if len(mlp_d) > 1 else 0.0

    # Mann-Whitney U test (non-parametric, good for small samples)
    if len(attn_d) > 0 and len(mlp_d) > 0:
        stat, p_value = stats.mannwhitneyu(attn_d, mlp_d, alternative='two-sided')
    else:
        stat, p_value = np.nan, np.nan

    return {
        "attention_mean": float(attention_mean),
        "attention_std": float(attention_std),
        "attention_d_values": attn_d,
        "mlp_mean": float(mlp_mean),
        "mlp_std": float(mlp_std),
        "mlp_d_values": mlp_d,
        "group_difference": float(attention_mean - mlp_mean),
        "mannwhitney_statistic": float(stat) if not np.isnan(stat) else None,
        "p_value": float(p_value) if not np.isnan(p_value) else None,
    }


def evaluate_gate(
    results: list[CohensDResult],
    threshold: float = 0.8,
) -> dict:
    """
    Evaluate gate condition: at least one layer type with Cohen's d > threshold.

    Args:
        results: List of CohensDResult from analyze_all_layer_types
        threshold: Cohen's d threshold (default 0.8)

    Returns:
        Dict with gate evaluation result
    """
    # Find layers above threshold
    layers_above = [r for r in results if r["cohens_d"] > threshold]

    # Best layer (highest Cohen's d)
    best = results[0] if results else None

    return {
        "passed": len(layers_above) > 0,
        "threshold": threshold,
        "best_layer": best["layer_type"] if best else None,
        "max_d": best["cohens_d"] if best else None,
        "max_d_ci": (best["ci_low"], best["ci_high"]) if best else None,
        "layers_above_threshold": [r["layer_type"] for r in layers_above],
        "n_layers_above": len(layers_above),
        "all_layer_d_values": {r["layer_type"]: r["cohens_d"] for r in results},
    }
