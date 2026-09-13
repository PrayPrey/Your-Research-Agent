"""Tests for variance_decomposer.py — tasks 005 + 006."""
import pytest
import torch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orbit_projector import OrbitProjector
from variance_decomposer import VarianceDecomposer, verify_mechanism_activated


def make_trajectory(n_checkpoints=15):
    """Create a fake trajectory with consistent (small) layer structure."""
    sd_template = {
        "module_list.0.weight": torch.randn(8, 3, 3, 3),
        "module_list.3.weight": torch.randn(16, 8, 3, 3),
        "module_list.9.weight": torch.randn(32, 64),
        "module_list.11.weight": torch.randn(10, 32),
    }
    trajectory = []
    for i in range(n_checkpoints):
        sd = {k: v + 0.01 * i * torch.randn_like(v) for k, v in sd_template.items()}
        trajectory.append(sd)
    return trajectory


def make_decomposer():
    proj = OrbitProjector(token_dim=64, orbit_basis_dim=64, h_m1_code_path="/nonexistent")
    return VarianceDecomposer(proj, eps=1e-8)


def test_compute_trajectory_variance_ratio_keys():
    decomposer = make_decomposer()
    traj = make_trajectory()
    result = decomposer.compute_trajectory_variance_ratio(traj)
    assert "ratio" in result
    assert "var_perm" in result
    assert "var_gl" in result
    assert "n_checkpoints" in result


def test_compute_trajectory_variance_ratio_range():
    decomposer = make_decomposer()
    traj = make_trajectory()
    result = decomposer.compute_trajectory_variance_ratio(traj)
    assert 0.0 <= result["ratio"] <= 1.0


def test_compute_trajectory_variance_ratio_n_checkpoints():
    decomposer = make_decomposer()
    traj = make_trajectory(n_checkpoints=20)
    result = decomposer.compute_trajectory_variance_ratio(traj)
    assert result["n_checkpoints"] == 20


def test_compute_trajectory_variance_ratio_empty():
    decomposer = make_decomposer()
    result = decomposer.compute_trajectory_variance_ratio([])
    assert result["n_checkpoints"] == 0
    assert result["ratio"] == 0.0


def test_compute_epoch_ratios_length():
    decomposer = make_decomposer()
    traj = make_trajectory(n_checkpoints=15)
    ratios = decomposer.compute_epoch_ratios(traj)
    assert len(ratios) == 15


def test_compute_epoch_ratios_range():
    decomposer = make_decomposer()
    traj = make_trajectory()
    ratios = decomposer.compute_epoch_ratios(traj)
    for r in ratios:
        assert 0.0 <= r <= 1.0


def test_compute_epoch_ratios_empty():
    decomposer = make_decomposer()
    ratios = decomposer.compute_epoch_ratios([])
    assert ratios == []


def test_compute_layer_breakdown_keys():
    decomposer = make_decomposer()
    traj = make_trajectory()
    breakdown = decomposer.compute_layer_breakdown(traj)
    assert isinstance(breakdown, dict)
    for ltype, stats in breakdown.items():
        assert "var_perm" in stats
        assert "var_gl" in stats
        assert "ratio" in stats


def test_compute_layer_breakdown_ratios_in_range():
    decomposer = make_decomposer()
    traj = make_trajectory()
    breakdown = decomposer.compute_layer_breakdown(traj)
    for ltype, stats in breakdown.items():
        assert 0.0 <= stats["ratio"] <= 1.0


def test_verify_mechanism_activated_pass():
    results = {
        "n_models": 150,
        "orbit_basis_dim": 32,
        "ratio_mean": 0.70,
        "var_perm_mean": 1000.0,
        "var_gl_mean": 400.0,
    }
    all_pass, indicators = verify_mechanism_activated(results)
    assert all_pass is True


def test_verify_mechanism_activated_fail_n_trajectories():
    results = {
        "n_models": 50,  # < 100
        "orbit_basis_dim": 32,
        "ratio_mean": 0.70,
        "var_perm_mean": 1000.0,
        "var_gl_mean": 400.0,
    }
    all_pass, indicators = verify_mechanism_activated(results)
    assert all_pass is False
    assert indicators["n_trajectories_gt_100"] is False


def test_verify_mechanism_activated_fail_ratio_out_of_range():
    results = {
        "n_models": 150,
        "orbit_basis_dim": 32,
        "ratio_mean": 1.5,  # > 1.0
        "var_perm_mean": 1000.0,
        "var_gl_mean": 400.0,
    }
    all_pass, indicators = verify_mechanism_activated(results)
    assert all_pass is False
    assert indicators["var_ratio_in_range"] is False
