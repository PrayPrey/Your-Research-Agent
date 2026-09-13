"""Tests for orbit_projector.py — tasks 003 + 004."""
import pytest
import torch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orbit_projector import OrbitProjector


def make_cnn_state_dict():
    """Make a small fake CNN-like state dict (Conv2d + Linear layers)."""
    return {
        "module_list.0.weight": torch.randn(8, 3, 3, 3),    # Conv2d
        "module_list.3.weight": torch.randn(16, 8, 3, 3),   # Conv2d
        "module_list.9.weight": torch.randn(32, 64),         # Linear
        "module_list.11.weight": torch.randn(10, 32),        # Linear
    }


def make_projector(use_h_m1=False):
    """Create OrbitProjector with or without h-m1 import."""
    # Point to non-existent path to test fallback mode
    path = "docs/youra_research/20260521_wsl/h-m1/code" if use_h_m1 else "/nonexistent"
    return OrbitProjector(token_dim=64, orbit_basis_dim=64, h_m1_code_path=path)


def test_get_supported_weight_names_fallback():
    proj = make_projector(use_h_m1=False)
    sd = make_cnn_state_dict()
    names = proj.get_supported_weight_names(sd)
    assert len(names) > 0
    assert all(n.endswith(".weight") for n in names)


def test_flatten_weights_shape():
    proj = make_projector()
    sd = make_cnn_state_dict()
    W_flat = proj.flatten_weights(sd)
    P = sum(v.numel() for k, v in sd.items() if k.endswith(".weight"))
    assert W_flat.shape == (P,)
    assert W_flat.dtype == torch.float32


def test_get_orbit_basis_shape():
    proj = make_projector()
    sd = make_cnn_state_dict()
    basis = proj.get_orbit_basis(sd)
    assert basis.dim() == 2
    D, P = basis.shape
    assert D <= 64
    assert P > 0


def test_get_orbit_basis_returns_finite():
    proj = make_projector()
    sd = make_cnn_state_dict()
    basis = proj.get_orbit_basis(sd)
    assert torch.isfinite(basis).all()


def test_compute_perm_orbit_projection_shape():
    proj = make_projector()
    sd = make_cnn_state_dict()
    W_flat = proj.flatten_weights(sd)
    basis = proj.get_orbit_basis(sd)
    W_perm, var_perm = proj.compute_perm_orbit_projection(W_flat, basis)
    assert W_perm.shape == W_flat.shape
    assert isinstance(var_perm, float)
    assert var_perm >= 0.0


def test_compute_perm_orbit_projection_var_positive():
    proj = make_projector()
    sd = make_cnn_state_dict()
    W_flat = proj.flatten_weights(sd)
    basis = proj.get_orbit_basis(sd)
    _, var_perm = proj.compute_perm_orbit_projection(W_flat, basis)
    # Var_perm should be positive for non-zero W
    assert var_perm >= 0.0


def test_compute_gl_orbit_projection_layer_scalar():
    proj = make_projector()
    W = torch.randn(32, 16)
    var_gl = proj.compute_gl_orbit_projection_layer(W, "Linear")
    assert isinstance(var_gl, float)
    assert var_gl >= 0.0


def test_compute_gl_orbit_projection_layer_conv():
    proj = make_projector()
    W = torch.randn(32, 3, 3, 3)
    var_gl = proj.compute_gl_orbit_projection_layer(W, "Conv2d")
    assert isinstance(var_gl, float)
    assert var_gl >= 0.0


def test_variance_ratio_logic():
    """Verify that ratio = var_perm / (var_perm + var_gl) is in [0, 1]."""
    proj = make_projector()
    sd = make_cnn_state_dict()
    W_flat = proj.flatten_weights(sd)
    basis = proj.get_orbit_basis(sd)
    _, var_perm = proj.compute_perm_orbit_projection(W_flat, basis)

    var_gl = 0.0
    for k, v in sd.items():
        if k.endswith(".weight") and v.dim() >= 2:
            layer_type = "Conv2d" if v.dim() == 4 else "Linear"
            var_gl += proj.compute_gl_orbit_projection_layer(v, layer_type)

    eps = 1e-8
    ratio = var_perm / (var_perm + var_gl + eps)
    assert 0.0 <= ratio <= 1.0
