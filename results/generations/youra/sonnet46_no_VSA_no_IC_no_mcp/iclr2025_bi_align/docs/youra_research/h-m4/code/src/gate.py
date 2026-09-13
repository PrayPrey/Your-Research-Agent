def check_gate(results: dict, beta_min: float = 0.0, p_max: float = 0.05) -> dict:
    gate_pass = (results["slope"] > beta_min) and (results["p_value"] < p_max)
    reason = []
    if results["slope"] <= beta_min:
        reason.append(f"beta={results['slope']:.4f} not > {beta_min}")
    if results["p_value"] >= p_max:
        reason.append(f"p={results['p_value']:.4f} not < {p_max}")
    return {
        "gate_pass": gate_pass,
        "gate_type": "SHOULD_WORK",
        "reason": "All conditions met" if gate_pass else "; ".join(reason),
    }


def compare_with_coste(beta_gao: float, beta_coste: float = 0.1433) -> dict:
    ratio = beta_gao / beta_coste if beta_coste != 0 else float("inf")
    within_order = 0.1 <= abs(ratio) <= 10.0
    return {
        "beta_gao": beta_gao,
        "beta_coste": beta_coste,
        "ratio": ratio,
        "within_order_of_magnitude": within_order,
    }
