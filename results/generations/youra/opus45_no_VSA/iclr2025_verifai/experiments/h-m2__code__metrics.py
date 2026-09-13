"""Metrics: pass@1, bootstrap CI, McNemar test."""
from typing import List, Tuple, Dict
import numpy as np
from collections import defaultdict
from repair_loop import IterationLog


def pass_at_1(logs: List[IterationLog], condition: str) -> float:
    """Fraction of problems where final iteration passed for given condition."""
    # Group by problem_id, take last iteration per problem
    final_results: Dict[str, bool] = {}
    for log in logs:
        if log.condition == condition:
            final_results[log.problem_id] = log.passed

    if not final_results:
        return 0.0
    return sum(final_results.values()) / len(final_results)


def relative_improvement(pass_a: float, pass_b: float) -> float:
    """(pass_a - pass_b) / pass_b * 100."""
    if pass_b == 0:
        return float("inf") if pass_a > 0 else 0.0
    return (pass_a - pass_b) / pass_b * 100


def _get_paired_results(logs: List[IterationLog]) -> List[Tuple[bool, bool]]:
    """Get (pass_A, pass_B) pairs per problem."""
    results_a: Dict[str, bool] = {}
    results_b: Dict[str, bool] = {}

    for log in logs:
        if log.condition == "A":
            results_a[log.problem_id] = log.passed
        else:
            results_b[log.problem_id] = log.passed

    pairs = []
    for pid in results_a:
        if pid in results_b:
            pairs.append((results_a[pid], results_b[pid]))
    return pairs


def bootstrap_ci(logs: List[IterationLog], n_resamples: int = 10000, seed: int = 42) -> Tuple[float, float]:
    """Bootstrap 95% CI of relative improvement."""
    pairs = _get_paired_results(logs)
    if not pairs:
        return (0.0, 0.0)

    rng = np.random.default_rng(seed)
    n = len(pairs)
    pairs_arr = np.array(pairs, dtype=bool)

    deltas = []
    for _ in range(n_resamples):
        indices = rng.choice(n, size=n, replace=True)
        sample = pairs_arr[indices]
        pa = sample[:, 0].mean()
        pb = sample[:, 1].mean()
        deltas.append(relative_improvement(pa, pb))

    return (np.percentile(deltas, 2.5), np.percentile(deltas, 97.5))


def mcnemar_test(logs: List[IterationLog]) -> float:
    """McNemar test p-value for paired pass/fail."""
    pairs = _get_paired_results(logs)

    # b = A passed, B failed; c = A failed, B passed
    b = sum(1 for a, bb in pairs if a and not bb)
    c = sum(1 for a, bb in pairs if not a and bb)

    # McNemar exact test (binomial)
    from scipy.stats import binomtest
    if b + c == 0:
        return 1.0
    return binomtest(b, b + c, 0.5).pvalue
