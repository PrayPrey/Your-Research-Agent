"""Results aggregation and gate checking."""

import statistics
from config import OVERLAP_THRESHOLD


def aggregate_benchmark(per_item_results: list[dict]) -> dict:
    """Aggregate per-item results to benchmark stats."""
    overlaps = [r["overlap"] for r in per_item_results]
    if not overlaps:
        return {"mean_overlap": 0.0, "median_overlap": 0.0, "max_overlap": 0.0,
                "items_above_1pct": 0, "total_items": 0}
    return {
        "mean_overlap": statistics.mean(overlaps),
        "median_overlap": statistics.median(overlaps),
        "max_overlap": max(overlaps),
        "items_above_1pct": sum(1 for o in overlaps if o > OVERLAP_THRESHOLD),
        "total_items": len(overlaps),
    }


def aggregate_all(results_by_benchmark: dict[str, list[dict]]) -> dict[str, dict]:
    """Aggregate all benchmarks."""
    return {name: aggregate_benchmark(results) for name, results in results_by_benchmark.items()}


def check_gate(aggregated: dict[str, dict], threshold: float = OVERLAP_THRESHOLD) -> dict:
    """Check if gate passes (any benchmark >1% mean overlap)."""
    above = [name for name, stats in aggregated.items() if stats["mean_overlap"] > threshold]
    max_bench = max(aggregated, key=lambda k: aggregated[k]["mean_overlap"]) if aggregated else None
    return {
        "pass": len(above) > 0,
        "benchmarks_above_threshold": above,
        "max_overlap_benchmark": max_bench,
    }
