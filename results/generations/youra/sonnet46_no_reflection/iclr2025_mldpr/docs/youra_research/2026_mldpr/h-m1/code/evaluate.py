"""H-M1: Evaluate — mechanism verification, gate check, results saving.
NOTE: Different signatures from H-E1 evaluate.py — do NOT import from H-E1.
"""
import json
import os
import numpy as np
import pandas as pd


def verify_mechanism_activated(
    panel_df: pd.DataFrame,
    granger_results: dict,
    spearman_result: dict,
) -> tuple:
    """Check all H-M1 mechanism activation criteria.
    Returns: (activated: bool, indicators: dict)
    """
    rho = spearman_result.get("rho")
    rho_p = spearman_result.get("p_value")
    valid_granger = {k: v for k, v in granger_results.items() if v is not None}

    indicators = {
        "panel_constructed": len(panel_df) >= 200,
        "sufficient_benchmarks": len(valid_granger) >= 30,
        "spearman_computed": rho is not None and not (isinstance(rho, float) and np.isnan(rho)),
        "granger_computed": len(valid_granger) > 0,
        "spearman_significant": (
            rho is not None and not np.isnan(rho) and rho > 0.4 and
            rho_p is not None and not np.isnan(rho_p) and rho_p < 0.05
        ),
        "granger_significant_lag2": any(
            v.get(2, 1.0) < 0.05 for v in valid_granger.values()
        ),
    }
    activated = (
        indicators["panel_constructed"]
        and indicators["sufficient_benchmarks"]
        and (indicators["spearman_significant"] or indicators["granger_significant_lag2"])
    )
    return activated, indicators


def check_gate_condition(
    spearman_result: dict,
    granger_agg: dict,
) -> tuple:
    """PASS if Spearman rho>0.4 AND p<0.05, OR Granger p<0.05 at lag=2.
    Returns: (gate_passed: bool, gate_details: dict)
    """
    rho = spearman_result.get("rho", 0.0) or 0.0
    rho_p = spearman_result.get("p_value", 1.0) or 1.0
    min_p_lag2 = granger_agg.get("min_p_lag2") or 1.0

    spearman_pass = float(rho) > 0.4 and float(rho_p) < 0.05
    granger_pass = float(min_p_lag2) < 0.05

    gate_passed = spearman_pass or granger_pass
    gate_details = {
        "gate_passed": gate_passed,
        "spearman_pass": spearman_pass,
        "granger_pass": granger_pass,
        "spearman_rho": rho,
        "spearman_p": rho_p,
        "granger_min_p_lag2": min_p_lag2,
        "gate_type": "MUST_WORK",
        "criteria": "Spearman rho>0.4 AND p<0.05 OR Granger p<0.05 at lag=2",
    }
    return gate_passed, gate_details


def save_results(results: dict, output_path: str) -> None:
    """Serialize results dict to JSON with numpy type handling."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    def _convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(i) for i in obj]
        return obj

    with open(output_path, "w") as f:
        json.dump(_convert(results), f, indent=2)
    print(f"Results saved to {output_path}")
