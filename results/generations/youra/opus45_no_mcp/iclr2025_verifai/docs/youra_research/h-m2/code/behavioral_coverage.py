"""H-M2: Behavioral coverage computation."""
from typing import List, Dict


def compute_behavioral_rate(per_problem_results: List[dict]) -> dict:
    """Compute behavioral error rate among static-clean code.

    Returns:
        {behavioral_rate: float, static_clean_count: int, behavioral_failures: int}
    """
    static_clean = [r for r in per_problem_results if r.get("is_static_clean")]
    failures = [r for r in static_clean if r.get("has_behavioral_failure")]

    rate = len(failures) / len(static_clean) if static_clean else 0.0

    return {
        "behavioral_rate": rate,
        "static_clean_count": len(static_clean),
        "behavioral_failures": len(failures)
    }


def failure_category_distribution(per_problem_results: List[dict]) -> Dict[str, int]:
    """Count failures by category among static-clean problems."""
    counts = {"wrong_output": 0, "runtime_exception": 0, "timeout": 0, "edge_case": 0}

    static_clean = [r for r in per_problem_results if r.get("is_static_clean")]
    for r in static_clean:
        if r.get("has_behavioral_failure") and r.get("failure_category"):
            cat = r["failure_category"]
            if cat in counts:
                counts[cat] += 1

    return counts


def per_benchmark_breakdown(per_problem_results: List[dict]) -> dict:
    """Compute behavioral rates split by benchmark."""
    humaneval = [r for r in per_problem_results if "humaneval" in r.get("benchmark", "").lower()]
    mbpp = [r for r in per_problem_results if "mbpp" in r.get("benchmark", "").lower()]

    return {
        "humaneval_plus": compute_behavioral_rate(humaneval),
        "mbpp_plus": compute_behavioral_rate(mbpp)
    }
