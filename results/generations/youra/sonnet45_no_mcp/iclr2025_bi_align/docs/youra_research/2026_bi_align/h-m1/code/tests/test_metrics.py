"""
Tests for base-rate calculation and majority vote.
"""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis.metrics import majority_vote, calculate_base_rate


@pytest.fixture
def unanimous_annotations():
    """Create annotations where all annotators agree."""
    data = []
    for sample_id in range(100):
        label = sample_id < 50  # First 50 are True, rest False
        for annotator_id in [1, 2, 3]:
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': label
            })
    return pd.DataFrame(data)


@pytest.fixture
def split_vote_annotations():
    """Create annotations with 2-1 splits."""
    data = []
    for sample_id in range(100):
        # 2 vote True, 1 votes False
        for annotator_id in [1, 2, 3]:
            label = annotator_id in [1, 2]  # Annotators 1 and 2 vote True
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': label
            })
    return pd.DataFrame(data)


def test_majority_vote_unanimous(unanimous_annotations):
    """Test majority vote with unanimous agreement."""
    final_labels = majority_vote(unanimous_annotations)

    assert len(final_labels) == 100, "Should have 100 final labels"
    assert np.sum(final_labels) == 50, "Should have 50 violations (first 50 samples)"


def test_majority_vote_split(split_vote_annotations):
    """Test majority vote with 2-1 splits."""
    final_labels = majority_vote(split_vote_annotations)

    # All should be violations (2 out of 3 vote True)
    assert np.sum(final_labels) == 100, "All samples should be violations with 2-1 split"


def test_majority_vote_shape():
    """Test that majority vote returns correct shape."""
    data = []
    n_samples = 500
    for sample_id in range(n_samples):
        for annotator_id in [1, 2, 3]:
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': sample_id % 2 == 0
            })

    annotations = pd.DataFrame(data)
    final_labels = majority_vote(annotations)

    assert final_labels.shape == (n_samples,), f"Expected shape ({n_samples},), got {final_labels.shape}"


def test_calculate_base_rate_all_violations():
    """Test base-rate calculation when all are violations."""
    final_labels = np.ones(500, dtype=int)
    base_rate, ci = calculate_base_rate(final_labels)

    assert base_rate == 1.0, f"Expected base_rate=1.0, got {base_rate}"
    assert ci[0] > 0.95, "Lower CI should be close to 1.0"
    assert ci[1] == 1.0 or ci[1] > 0.99, "Upper CI should be at or near 1.0"


def test_calculate_base_rate_no_violations():
    """Test base-rate calculation when no violations."""
    final_labels = np.zeros(500, dtype=int)
    base_rate, ci = calculate_base_rate(final_labels)

    assert base_rate == 0.0, f"Expected base_rate=0.0, got {base_rate}"
    assert ci[0] == 0.0 or ci[0] < 0.01, "Lower CI should be at or near 0.0"
    assert ci[1] < 0.05, "Upper CI should be close to 0.0"


def test_calculate_base_rate_half():
    """Test base-rate calculation with 50% violations."""
    final_labels = np.array([1] * 250 + [0] * 250)
    base_rate, ci = calculate_base_rate(final_labels)

    assert np.isclose(base_rate, 0.5, atol=0.01), f"Expected base_rate=0.5, got {base_rate}"
    assert ci[0] < 0.5 < ci[1], "CI should contain 0.5"


def test_calculate_base_rate_ci_width():
    """Test that confidence interval has reasonable width."""
    final_labels = np.array([1] * 200 + [0] * 300)
    base_rate, ci = calculate_base_rate(final_labels)

    ci_width = ci[1] - ci[0]
    assert 0.05 < ci_width < 0.15, f"CI width should be reasonable, got {ci_width}"


def test_calculate_base_rate_threshold():
    """Test base-rate near MUST_WORK threshold (0.40)."""
    # 200 violations out of 500 = 0.40
    final_labels = np.array([1] * 200 + [0] * 300)
    base_rate, ci = calculate_base_rate(final_labels)

    assert np.isclose(base_rate, 0.40, atol=0.01), f"Expected base_rate=0.40, got {base_rate}"
    assert ci[0] < base_rate < ci[1], "CI should contain base_rate"


def test_majority_vote_binary():
    """Test that majority vote returns binary values."""
    data = []
    np.random.seed(42)
    for sample_id in range(100):
        for annotator_id in [1, 2, 3]:
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': np.random.choice([True, False])
            })

    annotations = pd.DataFrame(data)
    final_labels = majority_vote(annotations)

    # Check all values are 0 or 1
    assert np.all(np.isin(final_labels, [0, 1])), "Final labels should be binary (0 or 1)"
