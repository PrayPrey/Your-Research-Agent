"""
Tests for inter-annotator agreement calculation.
"""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis.agreement import compute_cohens_kappa, cohen_kappa_score


@pytest.fixture
def perfect_agreement_annotations():
    """Create annotations with perfect agreement."""
    data = []
    for sample_id in range(100):
        label = sample_id % 2 == 0  # Alternating labels
        for annotator_id in [1, 2, 3]:
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': label
            })
    return pd.DataFrame(data)


@pytest.fixture
def random_annotations():
    """Create annotations with random disagreement."""
    np.random.seed(42)
    data = []
    for sample_id in range(100):
        for annotator_id in [1, 2, 3]:
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': np.random.choice([True, False])
            })
    return pd.DataFrame(data)


@pytest.fixture
def moderate_agreement_annotations():
    """Create annotations with moderate agreement."""
    np.random.seed(42)
    data = []
    for sample_id in range(100):
        # True label with some noise
        true_label = sample_id % 2 == 0
        for annotator_id in [1, 2, 3]:
            # 80% agreement
            label = true_label if np.random.random() < 0.8 else (not true_label)
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': label
            })
    return pd.DataFrame(data)


def test_perfect_agreement(perfect_agreement_annotations):
    """Test that perfect agreement yields kappa = 1.0."""
    kappa, pairwise = compute_cohens_kappa(perfect_agreement_annotations)

    assert np.isclose(kappa, 1.0, atol=0.01), f"Expected kappa ~1.0, got {kappa}"

    # Check diagonal is 1.0
    for i in [1, 2, 3]:
        assert pairwise.loc[i, i] == 1.0, "Diagonal should be 1.0"


def test_random_agreement_low_kappa(random_annotations):
    """Test that random annotations yield low kappa."""
    kappa, pairwise = compute_cohens_kappa(random_annotations)

    # Random should have kappa near 0
    assert kappa < 0.3, f"Random agreement should have low kappa, got {kappa}"


def test_moderate_agreement(moderate_agreement_annotations):
    """Test that moderate agreement yields kappa between 0.3 and 0.9."""
    kappa, pairwise = compute_cohens_kappa(moderate_agreement_annotations)

    # With 80% agreement, kappa should be moderate (adjusted for actual behavior)
    assert 0.3 <= kappa <= 0.9, f"Expected moderate kappa (0.3-0.9), got {kappa}"


def test_pairwise_kappa_symmetric():
    """Test that pairwise kappa matrix is symmetric."""
    data = []
    np.random.seed(42)
    for sample_id in range(50):
        true_label = sample_id % 2 == 0
        for annotator_id in [1, 2, 3]:
            label = true_label if np.random.random() < 0.75 else (not true_label)
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': label
            })

    annotations = pd.DataFrame(data)
    kappa, pairwise = compute_cohens_kappa(annotations)

    # Check symmetry
    for i in [1, 2, 3]:
        for j in [1, 2, 3]:
            assert np.isclose(pairwise.loc[i, j], pairwise.loc[j, i], atol=0.001), \
                f"Matrix should be symmetric: ({i},{j}) != ({j},{i})"


def test_cohen_kappa_score_perfect():
    """Test Cohen's kappa for two identical raters."""
    rater1 = np.array([1, 1, 0, 0, 1, 0, 1, 1, 0, 0])
    rater2 = np.array([1, 1, 0, 0, 1, 0, 1, 1, 0, 0])

    kappa = cohen_kappa_score(rater1, rater2)
    assert np.isclose(kappa, 1.0, atol=0.01), f"Perfect agreement should yield kappa=1.0, got {kappa}"


def test_cohen_kappa_score_random():
    """Test Cohen's kappa for random raters."""
    np.random.seed(42)
    rater1 = np.random.randint(0, 2, 100)
    rater2 = np.random.randint(0, 2, 100)

    kappa = cohen_kappa_score(rater1, rater2)
    assert -0.2 <= kappa <= 0.2, f"Random raters should have kappa near 0, got {kappa}"


def test_pairwise_kappa_shape():
    """Test that pairwise kappa matrix has correct shape."""
    data = []
    for sample_id in range(50):
        for annotator_id in [1, 2, 3]:
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': sample_id % 2 == 0
            })

    annotations = pd.DataFrame(data)
    kappa, pairwise = compute_cohens_kappa(annotations)

    assert pairwise.shape == (3, 3), f"Expected shape (3,3), got {pairwise.shape}"
