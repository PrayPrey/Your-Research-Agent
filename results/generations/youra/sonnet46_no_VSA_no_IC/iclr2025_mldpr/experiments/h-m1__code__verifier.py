"""verifier.py — Gate check for H-M1 mechanism activation."""
from __future__ import annotations
from typing import Tuple, Dict

from analyzer import AnalysisResults


def verify_mechanism_activated(
    results: AnalysisResults,
) -> Tuple[bool, Dict[str, bool]]:
    """Gate check: p_one_tailed < 0.10 AND variance_ratio_pre_global > 1.0.

    Returns:
        (activated, indicators) where indicators keys:
        pre_var_computed, global_var_computed, ratio_above_one,
        f_stat_computed, p_value_computed
    """
    indicators = {
        "pre_var_computed": results.get("pre_variance") is not None,
        "global_var_computed": results.get("global_variance") is not None,
        "ratio_above_one": results.get("variance_ratio_pre_global", 0.0) > 1.0,
        "f_stat_computed": results.get("F_stat") is not None,
        "p_value_computed": results.get("p_one_tailed") is not None,
    }

    p = results.get("p_one_tailed", 1.0)
    ratio = results.get("variance_ratio_pre_global", 0.0)
    gate_passed = (p < 0.10) and (ratio > 1.0)

    print(f"GATE: {'PASS' if gate_passed else 'FAIL'} (p={p:.4f}, ratio={ratio:.4f})")

    return gate_passed, indicators
