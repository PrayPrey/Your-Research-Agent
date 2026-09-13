"""Statistical testing for Mode 3 existence hypothesis."""

from scipy import stats


def binomial_test_mode3(count: int, total: int, p0: float = 0.10) -> dict:
    """One-sided binomial test: H1: p > p0."""
    if total == 0:
        return {
            "proportion": 0.0,
            "ci_95_lower": 0.0,
            "ci_95_upper": 0.0,
            "p_value": 1.0,
            "result": "FAIL",
        }

    res = stats.binomtest(count, total, p0, alternative="greater")
    ci = res.proportion_ci(confidence_level=0.95, method="wilson")

    proportion = count / total
    p_value = res.pvalue

    if p_value < 0.05 and proportion > p0:
        result = "SUCCESS"
    else:
        result = "FAIL"

    return {
        "proportion": proportion,
        "ci_95_lower": ci.low,
        "ci_95_upper": ci.high,
        "p_value": p_value,
        "result": result,
    }


def sensitivity_analysis(count: int, total: int, thresholds: list) -> dict:
    """Run binomial test at multiple thresholds."""
    results = {}
    for thresh in thresholds:
        results[str(thresh)] = binomial_test_mode3(count, total, thresh)
    return results
