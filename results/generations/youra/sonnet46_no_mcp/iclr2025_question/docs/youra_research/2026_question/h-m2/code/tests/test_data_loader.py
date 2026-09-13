import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from data_loader import validate_cluster_counts


def test_validate_cluster_counts_clamp():
    counts = np.array([0, 1, 3, 5, 6])
    validated = validate_cluster_counts(counts, n=5)
    assert validated.min() >= 1
    assert validated.max() <= 5


def test_validate_cluster_counts_length():
    counts = np.ones(2000, dtype=int)
    validated = validate_cluster_counts(counts, n=2000)
    assert len(validated) == 2000


def test_validate_cluster_counts_wrong_length():
    counts = np.ones(100, dtype=int)
    with pytest.raises(ValueError):
        validate_cluster_counts(counts, n=2000)


def test_validate_cluster_counts_no_change_valid():
    counts = np.array([1, 2, 3, 4, 5])
    validated = validate_cluster_counts(counts, n=5)
    np.testing.assert_array_equal(validated, counts)


def test_validate_cluster_counts_clamp_low():
    counts = np.array([0, -1, 1, 2, 3])
    validated = validate_cluster_counts(counts, n=5)
    assert validated[0] == 1
    assert validated[1] == 1


def test_validate_cluster_counts_clamp_high():
    counts = np.array([3, 4, 5, 6, 7])
    validated = validate_cluster_counts(counts, n=5)
    assert validated[3] == 5
    assert validated[4] == 5
