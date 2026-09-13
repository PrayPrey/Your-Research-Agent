"""H-M2 analysis: per-category repair rate differential computation."""

import logging

logger = logging.getLogger(__name__)


def compute_differential(results_a: list, results_b: list) -> dict:
    """
    Compute repair rate differential between Condition B and Condition A,
    split by type-error vs non-type-error problems.

    Category assignment:
      type_error: initial_mypy_errors > 0 (mypy detects error before any repair)
      non_type_error: initial_mypy_errors == 0 AND final_passed==False at round 1

    Args:
        results_a: list of dicts from run_condition_a (164 problems)
        results_b: list of dicts from run_condition_b (164 problems)

    Returns:
        dict with per-category repair rates and differential
    """
    # Index by task_id
    a_by_id = {r["task_id"]: r for r in results_a}
    b_by_id = {r["task_id"]: r for r in results_b}

    all_ids = set(a_by_id) | set(b_by_id)

    type_error_ids = set()
    non_type_error_ids = set()

    for tid in all_ids:
        a = a_by_id.get(tid)
        b = b_by_id.get(tid)
        # Use Condition A's initial_mypy_errors for labeling (same initial generation)
        # Fall back to Condition B if A not available
        initial_errors = 0
        if a:
            initial_errors = a.get("initial_mypy_errors", 0)
        elif b:
            initial_errors = b.get("initial_mypy_errors", 0)

        if initial_errors > 0:
            type_error_ids.add(tid)
        else:
            non_type_error_ids.add(tid)

    def repair_rate(results_dict: dict, id_set: set) -> float:
        subset = [results_dict[tid] for tid in id_set if tid in results_dict]
        if not subset:
            return 0.0
        passed = sum(1 for r in subset if r.get("final_passed", False))
        return passed / len(subset)

    rate_a_type = repair_rate(a_by_id, type_error_ids)
    rate_b_type = repair_rate(b_by_id, type_error_ids)
    rate_a_non = repair_rate(a_by_id, non_type_error_ids)
    rate_b_non = repair_rate(b_by_id, non_type_error_ids)

    delta_type = rate_b_type - rate_a_type
    delta_non = rate_b_non - rate_a_non
    differential = delta_type - delta_non

    logger.info(
        f"[H-M2] type_delta={delta_type:.3f}, non_type_delta={delta_non:.3f}, "
        f"differential={differential:.3f}"
    )

    mechanism_active = differential > 0 and delta_type > delta_non
    logger.info(f"Mechanism activated: {mechanism_active}")

    return {
        "type_error": {
            "n": len(type_error_ids),
            "rate_A": rate_a_type,
            "rate_B": rate_b_type,
            "delta": delta_type,
        },
        "non_type_error": {
            "n": len(non_type_error_ids),
            "rate_A": rate_a_non,
            "rate_B": rate_b_non,
            "delta": delta_non,
        },
        "differential": differential,
        "mechanism_activated": mechanism_active,
        "gate_passed": differential > 0,
    }


def per_round_repair_rates(results: list, id_set: set) -> dict:
    """Compute cumulative repair rate by round for a subset of problems."""
    by_id = {r["task_id"]: r for r in results}
    subset = {tid: by_id[tid] for tid in id_set if tid in by_id}
    if not subset:
        return {}
    rounds = {}
    for k in range(1, 6):
        passed = sum(
            1 for r in subset.values()
            if any(rd["exec_passed"] for rd in r["rounds"] if rd["round"] <= k)
        )
        rounds[k] = passed / len(subset)
    return rounds
