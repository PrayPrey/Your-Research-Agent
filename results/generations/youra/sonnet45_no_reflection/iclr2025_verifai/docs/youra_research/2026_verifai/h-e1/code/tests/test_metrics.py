"""Functional tests for heterogeneity metrics."""
import numpy as np
from metrics import compute_hamming_distance, compute_violation_entropy


def test_hamming_distance_identical():
    """Test Hamming distance with identical assignments."""
    assignment = np.array([True, False, True, False])
    ground_truth = np.array([True, False, True, False])
    d_n = compute_hamming_distance(assignment, ground_truth)
    assert d_n == 0.0, "Identical assignments should have d/n = 0"


def test_hamming_distance_different():
    """Test Hamming distance with different assignments."""
    assignment = np.array([True, True, True, True])
    ground_truth = np.array([False, False, False, False])
    d_n = compute_hamming_distance(assignment, ground_truth)
    assert d_n == 1.0, "Completely different assignments should have d/n = 1"


def test_hamming_distance_partial():
    """Test Hamming distance with partial match."""
    assignment = np.array([True, False, True, False])
    ground_truth = np.array([True, True, False, False])
    d_n = compute_hamming_distance(assignment, ground_truth)
    assert d_n == 0.5, "Half different should have d/n = 0.5"


def test_violation_entropy_all_satisfied():
    """Test entropy when all clauses are satisfied."""
    assignment = np.array([True, True, False])
    clauses = [[1, 2], [2, -3], [1, -3]]  # All satisfied by assignment
    entropy = compute_violation_entropy(assignment, clauses)
    assert np.isclose(entropy, 0.0, atol=1e-9), "All satisfied clauses should have H ≈ 0"


def test_violation_entropy_some_violations():
    """Test entropy with some clause violations."""
    assignment = np.array([False, False, False])
    clauses = [[1], [2], [3]]  # All violated
    entropy = compute_violation_entropy(assignment, clauses)
    # All three clauses violated equally -> max entropy
    assert entropy > 0.0, "Violations should produce non-zero entropy"
