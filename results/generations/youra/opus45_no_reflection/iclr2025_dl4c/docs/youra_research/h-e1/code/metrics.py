"""Metrics computation for EVAF H-E1."""

from collections import Counter


def compute_metrics(results: list[dict]) -> dict:
    """Compute EVAF metrics from pipeline results."""
    if not results:
        return {
            "accept_rate": 0.0,
            "coverage": 0.0,
            "rejection_breakdown": {},
            "total_problems": 0,
            "accepted_count": 0,
            "actionable_count": 0,
        }

    total = len(results)
    accepted = sum(1 for r in results if r.get("accepted", False))
    actionable = sum(1 for r in results if r.get("has_code_suggestion", False))

    rejection_reasons = [r.get("rejection_reason") for r in results
                        if not r.get("accepted", False) and r.get("rejection_reason")]
    rejection_breakdown = dict(Counter(rejection_reasons))

    return {
        "accept_rate": accepted / total,
        "coverage": actionable / total,
        "rejection_breakdown": rejection_breakdown,
        "total_problems": total,
        "accepted_count": accepted,
        "actionable_count": actionable,
    }
