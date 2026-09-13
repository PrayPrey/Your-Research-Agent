"""Metrics computation for H-M2 hedging analysis."""
from collections import Counter
from config import CONFIG

THRESHOLD = CONFIG["hedging"]["presence_rate_threshold"]


def compute_metrics(results: list[dict]) -> dict:
    """Compute hedging metrics from analysis results.

    Args:
        results: List of per-item analysis dicts with has_hedging, total_count.

    Returns:
        Dict with hedging_presence_rate, mean_hedging_count, n_samples, gate_pass.
    """
    n = len(results)
    if n == 0:
        return {"hedging_presence_rate": 0.0, "mean_hedging_count": 0.0, "n_samples": 0, "gate_pass": False}

    hedging_present = sum(1 for r in results if r["has_hedging"])
    total_markers = sum(r["total_count"] for r in results)
    rate = hedging_present / n

    return {
        "hedging_presence_rate": rate,
        "mean_hedging_count": total_markers / n,
        "n_samples": n,
        "gate_pass": rate > THRESHOLD,
    }


def marker_frequency_distribution(results: list[dict]) -> dict:
    """Aggregate marker frequencies across all results.

    Args:
        results: List of per-item analysis dicts with markers_found.

    Returns:
        Dict of marker -> total count, sorted desc.
    """
    counter = Counter()
    for r in results:
        counter.update(r["markers_found"])
    return dict(counter.most_common())


def check_gate(metrics: dict) -> dict:
    """Check SHOULD_WORK gate status.

    Args:
        metrics: Output from compute_metrics.

    Returns:
        Gate status dict.
    """
    status = "PASS" if metrics["gate_pass"] else "EXPLORE"
    return {
        "gate": "SHOULD_WORK",
        "status": status,
        "threshold": THRESHOLD,
        "actual": metrics["hedging_presence_rate"],
    }
