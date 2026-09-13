"""Statistical analysis module for H-M1: ANOVA and Tukey HSD."""

import numpy as np
from scipy.stats import f_oneway, tukey_hsd

from config import GRANULARITY_LEVELS, RepairConfig


def aggregate_by_granularity(results: list[dict]) -> dict[str, list[int]]:
    """Group binary success values by granularity level.

    Args:
        results: List of repair result dicts with 'granularity' and 'success' keys

    Returns:
        Dict mapping granularity level to list of binary success values (0 or 1)
    """
    groups = {g: [] for g in GRANULARITY_LEVELS}

    for r in results:
        granularity = r["granularity"]
        success = 1 if r["success"] else 0
        if granularity in groups:
            groups[granularity].append(success)

    # Verify all groups have same size
    sizes = [len(groups[g]) for g in GRANULARITY_LEVELS]
    if len(set(sizes)) > 1:
        print(f"Warning: Unequal group sizes: {dict(zip(GRANULARITY_LEVELS, sizes))}")

    return groups


def run_anova(groups: dict[str, list[int]], config: RepairConfig = None) -> dict:
    """Run one-way ANOVA across granularity groups.

    Tests null hypothesis: all group means are equal.

    Args:
        groups: Dict mapping granularity to list of binary success values
        config: Optional RepairConfig for alpha threshold

    Returns:
        Dict with:
            f_statistic: F-test statistic
            p_value: p-value for the test
            eta_squared: Effect size (SS_between / SS_total)
            gate_passed: Whether p_value < alpha
            success_rates: Dict of success rate per granularity
            n_per_group: Number of samples per group
    """
    alpha = config.anova_alpha if config else 0.05

    # Convert to numpy arrays
    groups_list = [np.array(groups[g], dtype=float) for g in GRANULARITY_LEVELS]

    # Run one-way ANOVA
    f_stat, p_value = f_oneway(*groups_list)

    # Calculate effect size (eta-squared)
    all_data = np.concatenate(groups_list)
    grand_mean = np.mean(all_data)
    ss_total = np.sum((all_data - grand_mean) ** 2)
    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups_list)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0.0

    # Calculate success rates
    success_rates = {g: float(np.mean(groups[g])) for g in GRANULARITY_LEVELS}

    # Gate decision
    gate_passed = bool(p_value < alpha)

    return {
        "f_statistic": float(f_stat),
        "p_value": float(p_value),
        "eta_squared": float(eta_squared),
        "gate_passed": gate_passed,
        "success_rates": success_rates,
        "n_per_group": len(groups_list[0]) if groups_list else 0,
    }


def run_posthoc(groups: dict[str, list[int]]) -> dict:
    """Run Tukey's HSD post-hoc pairwise comparisons.

    Should only be called if ANOVA is significant (p < 0.05).

    Args:
        groups: Dict mapping granularity to list of binary success values

    Returns:
        Dict with pairwise comparisons:
            "G0_vs_G1": {"statistic": float, "p_value": float, "significant": bool}
            ... (10 pairs total for 5 groups)
    """
    # Convert to numpy arrays
    groups_list = [np.array(groups[g], dtype=float) for g in GRANULARITY_LEVELS]

    # Run Tukey HSD
    tukey_result = tukey_hsd(*groups_list)

    # Build pairwise comparison dict
    pairwise = {}
    for i, g1 in enumerate(GRANULARITY_LEVELS):
        for j, g2 in enumerate(GRANULARITY_LEVELS):
            if i >= j:
                continue
            key = f"{g1}_vs_{g2}"
            pairwise[key] = {
                "statistic": float(tukey_result.statistic[i, j]),
                "p_value": float(tukey_result.pvalue[i, j]),
                "significant": bool(tukey_result.pvalue[i, j] < 0.05),
            }

    return pairwise
