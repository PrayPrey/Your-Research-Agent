"""H-M2: Behavioral error detection and categorization."""
from typing import Set

BEHAVIORAL_CATEGORIES: dict = {
    "wrong_output": [
        "AssertionError", "Expected", "expected", "!=", "assert", "wrong_answer"
    ],
    "runtime_exception": [
        "TypeError", "ValueError", "IndexError", "KeyError",
        "AttributeError", "ZeroDivisionError", "RuntimeError",
        "NameError", "runtime_error"
    ],
    "timeout": [
        "timeout", "Timeout", "TimeoutError", "time limit", "timed out"
    ],
    "edge_case": []
}


def is_static_clean(static_errors: set) -> bool:
    """Return True if code has zero static analysis errors."""
    return len(static_errors) == 0


def categorize_test_failure(exec_errors: Set[str]) -> str:
    """Categorize test failure into: wrong_output, runtime_exception, timeout, edge_case."""
    if not exec_errors:
        return None

    error_str = " ".join(exec_errors)

    for category in ["wrong_output", "runtime_exception", "timeout"]:
        for keyword in BEHAVIORAL_CATEGORIES[category]:
            if keyword in error_str:
                return category

    return "edge_case"
