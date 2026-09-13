"""Statistical tests for H-M3 analysis."""
import numpy as np
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar as statsmodels_mcnemar
from typing import List, Dict


def build_contingency_table(g3: List[bool], g4: List[bool]) -> np.ndarray:
    """Build 2x2 contingency table for McNemar's test.

    Layout:
              G4=Success  G4=Fail
    G3=Success    a          b
    G3=Fail       c          d

    Args:
        g3: G3 success outcomes (bool list)
        g4: G4 success outcomes (bool list)

    Returns:
        2x2 numpy array
    """
    n = len(g3)
    a = sum(1 for i in range(n) if g3[i] and g4[i])       # both success
    b = sum(1 for i in range(n) if g3[i] and not g4[i])   # G3 only
    c = sum(1 for i in range(n) if not g3[i] and g4[i])   # G4 only
    d = sum(1 for i in range(n) if not g3[i] and not g4[i])  # both fail

    table = np.array([[a, b], [c, d]])

    print(f"Contingency table:")
    print(f"  Both success (a): {a}")
    print(f"  G3 only (b): {b}")
    print(f"  G4 only (c): {c}")
    print(f"  Both fail (d): {d}")
    print(f"  Total: {a + b + c + d}")

    return table


def run_mcnemar_test(table: np.ndarray) -> Dict:
    """Run McNemar's exact test for marginal homogeneity.

    Tests whether G3 and G4 have significantly different success rates.

    Args:
        table: 2x2 contingency table

    Returns:
        Dict with statistic, pvalue, significant, interpretation
    """
    result = statsmodels_mcnemar(table, exact=True)

    significant = result.pvalue < 0.05

    if significant:
        # Determine which is better
        b = table[0, 1]  # G3 only
        c = table[1, 0]  # G4 only
        if b > c:
            interpretation = f"G3 significantly outperforms G4 (p={result.pvalue:.4f})"
        else:
            interpretation = f"G4 significantly outperforms G3 (p={result.pvalue:.4f})"
    else:
        interpretation = f"No significant difference between G3 and G4 (p={result.pvalue:.4f})"

    return {
        "statistic": float(result.statistic),
        "pvalue": float(result.pvalue),
        "significant": significant,
        "interpretation": interpretation
    }


def run_tost_equivalence(
    g3_successes: int,
    g3_total: int,
    g4_successes: int,
    g4_total: int,
    margin: float = 0.02,
    alpha: float = 0.05
) -> Dict:
    """TOST (Two One-Sided Tests) for proportion equivalence.

    Tests whether G4-G3 difference is within ±margin.
    H0_lower: diff <= -margin (G4 much worse)
    H0_upper: diff >= +margin (G4 much better)
    Equivalent iff both one-sided tests reject at alpha.

    Args:
        g3_successes: Number of G3 successes
        g3_total: Total G3 samples
        g4_successes: Number of G4 successes
        g4_total: Total G4 samples
        margin: Equivalence margin (default 0.02 = 2%)
        alpha: Significance level

    Returns:
        Dict with rates, difference, p-values, equivalence result
    """
    g3_rate = g3_successes / g3_total
    g4_rate = g4_successes / g4_total
    diff = g4_rate - g3_rate

    # Compute unpooled standard error
    se = np.sqrt(
        g3_rate * (1 - g3_rate) / g3_total +
        g4_rate * (1 - g4_rate) / g4_total
    )

    if se == 0:
        # Degenerate case: all same outcomes
        return {
            "g3_rate": g3_rate,
            "g4_rate": g4_rate,
            "difference": diff,
            "margin": margin,
            "se": 0,
            "p_lower": 1.0,
            "p_upper": 1.0,
            "tost_pvalue": 1.0,
            "equivalent": False,
            "interpretation": "Degenerate case: zero standard error"
        }

    # Lower one-sided test: H0: diff <= -margin
    z_lower = (diff - (-margin)) / se
    p_lower = 1 - stats.norm.cdf(z_lower)

    # Upper one-sided test: H0: diff >= +margin
    z_upper = (diff - margin) / se
    p_upper = stats.norm.cdf(z_upper)

    # TOST p-value is max of the two
    tost_pvalue = max(p_lower, p_upper)
    equivalent = (p_lower < alpha) and (p_upper < alpha)

    if equivalent:
        interpretation = f"G3 and G4 are equivalent within ±{margin*100:.1f}% margin"
    else:
        if diff > margin:
            interpretation = f"G4 exceeds G3 by more than {margin*100:.1f}% (diff={diff*100:.2f}%)"
        elif diff < -margin:
            interpretation = f"G3 exceeds G4 by more than {margin*100:.1f}% (diff={diff*100:.2f}%)"
        else:
            interpretation = f"Insufficient power to confirm equivalence (diff={diff*100:.2f}%)"

    return {
        "g3_rate": g3_rate,
        "g4_rate": g4_rate,
        "difference": diff,
        "margin": margin,
        "se": se,
        "z_lower": z_lower,
        "z_upper": z_upper,
        "p_lower": p_lower,
        "p_upper": p_upper,
        "tost_pvalue": tost_pvalue,
        "equivalent": equivalent,
        "interpretation": interpretation
    }


def compute_confidence_interval(
    g3_successes: int,
    g3_total: int,
    g4_successes: int,
    g4_total: int,
    confidence: float = 0.95
) -> Dict:
    """Compute confidence interval for G4-G3 difference.

    Uses unpooled standard error with normal approximation.

    Args:
        g3_successes: Number of G3 successes
        g3_total: Total G3 samples
        g4_successes: Number of G4 successes
        g4_total: Total G4 samples
        confidence: Confidence level (default 0.95)

    Returns:
        Dict with point_estimate, ci_lower, ci_upper, interpretation
    """
    g3_rate = g3_successes / g3_total
    g4_rate = g4_successes / g4_total
    diff = g4_rate - g3_rate

    # Unpooled standard error
    se = np.sqrt(
        g3_rate * (1 - g3_rate) / g3_total +
        g4_rate * (1 - g4_rate) / g4_total
    )

    # z-score for confidence level
    z = stats.norm.ppf((1 + confidence) / 2)

    ci_lower = diff - z * se
    ci_upper = diff + z * se

    # Interpretation
    if ci_lower > 0:
        interpretation = f"G4 significantly better than G3 ({confidence*100:.0f}% CI excludes 0)"
    elif ci_upper < 0:
        interpretation = f"G3 significantly better than G4 ({confidence*100:.0f}% CI excludes 0)"
    else:
        interpretation = f"No significant difference ({confidence*100:.0f}% CI includes 0)"

    return {
        "point_estimate": diff,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "confidence": confidence,
        "se": se,
        "interpretation": interpretation
    }
