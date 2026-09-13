"""Statistical analysis functions for H-M2: McNemar's test and rate calculations."""

import numpy as np
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar


def build_contingency_table(g0_outcomes: list, g3_outcomes: list) -> np.ndarray:
    """Build 2x2 contingency table for McNemar's test.

    Args:
        g0_outcomes: List of binary outcomes (0/1) for G0 feedback
        g3_outcomes: List of binary outcomes (0/1) for G3 feedback

    Returns:
        np.ndarray shape (2, 2) - table[i,j] = count where G0=i and G3=j

    Table layout:
                   G3=0 (fail)  G3=1 (success)
        G0=0 (fail)    a            b
        G0=1 (success) c            d

    Discordant pairs: b (G0 fail, G3 success) and c (G0 success, G3 fail)
    """
    assert len(g0_outcomes) == len(g3_outcomes), "Must be paired data"

    table = np.zeros((2, 2), dtype=int)
    for g0, g3 in zip(g0_outcomes, g3_outcomes):
        table[g0, g3] += 1

    return table


def run_mcnemar_test(table: np.ndarray) -> dict:
    """Run McNemar's exact test for paired nominal data.

    Args:
        table: 2x2 contingency table from build_contingency_table()

    Returns:
        dict with: statistic, pvalue, discordant_b, discordant_c, favors
    """
    # Discordant pairs
    b = table[0, 1]  # G0 fail, G3 success
    c = table[1, 0]  # G0 success, G3 fail

    # McNemar's test (exact for small samples)
    result = mcnemar(table, exact=True)

    # Determine which condition is favored
    if b > c:
        favors = "G3"
    elif c > b:
        favors = "G0"
    else:
        favors = "neither"

    return {
        "statistic": float(result.statistic),
        "pvalue": float(result.pvalue),
        "discordant_b": int(b),  # G0 fail -> G3 success
        "discordant_c": int(c),  # G0 success -> G3 fail
        "favors": favors,
        "significant": result.pvalue < 0.05
    }


def calculate_rates_and_difference(g0_outcomes: list, g3_outcomes: list) -> dict:
    """Calculate success rates and difference with 95% CI.

    Args:
        g0_outcomes: List of binary outcomes (0/1) for G0 feedback
        g3_outcomes: List of binary outcomes (0/1) for G3 feedback

    Returns:
        dict with: g0_rate, g3_rate, difference, difference_pp,
                   g0_successes, g3_successes, n_pairs,
                   ci_lower_pp, ci_upper_pp
    """
    n = len(g0_outcomes)
    g0_successes = sum(g0_outcomes)
    g3_successes = sum(g3_outcomes)

    g0_rate = g0_successes / n
    g3_rate = g3_successes / n
    difference = g3_rate - g0_rate  # G3 - G0 (positive if G3 better)

    # Confidence interval for difference of proportions (paired data)
    # Using Agresti-Caffo method for paired proportions
    # SE = sqrt((g0_rate*(1-g0_rate) + g3_rate*(1-g3_rate) - 2*cov) / n)
    # Simplified: use standard error for difference
    se = np.sqrt((g0_rate * (1 - g0_rate) + g3_rate * (1 - g3_rate)) / n)
    z = stats.norm.ppf(0.975)  # 95% CI
    ci_lower = difference - z * se
    ci_upper = difference + z * se

    return {
        "g0_rate": g0_rate,
        "g3_rate": g3_rate,
        "g0_successes": g0_successes,
        "g3_successes": g3_successes,
        "n_pairs": n,
        "difference": difference,
        "difference_pp": difference * 100,  # percentage points
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "ci_lower_pp": ci_lower * 100,
        "ci_upper_pp": ci_upper * 100
    }


def evaluate_gate(rates: dict, mcnemar_result: dict, threshold: float = 0.10) -> dict:
    """Evaluate H-M2 gate: G3 >= G0 + 10pp AND McNemar p < 0.05 favoring G3.

    Args:
        rates: Output from calculate_rates_and_difference()
        mcnemar_result: Output from run_mcnemar_test()
        threshold: Minimum required difference (default 0.10 = 10pp)

    Returns:
        dict with: gate_passed, verdict, reason,
                   difference_met, significant, favors_g3
    """
    difference = rates["difference"]
    pvalue = mcnemar_result["pvalue"]
    favors = mcnemar_result["favors"]

    # Gate conditions
    difference_met = difference >= threshold  # G3 - G0 >= 10pp
    significant = pvalue < 0.05
    favors_g3 = favors == "G3"

    # Gate passes only if ALL conditions met
    gate_passed = difference_met and significant and favors_g3

    # Determine reason
    if gate_passed:
        verdict = "PASS"
        reason = f"G3 outperforms G0 by {rates['difference_pp']:.1f}pp (>= 10pp) with p={pvalue:.2e}"
    else:
        verdict = "FAIL"
        reasons = []
        if not difference_met:
            reasons.append(f"difference={rates['difference_pp']:.1f}pp (need >= 10pp)")
        if not favors_g3:
            reasons.append(f"favors {favors} not G3")
        if not significant:
            reasons.append(f"p={pvalue:.3f} (need < 0.05)")
        reason = "; ".join(reasons)

    return {
        "gate_passed": gate_passed,
        "verdict": verdict,
        "reason": reason,
        "difference_met": difference_met,
        "significant": significant,
        "favors_g3": favors_g3,
        "threshold": threshold,
        "threshold_pp": threshold * 100
    }
