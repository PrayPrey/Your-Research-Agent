"""H-M1: Coverage metrics for structural error analysis."""
from typing import List, Dict

def compute_structural_coverage(per_problem_results: List[dict]) -> dict:
    """Filter to problems with exec_errors (test-failing), compute coverage.

    Returns {structural_coverage: float, n_failing: int, n_structural: int}
    """
    failing = [r for r in per_problem_results if len(r.get("exec_errors", [])) > 0]
    structural_count = sum(1 for r in failing if r.get("has_structural", False))
    coverage = structural_count / len(failing) if failing else 0.0
    return {
        "structural_coverage": coverage,
        "n_failing": len(failing),
        "n_structural": structural_count
    }

def error_category_distribution(per_problem_results: List[dict]) -> Dict[str, int]:
    """Count occurrences per structural category across all problems."""
    counts = {}
    for r in per_problem_results:
        for code, category in r.get("structural", []):
            counts[category] = counts.get(category, 0) + 1
    return counts

def per_benchmark_breakdown(per_problem_results: List[dict]) -> dict:
    """Returns per-benchmark coverage metrics."""
    out = {}
    for bench in ("humaneval", "mbpp"):
        subset = [r for r in per_problem_results if r.get("benchmark") == bench]
        out[bench] = compute_structural_coverage(subset)
    return out
