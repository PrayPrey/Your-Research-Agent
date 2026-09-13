"""Tests for orbit_var module."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import torch
from orbit_var import compute_orbit_var_all_models, run_gate_check
from permutation import sample_functional_permutations, apply_permutation
from data_loader import CHANNELS_PER_LAYER


def make_dummy_state_dict(seed=0):
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
    torch.manual_seed(seed)
    return {k: torch.randn(s) for k, s in shapes.items()}


def test_compute_orbit_var_zero_for_constant_encoder():
    """A constant encoder (ignores input) should have OrbitVar=0."""
    dataset = [make_dummy_state_dict(i) for i in range(5)]
    specs = sample_functional_permutations(CHANNELS_PER_LAYER, K=5, seed=1)

    def constant_encoder(sd):
        return torch.zeros(64)

    per_vars, mean_ov, max_ov = compute_orbit_var_all_models(
        dataset, constant_encoder, specs, log_every=100
    )
    assert mean_ov == pytest.approx(0.0, abs=1e-15)


def test_compute_orbit_var_nonzero_for_position_aware():
    """A position-aware encoder should have OrbitVar > 0."""
    from data_loader import CONV_WEIGHT_KEYS
    dataset = [make_dummy_state_dict(i) for i in range(5)]
    specs = sample_functional_permutations(CHANNELS_PER_LAYER, K=5, seed=1)

    def position_aware_encoder(sd):
        # Flatten first conv weight — position-aware, not invariant
        return sd[CONV_WEIGHT_KEYS[0]].flatten()[:64]

    per_vars, mean_ov, max_ov = compute_orbit_var_all_models(
        dataset, position_aware_encoder, specs, log_every=100
    )
    assert mean_ov > 1e-10, f"Position-aware encoder OrbitVar should be > 0, got {mean_ov:.3e}"


def test_gate_check_pass():
    assert run_gate_check(1e-10, 1e-12, threshold=1e-6) is True


def test_gate_check_fail_c2():
    assert run_gate_check(1e-5, 1e-12, threshold=1e-6) is False


def test_gate_check_fail_both():
    assert run_gate_check(0.01, 0.005, threshold=1e-6) is False
