def evaluate_gate(
    rho: float,
    p_value: float,
    ci_lower: float,
    fwl_delta: float,
) -> dict:
    """
    Gate: rho > 0 AND p_value < 0.05 AND ci_lower > 0.
    Returns: {passes_gate, fwl_consistent, gate_reason}
    """
    passes_gate = (rho > 0) and (p_value < 0.05) and (ci_lower > 0)
    fwl_consistent = (fwl_delta < 0.02)
    if passes_gate:
        gate_reason = f"rho={rho:.4f}>0, p={p_value:.2e}<0.05, CI_lower={ci_lower:.4f}>0"
    else:
        parts = []
        if rho <= 0:
            parts.append(f"rho={rho:.4f}<=0")
        if p_value >= 0.05:
            parts.append(f"p={p_value:.4f}>=0.05")
        if ci_lower <= 0:
            parts.append(f"CI_lower={ci_lower:.4f}<=0")
        gate_reason = "FAILED: " + "; ".join(parts)
    return {
        'passes_gate': passes_gate,
        'fwl_consistent': fwl_consistent,
        'gate_reason': gate_reason,
    }
