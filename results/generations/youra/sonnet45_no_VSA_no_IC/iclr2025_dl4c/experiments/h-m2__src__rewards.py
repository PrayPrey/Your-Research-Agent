"""Reward functions for h-m2 (error+trace granularity)."""

import bisect
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

ERROR_TYPES = ["SyntaxError", "TypeError", "NameError", "IndexError", "ValueError", "AttributeError", "KeyError"]
STACK_DEPTH_BUCKETS = [0, 1, 2, 3, 5, 10, 20, 50, 100, 200, float('inf')]

def parse_stack_depth(traceback: str) -> int:
    """Extract stack trace depth (line count in traceback)."""
    if traceback is None or traceback.strip() == "":
        return 0
    return len([line for line in traceback.strip().split('\n') if line.strip()])

def compute_error_trace_reward(execution_result: dict) -> float:
    """
    Compute error+trace reward (5.6 bits total).

    Args:
        execution_result: {passed: bool, error: str, traceback: str}

    Returns:
        float in [0.0, 1.0]
    """
    if execution_result.get("passed", False):
        return 1.0

    error = execution_result.get("error", "")
    traceback = execution_result.get("traceback", "")

    # Error type component (2.3 bits → 8 types)
    error_reward = 0.0
    for idx, error_type in enumerate(ERROR_TYPES):
        if error_type in error:
            error_reward = (idx + 1) / len(ERROR_TYPES)
            break

    # Stack depth component (3.3 bits → 10 buckets)
    depth = parse_stack_depth(traceback)
    bucket_idx = bisect.bisect_right(STACK_DEPTH_BUCKETS, depth) - 1
    depth_reward = bucket_idx / (len(STACK_DEPTH_BUCKETS) - 1)

    # Combined reward (weighted average)
    combined_reward = 0.4 * error_reward + 0.6 * depth_reward

    if combined_reward < 0.0 or combined_reward > 1.0:
        logger.warning(f"Reward {combined_reward:.3f} out of bounds. Clipping.")
        combined_reward = max(0.0, min(1.0, combined_reward))

    return combined_reward
