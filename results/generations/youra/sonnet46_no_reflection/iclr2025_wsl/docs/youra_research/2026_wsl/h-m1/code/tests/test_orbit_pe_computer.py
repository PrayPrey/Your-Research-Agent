"""Tests for OrbitPEComputer: spec compliance for H-M1 gate criteria."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import pytest
from orbit_pe_computer import OrbitPEComputer, HAS_ARCH_BRANCHES, _flatten_weight, compute_orbit_pe_all_layers


def test_has_arch_branches_false():
    """Gate criterion: HAS_ARCH_BRANCHES must be False."""
    assert HAS_ARCH_BRANCHES is False


def test_flatten_weight_linear():
    w = torch.randn(32, 16)
    out = _flatten_weight(w, "Linear")
    assert out.shape == (32, 16)


def test_flatten_weight_conv2d():
    w = torch.randn(32, 16, 3, 3)
    out = _flatten_weight(w, "Conv2d")
    assert out.shape == (32, 16 * 9)


def test_flatten_weight_mha():
    w = torch.randn(64, 32)
    out = _flatten_weight(w, "MultiheadAttention")
    assert out.shape == (64, 32)


def test_orbit_pe_computer_linear():
    model = OrbitPEComputer(token_dim=64)
    w = torch.randn(32, 16)
    out = model.forward(w, "Linear")
    assert out.shape == (32, 64), f"Expected (32, 64), got {out.shape}"


def test_orbit_pe_computer_conv2d():
    model = OrbitPEComputer(token_dim=64)
    w = torch.randn(32, 16, 3, 3)
    out = model.forward(w, "Conv2d")
    assert out.shape == (32, 64), f"Expected (32, 64), got {out.shape}"


def test_orbit_pe_computer_mha():
    model = OrbitPEComputer(token_dim=64)
    w = torch.randn(128, 64)
    out = model.forward(w, "MultiheadAttention")
    assert out.shape == (128, 64), f"Expected (128, 64), got {out.shape}"


def test_compute_orbit_id_permutation_invariant():
    """Permuting rows of weight should only permute the orbit IDs (not change their set)."""
    model = OrbitPEComputer(token_dim=64)
    w = torch.randn(16, 8)
    ids1 = model.compute_orbit_id(w, "Linear")
    perm = torch.randperm(16)
    ids2 = model.compute_orbit_id(w[perm], "Linear")
    # orbit IDs are ranks — permuted rows should give permuted ranks
    assert set(ids1.tolist()) == set(ids2.tolist()), "Orbit ID set should be same after permutation"


def test_orbit_dim_consistent_across_layer_types():
    """All layer types must produce same output dim (dim_consistent gate criterion)."""
    model = OrbitPEComputer(token_dim=64)
    weights = {
        "Linear": torch.randn(32, 16),
        "Conv2d": torch.randn(32, 16, 3, 3),
        "MultiheadAttention": torch.randn(64, 32),
    }
    dims = set()
    for lt, w in weights.items():
        out = model.forward(w, lt)
        dims.add(out.shape[-1])
    assert len(dims) == 1, f"Inconsistent output dims across layer types: {dims}"
    assert dims.pop() == 64


def test_compute_orbit_pe_all_layers():
    """compute_orbit_pe_all_layers should process all .weight params."""
    model = OrbitPEComputer(token_dim=64)
    state_dict = {
        "layer1.weight": torch.randn(32, 16),
        "layer2.weight": torch.randn(64, 32),
        "layer1.bias": torch.randn(32),  # should be skipped
    }
    orbit_vecs, success_flags = compute_orbit_pe_all_layers(state_dict, model)
    # Only weight params should be processed
    assert "layer1.weight" in orbit_vecs
    assert "layer2.weight" in orbit_vecs
    assert "layer1.bias" not in orbit_vecs
    assert all(success_flags.values()), f"Some layers failed: {success_flags}"
