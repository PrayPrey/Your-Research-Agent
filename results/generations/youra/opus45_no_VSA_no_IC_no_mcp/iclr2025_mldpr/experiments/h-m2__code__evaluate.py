"""Gate evaluation for h-m2 temporal prediction."""

from m2_config import R2_PASS_THRESHOLD, R2_FAIL_THRESHOLD, LOO_R2_THRESHOLD, CI_LOWER_THRESHOLD


def check_gate(results: dict) -> str:
    """PASS if r2 > 0.3, FAIL if r2 < 0.1, else MARGINAL."""
    if "error" in results:
        return "FAIL"
    r2 = results["r2"]
    if r2 > R2_PASS_THRESHOLD:
        return "PASS"
    if r2 < R2_FAIL_THRESHOLD:
        return "FAIL"
    return "MARGINAL"


def summarize(results: dict) -> dict:
    """Add informational flags."""
    if "error" in results:
        return results
    return {
        **results,
        "slope_negative": results["slope"] < 0,
        "loo_pass": results["loo_r2"] > LOO_R2_THRESHOLD,
        "ci_lower_pass": results["ci_95_lower"] > CI_LOWER_THRESHOLD,
    }
