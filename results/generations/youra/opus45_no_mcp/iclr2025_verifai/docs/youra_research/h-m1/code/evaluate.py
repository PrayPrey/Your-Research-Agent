"""H-M1: Gate evaluation for structural coverage."""

def evaluate_gate(structural_coverage: float, threshold: float = 0.60) -> dict:
    """Evaluate H-M1 gate condition.

    Returns {passed, metric, threshold, message}
    """
    return {
        "passed": structural_coverage > threshold,
        "metric": structural_coverage,
        "threshold": threshold,
        "message": f"Structural coverage: {structural_coverage:.1%} (threshold: >{threshold:.0%})"
    }
