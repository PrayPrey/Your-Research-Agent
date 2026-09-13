"""Token log-prob aggregation functions for H-M2."""
import numpy as np
from typing import Dict, List


def min_score(lp: np.ndarray) -> float:
    return float(np.min(lp))


def mean_score(lp: np.ndarray) -> float:
    return float(np.mean(lp))


def raw_sum(lp: np.ndarray) -> float:
    return float(np.sum(lp))


def compute_all_scores(logprob_arrays: List[np.ndarray]) -> Dict[str, np.ndarray]:
    """Returns {"min": (N,), "mean": (N,), "raw_sum": (N,)} from list of variable-length arrays."""
    mins  = np.array([min_score(lp)  for lp in logprob_arrays])
    means = np.array([mean_score(lp) for lp in logprob_arrays])
    sums  = np.array([raw_sum(lp)    for lp in logprob_arrays])
    return {"min": mins, "mean": means, "raw_sum": sums}
