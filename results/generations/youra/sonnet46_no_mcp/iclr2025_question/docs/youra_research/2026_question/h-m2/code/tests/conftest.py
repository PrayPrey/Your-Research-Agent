import numpy as np
import pytest


@pytest.fixture
def cluster_counts_pass():
    """PASS case: low cluster counts → high aggregation rate (~0.80)."""
    rng = np.random.default_rng(42)
    counts = rng.choice([1, 2, 3, 4], size=2000, p=[0.05, 0.15, 0.30, 0.50])
    return counts.astype(int)


@pytest.fixture
def cluster_counts_pivot():
    """PIVOT case: high cluster counts → low aggregation rate (~0.13, H-M1 realistic)."""
    rng = np.random.default_rng(42)
    counts = rng.choice([3, 4, 5], size=2000, p=[0.03, 0.10, 0.87])
    return counts.astype(int)


@pytest.fixture
def cluster_counts_partial():
    """PARTIAL case: medium aggregation rate (~0.38)."""
    rng = np.random.default_rng(42)
    counts = rng.choice([2, 3, 4, 5], size=2000, p=[0.05, 0.10, 0.23, 0.62])
    return counts.astype(int)


@pytest.fixture
def mock_labels():
    """1000 hallucinated (1) + 1000 factual (0), seed=42."""
    rng = np.random.default_rng(42)
    labels = np.array([0] * 1000 + [1] * 1000)
    rng.shuffle(labels)
    return labels
