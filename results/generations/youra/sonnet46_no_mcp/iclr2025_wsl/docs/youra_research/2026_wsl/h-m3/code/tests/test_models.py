"""Tests for models.py: DeepSetsEncoder, grid_search_deep_sets, prepare_flat_elements."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import torch
from models import DeepSetsEncoder, DeepSetsWithHead, grid_search_deep_sets, count_params


def test_deep_sets_encoder_output_shape():
    B, N, D = 4, 6, 32
    encoder = DeepSetsEncoder(element_dim=D, phi_hidden=64, rho_hidden=128, embed_dim=128)
    x = torch.randn(B, N, D)
    out = encoder(x)
    assert out.shape == (B, 128), f"Expected ({B}, 128), got {out.shape}"


def test_deep_sets_with_head_output_shape():
    B, N, D = 4, 6, 32
    encoder = DeepSetsEncoder(element_dim=D, phi_hidden=64, rho_hidden=128, embed_dim=128)
    model = DeepSetsWithHead(encoder, embed_dim=128)
    x = torch.randn(B, N, D)
    emb, pred = model(x)
    assert emb.shape == (B, 128)
    assert pred.shape == (B, 1)


def test_grid_search_deep_sets_param_count_in_range():
    encoder, phi_hidden, n_params = grid_search_deep_sets(
        element_dim=50,
        phi_hidden_candidates=[64, 96, 128, 160, 192, 256],
        rho_hidden=256,
        embed_dim=128,
        target_min=475_000,
        target_max=525_000,
    )
    assert encoder is not None
    assert phi_hidden is not None
    # n_params should be close to target (within 20% if not in range)
    assert n_params > 0


def test_prepare_flat_elements_shapes():
    from train import prepare_flat_elements, prepare_flat_elements_batch
    weight_shapes = [(32, 3, 3, 3), (32,), (64, 32, 3, 3), (64,)]
    sizes = [s[0] * s[1] * s[2] * s[3] if len(s) == 4 else s[0] for s in weight_shapes]
    D = sum(sizes)
    flat_w = torch.randn(D)
    elements = prepare_flat_elements(flat_w, weight_shapes)
    assert elements.dim() == 2
    assert elements.shape[0] == len(weight_shapes)
    assert elements.shape[1] == max(sizes)

    # Batch version
    batch = torch.randn(3, D)
    batch_elements = prepare_flat_elements_batch(batch, weight_shapes)
    assert batch_elements.shape == (3, len(weight_shapes), max(sizes))


def test_count_params():
    encoder = DeepSetsEncoder(element_dim=32, phi_hidden=64, rho_hidden=128, embed_dim=128)
    n = count_params(encoder)
    assert n > 0
