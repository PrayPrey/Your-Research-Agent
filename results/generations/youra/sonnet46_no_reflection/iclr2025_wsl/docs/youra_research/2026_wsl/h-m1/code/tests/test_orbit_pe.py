import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import torch
import torch.nn as nn
from orbit_pe import (
    compute_orbit_pe,
    compute_orbit_pe_success_rate,
    get_layer_type_map,
    SUPPORTED_LAYER_TYPES,
)


class MixedModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 8, 3)
        self.fc = nn.Linear(8, 4)
        self.attn = nn.MultiheadAttention(16, 2)


def test_supported_layer_types():
    assert "Linear" in SUPPORTED_LAYER_TYPES
    assert "Conv2d" in SUPPORTED_LAYER_TYPES
    assert "MultiheadAttention" in SUPPORTED_LAYER_TYPES


def test_compute_orbit_pe_success_linear():
    sd = {"fc.weight": torch.randn(10, 5)}
    type_map = {"fc.weight": "Linear"}
    vectors, flags = compute_orbit_pe(sd, type_map)
    assert flags["fc.weight"] is True
    assert vectors["fc.weight"].shape == (3,)


def test_compute_orbit_pe_success_conv2d():
    sd = {"conv.weight": torch.randn(8, 3, 3, 3)}
    type_map = {"conv.weight": "Conv2d"}
    vectors, flags = compute_orbit_pe(sd, type_map)
    assert flags["conv.weight"] is True
    assert vectors["conv.weight"].shape == (3,)


def test_compute_orbit_pe_success_mha():
    sd = {"attn.queries.weight": torch.randn(32, 16)}
    type_map = {"attn.queries.weight": "MultiheadAttention"}
    vectors, flags = compute_orbit_pe(sd, type_map, n_heads=2)
    assert flags["attn.queries.weight"] is True


def test_compute_orbit_pe_success_rate_all_true():
    flags = {"a": True, "b": True, "c": True}
    assert compute_orbit_pe_success_rate(flags) == 1.0


def test_compute_orbit_pe_success_rate_partial():
    flags = {"a": True, "b": False}
    rate = compute_orbit_pe_success_rate(flags)
    assert 0.0 < rate < 1.0


def test_get_layer_type_map():
    model = MixedModel()
    type_map = get_layer_type_map(model)
    assert "conv.weight" in type_map
    assert type_map["conv.weight"] == "Conv2d"
    assert "fc.weight" in type_map
    assert type_map["fc.weight"] == "Linear"
