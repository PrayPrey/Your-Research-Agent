"""Smoke checks for model.py layout validation (task-003/004, LIGHT tier, no GPU)."""
import sys
import types
from pathlib import Path

import numpy as np
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model import LayoutError, validate_layout, per_layer_lens_signals


def _mock_model(with_norm=True, with_head=True, hidden=8, vocab=50):
    m = types.SimpleNamespace()
    inner = types.SimpleNamespace()
    if with_norm:
        inner.norm = torch.nn.LayerNorm(hidden)
    m.model = inner
    if with_head:
        m.lm_head = torch.nn.Linear(hidden, vocab, bias=False)
    return m


def test_validate_layout_passes():
    validate_layout(_mock_model())


def test_validate_layout_raises_on_missing_lm_head():
    with pytest.raises(LayoutError):
        validate_layout(_mock_model(with_head=False))


def test_validate_layout_raises_on_missing_norm():
    with pytest.raises(LayoutError):
        validate_layout(_mock_model(with_norm=False))


def test_per_layer_lens_signals_shapes_and_nan():
    hidden, vocab, T = 8, 50, 4
    m = _mock_model(hidden=hidden, vocab=vocab)
    torch.manual_seed(0)
    hs = tuple(torch.randn(1, T + 2, hidden) for _ in range(33))
    sig = per_layer_lens_signals(m, hs, slice(2, 2 + T))
    for k in ("entropy", "maxprob", "adj_kl", "top1_match"):
        assert sig[k].shape == (32,), k
    assert np.isnan(sig["adj_kl"][0])
    assert np.isfinite(sig["adj_kl"][1:]).all()
    assert np.isfinite(sig["entropy"]).all()
    assert sig["top1_match"][31] == 1.0     # final layer matches itself


def test_per_layer_lens_signals_wrong_length_raises():
    m = _mock_model()
    hs = tuple(torch.randn(1, 4, 8) for _ in range(30))
    with pytest.raises(LayoutError):
        per_layer_lens_signals(m, hs, slice(1, 4))
