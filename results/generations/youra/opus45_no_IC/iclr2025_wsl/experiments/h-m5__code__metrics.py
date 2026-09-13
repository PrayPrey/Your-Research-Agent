"""H-M5: R² metrics and gate logic per PRD gate table."""

import numpy as np
from sklearn.metrics import r2_score
from typing import Dict, Tuple


H_M4_BASELINE = {
    "r2": 0.0036,
    "invariance": 0.9193,
}


def compute_r2(y_true, y_pred) -> float:
    """Compute R² score using sklearn."""
    return float(r2_score(y_true, y_pred))


def compare_with_baseline(
    mlp_r2: float,
    mlp_invariance: float,
    baseline: Dict = None,
) -> Dict:
    """Compare H-M5 results with H-M4 baseline values."""
    if baseline is None:
        baseline = H_M4_BASELINE

    return {
        "h_m4_r2": baseline["r2"],
        "h_m5_r2": mlp_r2,
        "r2_improvement": mlp_r2 - baseline["r2"],
        "h_m4_invariance": baseline["invariance"],
        "h_m5_invariance": mlp_invariance,
        "invariance_delta": mlp_invariance - baseline["invariance"],
    }


def gate_logic(
    test_r2: float,
    mean_invariance: float,
    r2_threshold: float = 0.1,
    invariance_threshold: float = 0.8,
) -> Tuple[str, str]:
    """Gate logic per PRD.

    Returns:
        (status, reason)
        status: "PASS", "FAIL", or "INCONCLUSIVE"
    """
    if test_r2 < r2_threshold:
        return (
            "INCONCLUSIVE",
            f"MLP R² ({test_r2:.4f}) < {r2_threshold} - need better training"
        )
    elif mean_invariance > invariance_threshold:
        return (
            "PASS",
            f"Invariance ({mean_invariance:.4f}) > {invariance_threshold} - MLP learned invariance from data"
        )
    else:
        return (
            "FAIL",
            f"Invariance ({mean_invariance:.4f}) <= {invariance_threshold} - MLP learns but NOT invariance"
        )


if __name__ == "__main__":
    status, reason = gate_logic(test_r2=0.5, mean_invariance=0.85)
    print(f"Status: {status}")
    print(f"Reason: {reason}")

    comparison = compare_with_baseline(mlp_r2=0.5, mlp_invariance=0.85)
    print(f"\nBaseline comparison: {comparison}")
