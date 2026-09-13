"""Tests for weight_analysis.py (task-006, task-010)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from weight_analysis import flatten_weights, compute_cosine_distance, stratified_pair_sample


def _make_state_dict(seed=0):
    torch.manual_seed(seed)
    return {
        "conv1.weight": torch.randn(32, 1, 3, 3),
        "conv1.bias": torch.randn(32),
        "conv2.weight": torch.randn(64, 32, 3, 3),
        "conv2.bias": torch.randn(64),
        "fc1.weight": torch.randn(128, 576),
        "fc1.bias": torch.randn(128),
        "fc2.weight": torch.randn(10, 128),
        "fc2.bias": torch.randn(10),
    }


def test_flatten_weights_dtype_device():
    sd = _make_state_dict()
    w = flatten_weights(sd)
    assert w.dtype == torch.float32
    assert w.device.type == "cpu"


def test_flatten_weights_1d():
    sd = _make_state_dict()
    w = flatten_weights(sd)
    assert w.dim() == 1
    assert w.shape[0] > 0


def test_flatten_weights_consistent():
    sd = _make_state_dict(0)
    w1 = flatten_weights(sd)
    w2 = flatten_weights(sd)
    assert torch.equal(w1, w2)


def test_flatten_weights_no_bias_keys():
    sd = {"layer.weight": torch.randn(10, 5)}
    w = flatten_weights(sd)
    assert w.shape[0] == 50


def test_compute_cosine_distance_identical():
    w = torch.randn(100)
    dist = compute_cosine_distance(w, w)
    assert abs(dist) < 1e-5


def test_compute_cosine_distance_range():
    w1 = torch.randn(100)
    w2 = torch.randn(100)
    dist = compute_cosine_distance(w1, w2)
    assert 0.0 <= dist <= 2.0


def test_stratified_pair_sample_bounded():
    import numpy as np
    np.random.seed(0)
    # Create 200 fake checkpoints with accuracies spread across [0.8, 1.0]
    checkpoints = [
        {"state_dict": _make_state_dict(i), "test_accuracy": 0.8 + 0.2 * (i / 200)}
        for i in range(200)
    ]
    pairs = stratified_pair_sample(checkpoints, n_per_decile=10, acc_threshold=0.05, seed=42)
    assert len(pairs) <= 100  # 10 deciles * 10 per decile


def test_stratified_pair_sample_deterministic():
    import numpy as np
    checkpoints = [
        {"state_dict": _make_state_dict(i), "test_accuracy": 0.8 + 0.002 * i}
        for i in range(100)
    ]
    p1 = stratified_pair_sample(checkpoints, n_per_decile=5, acc_threshold=0.05, seed=42)
    p2 = stratified_pair_sample(checkpoints, n_per_decile=5, acc_threshold=0.05, seed=42)
    assert len(p1) == len(p2)
