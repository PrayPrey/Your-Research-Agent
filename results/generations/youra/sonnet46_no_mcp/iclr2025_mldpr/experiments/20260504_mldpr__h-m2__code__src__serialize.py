"""H-M2 serialization: results.json and gate_result.json."""
import json
import os
import logging

logger = logging.getLogger(__name__)


def build_results_dict(primary_mwu: dict, unadjusted_mwu: dict, ols_results: dict, matching_meta: dict, ablations: dict) -> dict:
    """Build full results dictionary."""
    return {
        "hypothesis": "h-m2",
        "primary_mwu_matched": primary_mwu,
        "unadjusted_mwu": unadjusted_mwu,
        "ols_standardized": ols_results,
        "matching": matching_meta,
        "ablations": ablations,
    }


def save_results(results: dict, path: str):
    """Save results.json."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"Saved results to {path}")


def save_gate_result(results: dict, path: str, mwu_alpha: float = 0.05, beta_gate: float = 0.10):
    """Save gate_result.json with SHOULD_WORK schema."""
    primary = results.get("primary_mwu_matched", {})
    ols = results.get("ols_standardized", {})

    primary_pass = primary.get("p_value", 1.0) < mwu_alpha
    direction_pass = primary.get("direction_pass", False)
    accessible_beta = ols.get("accessible_beta", 0.0)
    secondary_pass = abs(accessible_beta) > beta_gate

    gate_passed = primary_pass and direction_pass

    gate_result = {
        "hypothesis": "h-m2",
        "gate_type": "SHOULD_WORK",
        "gate_passed": gate_passed,
        "criteria": {
            "primary_mwu_p": primary.get("p_value"),
            "primary_pass": primary_pass,
            "direction_pass": direction_pass,
            "accessible_beta": accessible_beta,
            "secondary_pass": secondary_pass,
            "mwu_alpha": mwu_alpha,
            "beta_gate": beta_gate,
        },
        "matching": results.get("matching", {}),
        "note": "SHOULD_WORK gate: failure does NOT stop pipeline",
    }

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(gate_result, f, indent=2, default=str)
    logger.info(f"Gate result: passed={gate_passed}, saved to {path}")
    return gate_result
