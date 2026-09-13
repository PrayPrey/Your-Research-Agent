"""Gate evaluation for h-c1 SHOULD_WORK condition."""

from config import CONFIG


def check_domain_pass(analysis: dict) -> bool:
    """Domain passes if |r_pearson| > threshold AND r_pearson < 0."""
    thr = CONFIG["success_r_abs_threshold"]
    r = analysis["r_pearson"]
    return abs(r) > thr and r < 0


def check_gate(vision_analysis: dict, nlp_analysis: dict, comparison: dict) -> dict:
    """SHOULD_WORK gate: both domains pass AND consistent direction."""
    v_pass = check_domain_pass(vision_analysis)
    n_pass = check_domain_pass(nlp_analysis)
    consistent = comparison["consistent_direction"]
    should_fail = not consistent
    success = v_pass and n_pass and consistent

    return {
        "success": success,
        "should_fail": should_fail,
        "vision_r": vision_analysis["r_pearson"],
        "nlp_r": nlp_analysis["r_pearson"],
        "consistent_direction": consistent,
        "vision_pass": v_pass,
        "nlp_pass": n_pass,
    }


def summarize(results: dict) -> dict:
    """Flatten key metrics for console output."""
    vision = results["vision"]
    nlp = results["nlp"]
    gate = results["gate"]

    return {
        "vision_n": vision["n"],
        "vision_r": vision["r_pearson"],
        "vision_p": vision["p_pearson"],
        "vision_ci": (vision["ci_95_lower"], vision["ci_95_upper"]),
        "nlp_n": nlp["n"],
        "nlp_r": nlp["r_pearson"],
        "nlp_p": nlp["p_pearson"],
        "nlp_ci": (nlp["ci_95_lower"], nlp["ci_95_upper"]),
        "gate_success": gate["success"],
        "consistent_direction": gate["consistent_direction"],
    }
