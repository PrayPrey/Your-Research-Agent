"""Aggregation functions for token log-prob sequences."""
import numpy as np
from typing import List, Dict, Tuple


def aggregate(logprobs: List[float], method: str) -> float:
    """
    Aggregate token log-prob sequence to scalar.

    Args:
        logprobs: list of float, all <= 0, length >= 1
        method: one of 'min', 'mean', 'sum'

    Returns:
        float (not negated; negation done in compute_all_scores)
    """
    if not logprobs:
        raise ValueError("empty logprobs")
    lp = np.array(logprobs)
    if method == "min":
        return float(np.min(lp))
    elif method == "mean":
        return float(np.mean(lp))
    elif method == "sum":
        return float(np.sum(lp))
    raise ValueError(f"Unknown method: {method}. Must be one of: min, mean, sum")


def compute_all_scores(
    records: List[Dict],
) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """
    Compute negated aggregation scores and labels for all three methods.

    Returns:
        {method: (scores, labels)} where:
            scores: np.ndarray shape (N,), negated (higher = more uncertain)
            labels: np.ndarray shape (N,), int (1=correct, 0=hallucinated)
    """
    labels = np.array([r["label"] for r in records], dtype=int)
    results = {}
    for method in ["min", "mean", "sum"]:
        raw = np.array([aggregate(r["logprobs"], method) for r in records])
        scores = -raw  # negate: higher = more uncertain = predicted hallucinated
        results[method] = (scores, labels)
    return results
