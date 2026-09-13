"""H-M2 Verifier: verify_mechanism_activated."""
from __future__ import annotations

from typing import Dict, Tuple

from analyzer import VarianceCompressionResults


def verify_mechanism_activated(
    results: VarianceCompressionResults,
) -> Tuple[bool, Dict[str, bool]]:
    """Check 5 indicators; return (all_pass, indicators_dict).

    Gate: direction_confirmed AND statistically_significant.
    """
    indicators = {
        "direction_confirmed": bool(results["direction_confirmed"]),
        "statistically_significant": bool(results["bf_p_two_tailed"] < 0.05),
        "effect_measured": bool(results["var_pre"] != results["var_post"]),
        "n_pre_nonzero": bool(results["n_pre"] > 0),
        "n_post_nonzero": bool(results["n_post"] > 0),
    }
    all_pass = indicators["direction_confirmed"] and indicators["statistically_significant"]
    verdict = "PASS" if all_pass else "FAIL"
    print(f"Mechanism verification: {indicators}; Gate verdict: {verdict}")
    return all_pass, indicators
