"""AST validation with timing instrumentation."""

import ast
import time
from typing import Tuple
import numpy as np


def validate_syntax_timed(code: str) -> Tuple[bool, float]:
    """
    Validate Python syntax using AST parsing and measure latency.

    Args:
        code: Python code string to validate

    Returns:
        (is_valid, elapsed_ms): Validity status and parse time in milliseconds
    """
    start = time.perf_counter()
    try:
        ast.parse(code)
        valid = True
    except SyntaxError:
        valid = False
    elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
    return valid, elapsed


def compute_latency_stats(timings: list) -> dict:
    """
    Compute latency statistics.

    Args:
        timings: List of parse times in milliseconds

    Returns:
        Dictionary with mean, median, p95, and max latency
    """
    arr = np.array(timings)
    return {
        'mean': float(np.mean(arr)),
        'median': float(np.median(arr)),
        'p95': float(np.percentile(arr, 95)),
        'max': float(np.max(arr))
    }
