"""Localization accuracy measurement for H-M2."""
import math
from typing import List, Dict

from config import U_LINE_ERRORS, U_IGNORE_ERRORS, TOLERANCE_LINES


def _categorize_error(traceback_str: str) -> str:
    """Categorize error as U_line or U_ignore using h-m2 sets."""
    for err in U_LINE_ERRORS:
        if err in traceback_str:
            return "U_line"
    for err in U_IGNORE_ERRORS:
        if err in traceback_str:
            return "U_ignore"
    return "unknown"


def is_accurate(traceback_line: int, actual_line: int, tolerance: int = TOLERANCE_LINES) -> bool:
    """Check if traceback line is within tolerance of actual bug line."""
    if traceback_line is None or actual_line is None:
        return False
    return abs(traceback_line - actual_line) <= tolerance


def _wilson_ci(correct: int, n: int, confidence: float = 0.95) -> tuple:
    """Wilson score confidence interval for binomial proportion."""
    if n == 0:
        return 0.0, 0.0

    z = 1.96 if confidence == 0.95 else 1.645
    p = correct / n

    denom = 1 + z*z / n
    center = (p + z*z / (2*n)) / denom
    margin = z * math.sqrt((p*(1-p) + z*z/(4*n)) / n) / denom

    return max(0, center - margin), min(1, center + margin)


def compute_category_accuracy(samples: List[Dict]) -> Dict[str, Dict]:
    """Compute accuracy per category (U_line vs U_ignore)."""
    results = {
        "U_line": {"correct": 0, "n": 0},
        "U_ignore": {"correct": 0, "n": 0}
    }

    for sample in samples:
        category = _categorize_error(sample.get("traceback", ""))
        if category not in results:
            continue

        tb_line = sample.get("error_line")
        actual_line = sample.get("actual_bug_line")

        if tb_line is None or actual_line is None:
            continue

        results[category]["n"] += 1
        if is_accurate(tb_line, actual_line):
            results[category]["correct"] += 1

    for cat in results:
        n = results[cat]["n"]
        correct = results[cat]["correct"]
        results[cat]["accuracy"] = correct / n if n > 0 else 0.0
        ci_low, ci_high = _wilson_ci(correct, n)
        results[cat]["ci_low"] = ci_low
        results[cat]["ci_high"] = ci_high

    return results


def compute_distance_distribution(samples: List[Dict]) -> Dict[str, List[int]]:
    """Compute distance distribution per category."""
    results = {"U_line": [], "U_ignore": []}

    for sample in samples:
        category = _categorize_error(sample.get("traceback", ""))
        if category not in results:
            continue

        tb_line = sample.get("error_line")
        actual_line = sample.get("actual_bug_line")

        if tb_line is None or actual_line is None:
            continue

        distance = abs(tb_line - actual_line)
        results[category].append(distance)

    return results


def compute_per_exception_breakdown(samples: List[Dict]) -> Dict[str, Dict]:
    """Compute accuracy per specific exception type."""
    breakdown = {}

    for sample in samples:
        exc_type = sample.get("error_type_specific", "Unknown")
        if exc_type not in breakdown:
            breakdown[exc_type] = {"correct": 0, "n": 0}

        tb_line = sample.get("error_line")
        actual_line = sample.get("actual_bug_line")

        if tb_line is None or actual_line is None:
            continue

        breakdown[exc_type]["n"] += 1
        if is_accurate(tb_line, actual_line):
            breakdown[exc_type]["correct"] += 1

    for exc in breakdown:
        n = breakdown[exc]["n"]
        correct = breakdown[exc]["correct"]
        breakdown[exc]["accuracy"] = correct / n if n > 0 else 0.0

    return dict(sorted(breakdown.items(), key=lambda x: -x[1]["n"]))
