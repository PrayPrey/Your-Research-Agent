"""Gate evaluation for H-M2: Sharpness ratio check"""

import math
from config import GATE_THRESHOLD


def evaluate_gate(compare_result: dict, threshold: float = None) -> dict:
    """
    Evaluate gate: ratio < threshold -> PASS.
    Returns {'ratio', 'pass', 'sequential_sharpness', 'retrieval_sharpness'}
    """
    if threshold is None:
        threshold = GATE_THRESHOLD

    ratio = compare_result["ratio"]
    pass_gate = ratio < threshold

    return {
        "ratio": ratio,
        "pass": pass_gate,
        "threshold": threshold,
        "sequential_sharpness": compare_result["sequential_sharpness"],
        "retrieval_sharpness": compare_result["retrieval_sharpness"],
    }


def verify_mechanism(compare_result: dict) -> tuple:
    """
    Checks:
    - both sharpness values computed (not None/nan)
    - |seq - ret| > 0.01 (tasks differentiated)
    - 0 < ratio < 10 (sane range)
    Returns (passed: bool, message: str)
    """
    seq = compare_result["sequential_sharpness"]
    ret = compare_result["retrieval_sharpness"]
    ratio = compare_result["ratio"]

    checks = []

    if seq is None or (isinstance(seq, float) and math.isnan(seq)):
        checks.append("Sequential sharpness not computed")
    if ret is None or (isinstance(ret, float) and math.isnan(ret)):
        checks.append("Retrieval sharpness not computed")

    if abs(seq - ret) <= 0.01:
        checks.append(f"Tasks not differentiated: |{seq:.4f} - {ret:.4f}| <= 0.01")

    if not (0 < ratio < 10):
        checks.append(f"Ratio out of sane range: {ratio:.4f} not in (0, 10)")

    if checks:
        return False, "; ".join(checks)

    return True, "Mechanism verification passed"
