"""Gate metric computation for h-e1 prescreening validation."""
import logging
import numpy as np

logger = logging.getLogger(__name__)


def compute_variance_ratio_per_group(
    r_ratio_vec: list[float],
    r_binary_vec: list[float],
    eps: float = 1e-8,
) -> float | None:
    """Compute var(r_ratio) / var(r_binary).

    Args:
        r_ratio_vec: length k=8, values in [0, 1].
        r_binary_vec: length k=8, values in {0.0, 1.0}.
        eps: denominator guard threshold.

    Returns:
        variance ratio as float, or None if var_binary <= eps (degenerate group).
    """
    arr_ratio = np.array(r_ratio_vec, dtype=np.float64)
    arr_binary = np.array(r_binary_vec, dtype=np.float64)

    var_ratio = float(np.var(arr_ratio))    # population variance (ddof=0)
    var_binary = float(np.var(arr_binary))

    if var_binary <= eps:
        return None   # degenerate group (all-pass or all-fail): excluded

    return var_ratio / var_binary


def compute_gate_metrics(
    per_problem_results: list[dict],
    threshold_pass_ge1: float = 0.10,
    threshold_pct_above: float = 0.80,
    variance_ratio_threshold: float = 1.5,
) -> dict:
    """Aggregate per-problem stats into gate metrics dict.

    Args:
        per_problem_results: list of dicts with keys:
            problem_id, s_term, r_ratio_vec [k], r_binary_vec [k],
            tests_passed_vec [k], T
        threshold_pass_ge1: gate threshold for fraction_k_pass_ge1.
        threshold_pct_above: gate threshold for pct_groups_above_1_5x.
        variance_ratio_threshold: variance ratio threshold for gate.

    Returns:
        dict with gate metrics.
    """
    fraction_k_pass_ge1_list = []
    variance_ratios = []

    for row in per_problem_results:
        r_ratio_vec = row["r_ratio_vec"]
        r_binary_vec = row["r_binary_vec"]
        tests_passed_vec = row["tests_passed_vec"]

        # Handle JSON-encoded strings (from CSV deserialization)
        if isinstance(r_ratio_vec, str):
            import json
            r_ratio_vec = json.loads(r_ratio_vec)
        if isinstance(r_binary_vec, str):
            import json
            r_binary_vec = json.loads(r_binary_vec)
        if isinstance(tests_passed_vec, str):
            import json
            tests_passed_vec = json.loads(tests_passed_vec)

        # Metric (a): at least one partial pass
        k_pass_ge1 = float(any(tp >= 1 for tp in tests_passed_vec))
        fraction_k_pass_ge1_list.append(k_pass_ge1)

        # Metric (b): variance ratio
        vr = compute_variance_ratio_per_group(r_ratio_vec, r_binary_vec)
        if vr is not None:
            variance_ratios.append(vr)

    fraction_k_pass_ge1 = float(np.mean(fraction_k_pass_ge1_list)) if fraction_k_pass_ge1_list else 0.0
    mean_var_ratio = float(np.mean(variance_ratios)) if variance_ratios else 0.0
    pct_groups_above_1_5x = float(
        np.mean([vr >= variance_ratio_threshold for vr in variance_ratios])
    ) if variance_ratios else 0.0

    gate_pass = (
        fraction_k_pass_ge1 >= threshold_pass_ge1
        and pct_groups_above_1_5x >= threshold_pct_above
    )

    return {
        "fraction_k_pass_ge1": fraction_k_pass_ge1,
        "mean_var_ratio": mean_var_ratio,
        "pct_groups_above_1_5x": pct_groups_above_1_5x,
        "gate_pass": gate_pass,
        "n_problems": len(per_problem_results),
        "n_non_degenerate_groups": len(variance_ratios),
    }


def check_gate(metrics: dict) -> tuple[bool, str]:
    """Return (gate_pass, message) based on threshold checks.

    Args:
        metrics: output of compute_gate_metrics().

    Returns:
        (gate_pass, human-readable message).
    """
    gate_pass = metrics.get("gate_pass", False)
    frac = metrics.get("fraction_k_pass_ge1", 0.0)
    pct = metrics.get("pct_groups_above_1_5x", 0.0)
    mean_vr = metrics.get("mean_var_ratio", 0.0)
    n = metrics.get("n_problems", 0)
    n_nd = metrics.get("n_non_degenerate_groups", 0)

    status = "PASS" if gate_pass else "FAIL"
    msg = (
        f"Gate {status}: "
        f"fraction_k_pass_ge1={frac:.3f} (threshold>=0.10), "
        f"pct_groups_above_1.5x={pct:.3f} (threshold>=0.80), "
        f"mean_var_ratio={mean_vr:.3f}, "
        f"n_problems={n}, n_non_degenerate_groups={n_nd}"
    )
    return gate_pass, msg
