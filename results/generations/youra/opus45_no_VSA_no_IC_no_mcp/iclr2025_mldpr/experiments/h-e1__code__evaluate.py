"""Evaluation and gate checking for DNSI experiment."""

from config import CONFIG
from metrics import validate_dnsi


def compute_success_rate(results: dict[str, float | None]) -> float:
    """Compute fraction of benchmarks with valid DNSI."""
    if not results:
        return 0.0
    valid_count = sum(1 for v in results.values() if validate_dnsi(v))
    return valid_count / len(results)


def check_gate(results: dict[str, float | None], threshold: float | None = None) -> bool:
    """Check if MUST_WORK gate is satisfied (>50% success rate)."""
    if threshold is None:
        threshold = CONFIG["success_rate_threshold"]
    return compute_success_rate(results) > threshold


def summarize(results: dict) -> dict:
    """Generate summary statistics for DNSI computation results."""
    dnsi_values = results.get("dnsi", {})

    valid_values = [v for v in dnsi_values.values() if validate_dnsi(v)]
    invalid_count = len(dnsi_values) - len(valid_values)

    summary = {
        "total_benchmarks": len(dnsi_values),
        "valid_count": len(valid_values),
        "invalid_count": invalid_count,
        "success_rate": compute_success_rate(dnsi_values),
        "gate_passed": check_gate(dnsi_values),
        "threshold": CONFIG["success_rate_threshold"],
    }

    if valid_values:
        import numpy as np
        summary["dnsi_mean"] = float(np.mean(valid_values))
        summary["dnsi_std"] = float(np.std(valid_values))
        summary["dnsi_min"] = float(min(valid_values))
        summary["dnsi_max"] = float(max(valid_values))

    return summary
