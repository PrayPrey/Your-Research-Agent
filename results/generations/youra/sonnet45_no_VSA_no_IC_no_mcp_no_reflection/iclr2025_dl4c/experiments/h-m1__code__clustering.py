"""Clustering coefficient and permutation test."""

from typing import Dict, List, Tuple
from collections import Counter
import numpy as np

from utils import ErrorType


def clustering_coefficient(
    fix_sequence: List[int],
    error_labels: Dict[int, ErrorType]
) -> float:
    """
    Compute clustering coefficient.

    Args:
        fix_sequence: Test IDs in order fixed [t1, t2, t3, ...]
        error_labels: {test_id: ErrorType}

    Returns:
        observed_consecutive_same / expected_random
    """
    if len(fix_sequence) < 2:
        return 0.0

    # Extract error type sequence
    types = [error_labels[tid] for tid in fix_sequence if tid in error_labels]
    if len(types) < 2:
        return 0.0

    # Count consecutive same-type pairs
    consecutive_same = sum(
        1 for i in range(len(types) - 1)
        if types[i] == types[i + 1]
    )

    # Observed rate
    observed = consecutive_same / (len(types) - 1)

    # Expected random rate
    type_counts = Counter(types)
    total = len(types)

    if total == 0:
        return 0.0

    # Probability of consecutive same-type under random ordering
    expected = sum(
        (count / total) ** 2
        for count in type_counts.values()
    )

    if expected == 0:
        return 0.0

    return observed / expected


def permutation_test(
    fix_sequence: List[int],
    error_labels: Dict[int, ErrorType],
    n_permutations: int = 1000,
    seed: int = 1
) -> Tuple[float, float]:
    """
    Test significance vs random.

    Returns:
        (clustering_coeff_observed, p_value)
    """
    # Observed clustering
    observed = clustering_coefficient(fix_sequence, error_labels)

    # Generate null distribution
    rng = np.random.default_rng(seed)
    null_coeffs = []

    for _ in range(n_permutations):
        shuffled = rng.permutation(fix_sequence).tolist()
        null_coeff = clustering_coefficient(shuffled, error_labels)
        null_coeffs.append(null_coeff)

    # Two-tailed p-value
    null_mean = np.mean(null_coeffs)
    p_value = (
        sum(abs(null_c - null_mean) >= abs(observed - null_mean) for null_c in null_coeffs) + 1
    ) / (n_permutations + 1)

    return observed, p_value


def evaluate_gate(
    clustering_coef: float,
    p_value: float,
    clustering_threshold: float = 0.3,
    p_threshold: float = 0.05
) -> Dict:
    """MUST_WORK gate check."""
    passed = clustering_coef > clustering_threshold and p_value < p_threshold

    return {
        "clustering_agent": clustering_coef,
        "p_value": p_value,
        "clustering_threshold": clustering_threshold,
        "p_threshold": p_threshold,
        "gate_pass": passed,
        "decision": "PASS" if passed else "PIVOT"
    }
