"""
Tests for stratified sampling module.
"""
import pytest
import pandas as pd
import numpy as np
from datasets import Dataset
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.sampler import stratified_sample


@pytest.fixture
def mock_dataset():
    """Create a mock HH-RLHF dataset for testing."""
    np.random.seed(42)
    n_samples = 2000

    data = {
        'prompt': [f"Prompt {i}" for i in range(n_samples)],
        'rejected': [f"Response " + "x" * np.random.randint(10, 1000) for i in range(n_samples)]
    }

    return Dataset.from_dict(data)


def test_stratified_sample_size(mock_dataset):
    """Test that stratified sample returns correct size."""
    sample_size = 500
    result = stratified_sample(mock_dataset, sample_size=sample_size, seed=42)

    assert len(result) == sample_size, f"Expected {sample_size} samples, got {len(result)}"


def test_stratified_sample_columns(mock_dataset):
    """Test that stratified sample has required columns."""
    result = stratified_sample(mock_dataset, sample_size=500, seed=42)

    expected_columns = ['id', 'prompt', 'rejected_response', 'length', 'length_quartile']
    assert list(result.columns) == expected_columns, f"Expected columns {expected_columns}, got {list(result.columns)}"


def test_stratified_sample_balance(mock_dataset):
    """Test that each quartile has approximately equal samples."""
    sample_size = 500
    result = stratified_sample(mock_dataset, sample_size=sample_size, seed=42)

    quartile_counts = result['length_quartile'].value_counts()

    # Each quartile should have approximately 125 samples (500 / 4)
    expected_per_quartile = sample_size // 4
    tolerance = 10  # Allow some variation

    for quartile, count in quartile_counts.items():
        assert abs(count - expected_per_quartile) <= tolerance, \
            f"Quartile {quartile} has {count} samples, expected ~{expected_per_quartile}"


def test_stratified_sample_reproducibility(mock_dataset):
    """Test that same seed produces same samples."""
    seed = 42
    sample1 = stratified_sample(mock_dataset, sample_size=500, seed=seed)
    sample2 = stratified_sample(mock_dataset, sample_size=500, seed=seed)

    # Check that IDs match
    assert list(sample1['id']) == list(sample2['id']), "Same seed should produce same samples"


def test_stratified_sample_different_seeds(mock_dataset):
    """Test that different seeds produce different samples."""
    sample1 = stratified_sample(mock_dataset, sample_size=500, seed=42)
    sample2 = stratified_sample(mock_dataset, sample_size=500, seed=123)

    # Check that IDs differ
    assert list(sample1['id']) != list(sample2['id']), "Different seeds should produce different samples"


def test_stratified_sample_length_calculation(mock_dataset):
    """Test that length is calculated correctly."""
    result = stratified_sample(mock_dataset, sample_size=100, seed=42)

    for _, row in result.iterrows():
        expected_length = len(row['rejected_response'])
        assert row['length'] == expected_length, \
            f"Length mismatch: expected {expected_length}, got {row['length']}"


def test_stratified_sample_quartile_ordering(mock_dataset):
    """Test that quartiles represent increasing length ranges."""
    result = stratified_sample(mock_dataset, sample_size=500, seed=42)

    quartile_lengths = result.groupby('length_quartile')['length'].mean().sort_index()

    # Q1 should have smallest average, Q4 should have largest
    quartile_list = quartile_lengths.tolist()
    assert quartile_list == sorted(quartile_list), \
        "Quartiles should have increasing average lengths"
