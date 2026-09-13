"""
Statistical Analysis Pipeline for H-E1 experiment.

Computes Cohen's d effect sizes, confidence intervals, paired t-tests,
and gate condition checking.
"""

import json
from pathlib import Path
from typing import Tuple, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """
    Compute pooled-SD Cohen's d effect size.

    Args:
        group1: First group scores (enumerated)
        group2: Second group scores (synthesized)

    Returns:
        Cohen's d value (positive = group1 > group2)
    """
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return 0.0

    m1, m2 = np.mean(group1), np.mean(group2)
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0

    return (m1 - m2) / pooled_std


def cohens_d_ci(
    d: float, n1: int, n2: int, alpha: float = 0.05
) -> Tuple[float, float]:
    """
    Compute confidence interval for Cohen's d.

    Uses non-central t-distribution approximation.

    Args:
        d: Effect size
        n1: Size of group 1
        n2: Size of group 2
        alpha: Significance level (default 0.05 for 95% CI)

    Returns:
        (ci_low, ci_high)
    """
    # Standard error of d
    se = np.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2)))

    # t critical value
    z = stats.norm.ppf(1 - alpha / 2)

    ci_low = d - z * se
    ci_high = d + z * se

    return ci_low, ci_high


def paired_ttest(
    group1: np.ndarray, group2: np.ndarray
) -> Tuple[float, float]:
    """
    Perform paired t-test.

    Args:
        group1: First group scores
        group2: Second group scores

    Returns:
        (t_statistic, p_value)
    """
    if len(group1) != len(group2):
        raise ValueError("Groups must have same length for paired test")

    t_stat, p_value = stats.ttest_rel(group1, group2)
    return float(t_stat), float(p_value)


def pooled_effect_size(
    effect_sizes: List[float], ns: List[int]
) -> Tuple[float, float]:
    """
    Compute weighted average effect size across studies/models.

    Args:
        effect_sizes: List of Cohen's d values
        ns: List of sample sizes per study

    Returns:
        (pooled_d, standard_error)
    """
    if not effect_sizes or not ns:
        return 0.0, 0.0

    # Inverse variance weighting
    weights = [n / sum(ns) for n in ns]
    pooled_d = sum(d * w for d, w in zip(effect_sizes, weights))

    # Pooled SE
    pooled_se = np.sqrt(sum((1/n) for n in ns))

    return float(pooled_d), float(pooled_se)


def heterogeneity_test(
    effect_sizes: List[float], ns: List[int]
) -> Dict[str, float]:
    """
    Test for heterogeneity across effect sizes (Cochran's Q).

    Args:
        effect_sizes: List of Cohen's d values
        ns: List of sample sizes

    Returns:
        {"Q": float, "p_value": float, "I2": float}
    """
    if len(effect_sizes) < 2:
        return {"Q": 0.0, "p_value": 1.0, "I2": 0.0}

    k = len(effect_sizes)
    pooled_d, _ = pooled_effect_size(effect_sizes, ns)

    # Compute Q statistic
    weights = ns
    Q = sum(w * (d - pooled_d)**2 for w, d in zip(weights, effect_sizes))

    # p-value from chi-squared distribution
    p_value = 1 - stats.chi2.cdf(Q, df=k - 1)

    # I2 statistic (percentage of variability due to heterogeneity)
    I2 = max(0, (Q - (k - 1)) / Q * 100) if Q > 0 else 0.0

    return {
        "Q": float(Q),
        "p_value": float(p_value),
        "I2": float(I2),
    }


def compute_per_rm_stats(scores_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute statistics for each reward model.

    Args:
        scores_df: DataFrame with columns [rm, prompt_id, structure, score, ...]

    Returns:
        DataFrame with columns [rm, cohens_d, ci_low, ci_high, p_value, n, mean_enum, mean_synth]
    """
    results = []

    for rm in scores_df["rm"].unique():
        rm_data = scores_df[scores_df["rm"] == rm]

        # Get enumerated and synthesized scores
        enum_scores = rm_data[rm_data["structure"] == "enumerated"]["score"].values
        synth_scores = rm_data[rm_data["structure"] == "synthesized"]["score"].values

        n = len(enum_scores)
        if n == 0:
            continue

        # Compute effect size
        d = cohens_d(enum_scores, synth_scores)
        ci_low, ci_high = cohens_d_ci(d, n, n)

        # Paired t-test (if same prompt pairs)
        try:
            t_stat, p_value = paired_ttest(enum_scores, synth_scores)
        except ValueError:
            # Fall back to independent t-test
            t_stat, p_value = stats.ttest_ind(enum_scores, synth_scores)
            p_value = float(p_value)

        results.append({
            "rm": rm,
            "cohens_d": d,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "t_stat": t_stat,
            "p_value": p_value,
            "n": n,
            "mean_enum": float(np.mean(enum_scores)),
            "mean_synth": float(np.mean(synth_scores)),
            "std_enum": float(np.std(enum_scores)),
            "std_synth": float(np.std(synth_scores)),
        })

    return pd.DataFrame(results)


def compute_aggregate_stats(per_rm_df: pd.DataFrame) -> Dict:
    """
    Compute aggregate statistics across all RMs.

    Args:
        per_rm_df: DataFrame from compute_per_rm_stats()

    Returns:
        Dict with pooled effect size and heterogeneity statistics
    """
    effect_sizes = per_rm_df["cohens_d"].tolist()
    ns = per_rm_df["n"].tolist()

    pooled_d, pooled_se = pooled_effect_size(effect_sizes, ns)
    hetero = heterogeneity_test(effect_sizes, ns)

    # Count models with significant positive effect
    n_positive = sum(1 for d in effect_sizes if d > 0)
    n_significant = sum(
        1 for _, row in per_rm_df.iterrows()
        if row["p_value"] < 0.05 and row["cohens_d"] > 0
    )
    n_above_threshold = sum(1 for d in effect_sizes if d >= 0.3)

    return {
        "pooled_cohens_d": pooled_d,
        "pooled_se": pooled_se,
        "heterogeneity": hetero,
        "n_models": len(effect_sizes),
        "n_positive_effect": n_positive,
        "n_significant": n_significant,
        "n_above_threshold": n_above_threshold,
        "effect_sizes": effect_sizes,
    }


def check_gate_condition(
    per_rm_df: pd.DataFrame,
    d_threshold: float = 0.3,
    min_models: int = 2
) -> bool:
    """
    Check if gate condition is satisfied.

    Gate: Cohen's d >= threshold in >= min_models architecturally distinct RMs

    Args:
        per_rm_df: DataFrame from compute_per_rm_stats()
        d_threshold: Minimum effect size threshold
        min_models: Minimum number of models that must meet threshold

    Returns:
        True if gate condition is satisfied
    """
    n_passing = sum(1 for d in per_rm_df["cohens_d"] if d >= d_threshold)
    return n_passing >= min_models


def export_results(
    per_rm_df: pd.DataFrame,
    agg: Dict,
    output_dir: str,
    scores_df: Optional[pd.DataFrame] = None,
) -> None:
    """
    Export results to JSON and CSV files.

    Args:
        per_rm_df: Per-RM statistics DataFrame
        agg: Aggregate statistics dict
        output_dir: Output directory path
        scores_df: Optional raw scores DataFrame
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Export effect sizes to JSON
    effect_sizes_data = {
        "per_rm": per_rm_df.to_dict(orient="records"),
        "aggregate": agg,
        "gate_condition": {
            "threshold": 0.3,
            "min_models": 2,
            "satisfied": check_gate_condition(per_rm_df),
        }
    }
    with open(output_path / "effect_sizes.json", "w") as f:
        json.dump(effect_sizes_data, f, indent=2)

    # Export summary stats to CSV
    per_rm_df.to_csv(output_path / "summary_stats.csv", index=False)

    # Export raw scores if provided
    if scores_df is not None:
        scores_df.to_csv(output_path / "raw_scores.csv", index=False)
        with open(output_path / "raw_scores.json", "w") as f:
            json.dump(scores_df.to_dict(orient="records"), f, indent=2)

    print(f"Results exported to {output_path}")
