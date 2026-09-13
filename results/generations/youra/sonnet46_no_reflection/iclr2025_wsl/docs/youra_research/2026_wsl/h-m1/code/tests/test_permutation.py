import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import torch
import torch.nn as nn
from permutation import (
    apply_canonical_channel_permutation,
    apply_transformer_head_permutation,
    _make_perm,
    _permute_batchnorm,
    _permute_layernorm,
)


def make_simple_cnn_state_dict():
    sd = {}
    # Layer 0: conv [8, 3, 3, 3]
    sd["layer0.weight"] = torch.randn(8, 3, 3, 3)
    sd["layer0.bias"] = torch.randn(8)
    # Layer 1: conv [16, 8, 3, 3]
    sd["layer1.weight"] = torch.randn(16, 8, 3, 3)
    sd["layer1.bias"] = torch.randn(16)
    # Layer 2: linear [10, 16]
    sd["fc.weight"] = torch.randn(10, 16)
    sd["fc.bias"] = torch.randn(10)
    return sd


def test_permuted_state_dict_shapes_preserved():
    sd = make_simple_cnn_state_dict()
    perm_sd = apply_canonical_channel_permutation(sd, perm_seed=0)
    for k in sd:
        assert perm_sd[k].shape == sd[k].shape, f"Shape mismatch for {k}"


def test_permuted_not_equal_original():
    sd = make_simple_cnn_state_dict()
    perm_sd = apply_canonical_channel_permutation(sd, perm_seed=0)
    # At least some weights should differ
    diffs = sum(not torch.allclose(sd[k], perm_sd[k]) for k in sd)
    assert diffs > 0


def test_ten_seeds_produce_different_permutations():
    perms = [_make_perm(16, seed) for seed in range(10)]
    perm_tensors = [p.tolist() for p in perms]
    unique = set(tuple(p) for p in perm_tensors)
    assert len(unique) == 10


def test_permute_batchnorm():
    sd = {
        "bn.running_mean": torch.arange(8, dtype=torch.float),
        "bn.running_var": torch.ones(8),
        "bn.weight": torch.ones(8),
        "bn.bias": torch.zeros(8),
    }
    pi = torch.randperm(8)
    updates = _permute_batchnorm(sd, "bn", pi)
    assert updates["bn.running_mean"].tolist() == sd["bn.running_mean"][pi].tolist()
    assert updates["bn.weight"].shape == (8,)


def test_permute_layernorm():
    sd = {
        "ln.weight": torch.ones(32),
        "ln.bias": torch.zeros(32),
    }
    pi = torch.randperm(32)
    updates = _permute_layernorm(sd, "ln", pi)
    assert updates["ln.weight"].shape == (32,)
    assert updates["ln.bias"].shape == (32,)


def make_transformer_state_dict(n_heads=2, head_dim=16, d_model=32):
    sd = {}
    # Separate Q/K/V (Transformer-NFN style)
    sd["encoder.0.attention.queries.weight"] = torch.randn(n_heads * head_dim, d_model)
    sd["encoder.0.attention.queries.bias"] = torch.randn(n_heads * head_dim)
    sd["encoder.0.attention.keys.weight"] = torch.randn(n_heads * head_dim, d_model)
    sd["encoder.0.attention.keys.bias"] = torch.randn(n_heads * head_dim)
    sd["encoder.0.attention.values.weight"] = torch.randn(n_heads * head_dim, d_model)
    sd["encoder.0.attention.values.bias"] = torch.randn(n_heads * head_dim)
    sd["encoder.0.attention.out_projection.weight"] = torch.randn(d_model, n_heads * head_dim)
    sd["encoder.0.attention.out_projection.bias"] = torch.randn(d_model)
    return sd


def test_transformer_head_permutation_shapes_preserved():
    n_heads, head_dim, d_model = 2, 16, 32
    sd = make_transformer_state_dict(n_heads, head_dim, d_model)
    perm_sd = apply_transformer_head_permutation(sd, perm_seed=0, n_heads=n_heads, head_dim=head_dim)
    for k in sd:
        assert perm_sd[k].shape == sd[k].shape, f"Shape mismatch for {k}"


def test_transformer_permutation_changes_weights():
    n_heads, head_dim, d_model = 2, 16, 32
    sd = make_transformer_state_dict(n_heads, head_dim, d_model)
    perm_sd = apply_transformer_head_permutation(sd, perm_seed=0, n_heads=n_heads, head_dim=head_dim)
    key = "encoder.0.attention.queries.weight"
    # Different permutation seed should produce different result
    perm_sd2 = apply_transformer_head_permutation(sd, perm_seed=5, n_heads=n_heads, head_dim=head_dim)
    # At least one of the two permuted versions should differ from original
    assert not torch.allclose(perm_sd[key], sd[key]) or not torch.allclose(perm_sd2[key], sd[key])
