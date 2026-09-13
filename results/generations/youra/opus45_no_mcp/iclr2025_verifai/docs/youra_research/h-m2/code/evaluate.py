"""H-M2: Gate evaluation."""


def evaluate_gate(behavioral_rate: float, threshold: float = 0.40) -> dict:
    """Evaluate SHOULD_WORK gate: behavioral_rate > threshold."""
    passed = behavioral_rate > threshold
    return {
        "passed": passed,
        "metric": behavioral_rate,
        "threshold": threshold,
        "message": f"Behavioral rate {behavioral_rate:.1%} {'>' if passed else '<='} {threshold:.0%}"
    }
