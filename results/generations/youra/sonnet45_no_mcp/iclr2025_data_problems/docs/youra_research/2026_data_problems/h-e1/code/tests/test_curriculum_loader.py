"""
Tests for Curriculum Data Loader
Verifies correct implementation of all 4 curriculum conditions.
"""

import pytest
import torch
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.curriculum_loader import CurriculumDataLoader
from config import DIVERSITY_SCORES


class MockDataset:
    """Mock dataset for testing."""
    def __init__(self, n_samples=100):
        self.n_samples = n_samples

    def __len__(self):
        return self.n_samples

    def __getitem__(self, idx):
        return {
            'input_ids': torch.randint(0, 50257, (2047,)),
            'labels': torch.randint(0, 50257, (2047,))
        }


def test_curriculum_loader_static():
    """Test static uniform sampling."""
    domain_data = {d: MockDataset() for d in DIVERSITY_SCORES.keys()}

    loader = CurriculumDataLoader(
        domain_data=domain_data,
        diversity_scores=DIVERSITY_SCORES,
        condition="static",
        batch_size=8,
        total_steps=100,
        seed=42
    )

    # Check weights at different training progress points
    for progress in [0.0, 0.25, 0.5, 0.75, 1.0]:
        weights = loader.get_domain_weights(progress)

        # All domains should have equal weight (1/6)
        expected_weight = 1.0 / len(DIVERSITY_SCORES)
        for domain, weight in weights.items():
            assert abs(weight - expected_weight) < 1e-6, \
                f"Static weights should be uniform: {weight} != {expected_weight}"


def test_curriculum_loader_diversity_ranked():
    """Test diversity-ranked (high to low) curriculum."""
    domain_data = {d: MockDataset() for d in DIVERSITY_SCORES.keys()}

    loader = CurriculumDataLoader(
        domain_data=domain_data,
        diversity_scores=DIVERSITY_SCORES,
        condition="diversity_ranked",
        batch_size=8,
        total_steps=100,
        seed=42
    )

    # At early training (0.0), high-diversity domains should have higher weight
    early_weights = loader.get_domain_weights(0.0)
    assert early_weights["Pile-CC"] > early_weights["PubMed"], \
        "Early training should favor high-diversity domains"

    # At late training (1.0), low-diversity domains should have higher weight
    late_weights = loader.get_domain_weights(1.0)
    assert late_weights["PubMed"] > late_weights["Pile-CC"], \
        "Late training should favor low-diversity domains"


def test_curriculum_loader_reversed():
    """Test reversed (low to high diversity) curriculum."""
    domain_data = {d: MockDataset() for d in DIVERSITY_SCORES.keys()}

    loader = CurriculumDataLoader(
        domain_data=domain_data,
        diversity_scores=DIVERSITY_SCORES,
        condition="reversed",
        batch_size=8,
        total_steps=100,
        seed=42
    )

    # At early training (0.0), low-diversity domains should have higher weight
    early_weights = loader.get_domain_weights(0.0)
    assert early_weights["PubMed"] > early_weights["Pile-CC"], \
        "Reversed: Early training should favor low-diversity domains"

    # At late training (1.0), high-diversity domains should have higher weight
    late_weights = loader.get_domain_weights(1.0)
    assert late_weights["Pile-CC"] > late_weights["PubMed"], \
        "Reversed: Late training should favor high-diversity domains"


def test_curriculum_loader_weights_sum_to_one():
    """Test that weights always sum to 1.0."""
    domain_data = {d: MockDataset() for d in DIVERSITY_SCORES.keys()}

    for condition in ["static", "diversity_ranked", "reversed", "shuffled"]:
        loader = CurriculumDataLoader(
            domain_data=domain_data,
            diversity_scores=DIVERSITY_SCORES,
            condition=condition,
            batch_size=8,
            total_steps=100,
            seed=42
        )

        for progress in np.linspace(0.0, 1.0, 10):
            weights = loader.get_domain_weights(progress)
            total_weight = sum(weights.values())
            assert abs(total_weight - 1.0) < 1e-6, \
                f"{condition} weights don't sum to 1.0: {total_weight}"


def test_curriculum_loader_min_weight():
    """Test that domains maintain reasonable minimum weight after normalization."""
    domain_data = {d: MockDataset() for d in DIVERSITY_SCORES.keys()}

    loader = CurriculumDataLoader(
        domain_data=domain_data,
        diversity_scores=DIVERSITY_SCORES,
        condition="diversity_ranked",
        batch_size=8,
        total_steps=100,
        gaussian_width=0.3,
        min_weight=0.05,
        seed=42
    )

    for progress in np.linspace(0.0, 1.0, 20):
        weights = loader.get_domain_weights(progress)
        # After normalization, weights should be close to min_weight threshold
        # Allow slight deviation due to normalization (within 2%)
        for domain, weight in weights.items():
            assert weight >= 0.03, \
                f"Domain {domain} weight {weight} too low (should be ≥3%)"


def test_sample_batch_shape():
    """Test that batch has correct shape."""
    domain_data = {d: MockDataset() for d in DIVERSITY_SCORES.keys()}

    loader = CurriculumDataLoader(
        domain_data=domain_data,
        diversity_scores=DIVERSITY_SCORES,
        condition="static",
        batch_size=8,
        total_steps=100,
        sequence_length=2047,
        seed=42
    )

    batch = loader.sample_batch(step=0)

    assert batch['input_ids'].shape == (8, 2047), "Incorrect input_ids shape"
    assert batch['labels'].shape == (8, 2047), "Incorrect labels shape"
    assert batch['domain_ids'].shape == (8,), "Incorrect domain_ids shape"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
