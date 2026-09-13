"""
Binomial hypothesis test for MUST_WORK gate validation.
"""
from typing import Tuple
from scipy.stats import binomtest


def binomial_test(
    n_successes: int,
    n_trials: int,
    p_null: float = 0.40,
    alpha: float = 0.05,
    alternative: str = "greater"
) -> Tuple[float, bool]:
    """
    Perform one-tailed binomial test for H0: p < 0.40 vs H1: p ≥ 0.40.

    Args:
        n_successes: Number of genuine violations observed
        n_trials: Total sample size (500)
        p_null: Null hypothesis threshold (default 0.40)
        alpha: Significance level (default 0.05)
        alternative: Test direction ('greater' for one-tailed)

    Returns:
        Tuple[float, bool]:
            - p-value (float)
            - PASS/FAIL decision (True=PASS, False=FAIL)
    """
    result = binomtest(
        k=n_successes,
        n=n_trials,
        p=p_null,
        alternative=alternative
    )

    p_value = result.pvalue
    decision = bool(p_value < alpha)  # True=PASS gate, False=FAIL gate

    return float(p_value), decision
