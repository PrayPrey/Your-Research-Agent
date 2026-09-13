# evaluate.py - h-m3: RCI flip rate computation and gate check
from config import CONFIG


def compute_rates(results):
    """
    Compute flip rates for hallucinated vs correct responses.

    Args:
        results: list of dicts with has_flip and is_hallucination

    Returns:
        dict with hallucination_flip_rate, correct_flip_rate, separation
    """
    halluc_flips = [r["has_flip"] for r in results if r["is_hallucination"]]
    correct_flips = [r["has_flip"] for r in results if not r["is_hallucination"]]

    halluc_rate = sum(halluc_flips) / len(halluc_flips) if halluc_flips else 0.0
    correct_rate = sum(correct_flips) / len(correct_flips) if correct_flips else 0.0
    separation = halluc_rate - correct_rate

    return {
        "hallucination_flip_rate": halluc_rate,
        "correct_flip_rate": correct_rate,
        "separation": separation,
        "n_hallucinations": len(halluc_flips),
        "n_correct": len(correct_flips),
        "halluc_flip_count": sum(halluc_flips),
        "correct_flip_count": sum(correct_flips),
    }


def check_gate(rates):
    """
    Check if results pass SHOULD_WORK gate criteria.

    Full pass: halluc_rate >= 0.30 AND correct_rate < 0.10
    PoC pass: halluc_rate > correct_rate (direction only)
    Falsified: halluc_rate < 0.20 OR correct_rate >= 0.15

    Returns:
        dict with pass, poc_pass, falsified, details
    """
    halluc_rate = rates["hallucination_flip_rate"]
    correct_rate = rates["correct_flip_rate"]
    separation = rates["separation"]

    # Full success criteria
    halluc_ok = halluc_rate >= CONFIG["halluc_rate_threshold"]
    correct_ok = correct_rate < CONFIG["correct_rate_threshold"]
    sep_ok = separation >= CONFIG["separation_threshold"]
    full_pass = halluc_ok and correct_ok

    # PoC pass: just need effect in right direction
    poc_pass = halluc_rate > correct_rate

    # Falsification check
    halluc_fail = halluc_rate < CONFIG["halluc_falsification"]
    correct_fail = correct_rate >= CONFIG["correct_falsification"]
    falsified = halluc_fail or correct_fail

    return {
        "pass": full_pass,
        "poc_pass": poc_pass,
        "falsified": falsified,
        "details": {
            "halluc_ok": halluc_ok,
            "correct_ok": correct_ok,
            "sep_ok": sep_ok,
            "halluc_rate": halluc_rate,
            "correct_rate": correct_rate,
            "separation": separation,
        },
    }
