"""Tests for permutation module."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import torch
from permutation import (
    sample_functional_permutations,
    apply_permutation,
    _CIFAR10GS_CNN,
)
from data_loader import CHANNELS_PER_LAYER, CONV_WEIGHT_KEYS, CONV_BIAS_KEYS


def make_dummy_state_dict():
    """Create a dummy state_dict matching CIFAR10-GS architecture."""
    sd = {}
    # Conv weights and biases
    shapes = {
        "module_list.0.weight": (8, 3, 5, 5),
        "module_list.0.bias": (8,),
        "module_list.3.weight": (6, 8, 5, 5),
        "module_list.3.bias": (6,),
        "module_list.6.weight": (4, 6, 2, 2),
        "module_list.6.bias": (4,),
        "module_list.9.weight": (20, 36),
        "module_list.9.bias": (20,),
        "module_list.11.weight": (10, 20),
        "module_list.11.bias": (10,),
    }
    torch.manual_seed(42)
    for k, s in shapes.items():
        sd[k] = torch.randn(s)
    return sd


def test_sample_permutations_shape():
    specs = sample_functional_permutations(CHANNELS_PER_LAYER, K=5, seed=1)
    assert len(specs) == 5
    for spec in specs:
        assert len(spec) == len(CHANNELS_PER_LAYER)
        for p, c in zip(spec, CHANNELS_PER_LAYER):
            assert p.shape == (c,)
            assert set(p.tolist()) == set(range(c))


def test_apply_permutation_shapes_preserved():
    sd = make_dummy_state_dict()
    specs = sample_functional_permutations(CHANNELS_PER_LAYER, K=1, seed=1)
    perm_sd = apply_permutation(sd, specs[0])
    for k in sd:
        assert perm_sd[k].shape == sd[k].shape, f"Shape mismatch for {k}"


def test_apply_permutation_changes_weights():
    sd = make_dummy_state_dict()
    specs = sample_functional_permutations(CHANNELS_PER_LAYER, K=1, seed=1)
    perm_sd = apply_permutation(sd, specs[0])
    # At least one key should differ
    changed = any(not torch.equal(sd[k], perm_sd[k]) for k in CONV_WEIGHT_KEYS)
    assert changed, "Permutation should change at least one weight"


def test_permutation_identity():
    """Identity permutation (sorted indices) returns equal state_dict."""
    sd = make_dummy_state_dict()
    identity_spec = [torch.arange(c) for c in CHANNELS_PER_LAYER]
    perm_sd = apply_permutation(sd, identity_spec)
    for k in sd:
        assert torch.allclose(sd[k], perm_sd[k]), f"Identity perm changed {k}"


def test_cnn_loads_state_dict():
    sd = make_dummy_state_dict()
    model = _CIFAR10GS_CNN()
    model.load_state_dict(sd)
    x = torch.rand(1, 3, 28, 28)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (1, 10)
