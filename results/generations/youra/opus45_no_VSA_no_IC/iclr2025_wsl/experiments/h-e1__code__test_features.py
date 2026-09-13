"""Unit tests for feature extraction."""
import numpy as np
import torch
import pytest
from features import layer_statistics, extract_weight_statistics


def test_layer_statistics_shape():
    """layer_statistics returns 7 values."""
    w = torch.randn(64, 32, 3, 3)
    stats = layer_statistics(w)
    assert stats.shape == (7,), f"Expected shape (7,), got {stats.shape}"


def test_layer_statistics_values():
    """Verify statistics on known input."""
    w = torch.ones(10, 5) * 2.0
    stats = layer_statistics(w)

    assert np.isclose(stats[0], 2.0, atol=1e-5), f"Mean should be 2.0, got {stats[0]}"
    assert np.isclose(stats[1], 0.0, atol=1e-5), f"Std should be 0.0, got {stats[1]}"
    assert np.isclose(stats[2], 2.0, atol=1e-5), f"Min should be 2.0, got {stats[2]}"
    assert np.isclose(stats[3], 2.0, atol=1e-5), f"Max should be 2.0, got {stats[3]}"


def test_layer_statistics_sparsity():
    """Verify sparsity calculation."""
    w = torch.zeros(10, 10)
    w[0, 0] = 1.0
    stats = layer_statistics(w)
    expected_sparsity = 99 / 100
    assert np.isclose(stats[6], expected_sparsity, atol=0.01), f"Sparsity should be ~{expected_sparsity}, got {stats[6]}"


def test_extract_weight_statistics_filters_1d():
    """extract_weight_statistics skips 1D tensors (bias, BN)."""
    state_dict = {
        'conv1.weight': torch.randn(64, 3, 3, 3),
        'conv1.bias': torch.randn(64),
        'bn1.weight': torch.randn(64),
        'bn1.running_mean': torch.randn(64),
    }
    feats = extract_weight_statistics(state_dict)
    assert len(feats) == 7, f"Expected 7 features (1 layer), got {len(feats)}"


def test_extract_weight_statistics_multiple_layers():
    """Multiple conv layers concatenate correctly."""
    state_dict = {
        'layer1.0.conv1.weight': torch.randn(64, 64, 3, 3),
        'layer1.0.conv2.weight': torch.randn(64, 64, 3, 3),
        'layer1.0.bn1.weight': torch.randn(64),
    }
    feats = extract_weight_statistics(state_dict)
    assert len(feats) == 14, f"Expected 14 features (2 layers), got {len(feats)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
