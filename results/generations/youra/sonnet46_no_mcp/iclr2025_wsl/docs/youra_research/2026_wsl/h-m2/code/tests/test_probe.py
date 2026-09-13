"""Tests for h-m1 probe.py (tasks 010-014)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from probe import (
    get_mnist_cnn_layer_order,
    generate_permuted_weights,
    _embed_state_dict,
    _permute_conv_out,
    _permute_conv_in,
    _permute_fc_out,
    _permute_fc_in,
)
from models import FlatMLPEncoder


def _make_state_dict():
    """Minimal CNN state_dict matching layer_order keys."""
    return {
        "module_list.0.weight": torch.randn(32, 1, 3, 3),
        "module_list.0.bias": torch.randn(32),
        "module_list.3.weight": torch.randn(64, 32, 3, 3),
        "module_list.3.bias": torch.randn(64),
        "module_list.6.weight": torch.randn(128, 64 * 4),  # spatial=4
        "module_list.6.bias": torch.randn(128),
        "module_list.8.weight": torch.randn(10, 128),
        "module_list.8.bias": torch.randn(10),
    }


def test_layer_order_keys():
    lo = get_mnist_cnn_layer_order()
    assert len(lo) == 3
    keys = {k for pair in lo for k in (pair[0], pair[1])}
    assert "module_list.0.weight" in keys


def test_permute_helpers_shape():
    w_conv = torch.randn(32, 16, 3, 3)
    perm = torch.randperm(32)
    assert _permute_conv_out(w_conv, perm).shape == w_conv.shape
    perm2 = torch.randperm(16)
    assert _permute_conv_in(w_conv, perm2).shape == w_conv.shape

    w_fc = torch.randn(64, 32)
    perm3 = torch.randperm(64)
    assert _permute_fc_out(w_fc, perm3).shape == w_fc.shape
    perm4 = torch.randperm(32)
    assert _permute_fc_in(w_fc, perm4).shape == w_fc.shape


def test_permuted_same_keys():
    sd = _make_state_dict()
    lo = get_mnist_cnn_layer_order()
    perm_sd = generate_permuted_weights(sd, lo, seed=0)
    assert set(perm_sd.keys()) == set(sd.keys())
    for k in sd:
        assert perm_sd[k].shape == sd[k].shape


def test_embed_output_shape():
    enc = FlatMLPEncoder(input_dim=32, hidden_dims=[16], embed_dim=8)
    sd = {"w": torch.randn(32)}
    mean = torch.zeros(32)
    std = torch.ones(32)
    emb = _embed_state_dict(enc, sd, mean, std, torch.device("cpu"))
    assert emb.shape == (8,)


def test_embed_device():
    enc = FlatMLPEncoder(input_dim=32, hidden_dims=[16], embed_dim=8)
    sd = {"w": torch.randn(32)}
    mean = torch.zeros(32)
    std = torch.ones(32)
    emb = _embed_state_dict(enc, sd, mean, std, torch.device("cpu"))
    assert emb.device.type == "cpu"
