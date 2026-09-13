"""Direction-based gate analysis for h-e1-v2 (no ANCOVA required)."""
import logging
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from analyze import load_results  # noqa: E402 - reuse h-e1 CSV loader

logger = logging.getLogger(__name__)


def check_direction_v2(df: pd.DataFrame, dv: str = "hellaswag_acc_norm") -> dict:
    """Compute tau*(14M) and tau*(31M) via argmax; direction_confirmed = tau*(14M) <= tau*(31M)."""
    df14 = df[df["scale"] == 14]
    df31 = df[df["scale"] == 31]

    tau_star_14m = df14.groupby("ppl_threshold")[dv].mean().idxmax()
    tau_star_31m = df31.groupby("ppl_threshold")[dv].mean().idxmax()
    direction_confirmed = bool(tau_star_14m <= tau_star_31m)

    results_14m = df14.groupby("ppl_threshold")[dv].mean().to_dict()
    results_31m = df31.groupby("ppl_threshold")[dv].mean().to_dict()

    # 14M benefits from stricter filtering OR 31M tolerates looser filtering
    interaction_exists = (
        results_14m.get(20, 0) > results_14m.get(50, 0)
        or results_31m.get(50, 0) >= results_31m.get(20, 0)
    )

    all_vals = list(results_14m.values()) + list(results_31m.values())
    above_random = all(v > 0.25 for v in all_vals) if all_vals else False

    return {
        "tau_star_14m": int(tau_star_14m),
        "tau_star_31m": int(tau_star_31m),
        "direction_confirmed": direction_confirmed,
        "interaction_exists": interaction_exists,
        "above_random": above_random,
        "results_14m": results_14m,
        "results_31m": results_31m,
    }


def gate_check_v2(analysis_results: dict) -> dict:
    """Direction-based gate for EXISTENCE PoC. No ANCOVA required."""
    direction = analysis_results.get("direction_confirmed", False)
    above_random = analysis_results.get("above_random", False)
    interaction_exists = analysis_results.get("interaction_exists", False)

    checks = {
        "direction_passes": direction,
        "above_random": above_random,
        "interaction_exists": interaction_exists,
    }
    passed = checks["direction_passes"] and checks["above_random"] and checks["interaction_exists"]

    tau14 = analysis_results.get("tau_star_14m", "?")
    tau31 = analysis_results.get("tau_star_31m", "?")
    reason_parts = []
    if not checks["direction_passes"]:
        reason_parts.append(f"direction FAILED: tau*(14M)={tau14} > tau*(31M)={tau31}")
    if not checks["above_random"]:
        reason_parts.append("some conditions below random (acc_norm <= 0.25)")
    if not checks["interaction_exists"]:
        reason_parts.append("no interaction signal detected")

    return {
        "passed": passed,
        "reason": "PASS" if passed else "FAIL: " + "; ".join(reason_parts),
        "checks": checks,
        "tau_star_14m": tau14,
        "tau_star_31m": tau31,
        "direction_confirmed": direction,
    }


def run_full_analysis_v2(csv_path: str) -> dict:
    """Direction-only analysis for h-e1-v2. No ANCOVA."""
    df = load_results(csv_path)
    logger.info(f"Loaded {len(df)} result rows from {csv_path}")

    direction = check_direction_v2(df, dv="hellaswag_acc_norm")
    gate = gate_check_v2(direction)
    full_results = {**direction, "gate": gate}

    print(f"\n{'='*60}")
    print(f"GATE CHECK RESULT: {'PASS' if gate['passed'] else 'FAIL'}")
    print(f"  tau*(14M)={direction['tau_star_14m']}, tau*(31M)={direction['tau_star_31m']}")
    print(f"  direction: {'confirmed' if direction['direction_confirmed'] else 'NOT confirmed'}")
    print(f"  above_random: {direction['above_random']}")
    print(f"  interaction_exists: {direction['interaction_exists']}")
    print(f"  reason: {gate['reason']}")
    print(f"{'='*60}\n")

    return full_results
