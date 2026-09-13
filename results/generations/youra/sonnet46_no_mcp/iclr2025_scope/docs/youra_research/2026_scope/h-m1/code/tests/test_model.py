"""Tests for model.py — tasks 004-008 (H2OEvictionAwareAttention + model builder)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import torch
import torch.nn as nn
from unittest.mock import MagicMock, patch
from model import H2OEvictionAwareAttention, _get_parent


class FakeAttention(nn.Module):
    """Minimal fake attention for unit testing."""
    def __init__(self, hidden_size=64, num_heads=4):
        super().__init__()
        self.num_heads = num_heads
        head_dim = hidden_size // num_heads
        self.q_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.k_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.v_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.o_proj = nn.Linear(hidden_size, hidden_size, bias=False)

    def forward(self, hidden_states, attention_mask=None, **kwargs):
        return (hidden_states,)  # Pass-through for testing


# ── H2O Mask Tests ──────────────────────────────────────────────────────────

def test_h2o_mask_shape():
    """Mask shape must equal attn_scores shape."""
    base = FakeAttention()
    wrapper = H2OEvictionAwareAttention(base, kv_budget_ratio=0.5)
    B, H, Tq, Tk = 2, 4, 8, 8
    attn_scores = torch.randn(B, H, Tq, Tk)
    mask = wrapper.h2o_mask(attn_scores)
    assert mask.shape == attn_scores.shape, f"Expected {attn_scores.shape}, got {mask.shape}"


def test_h2o_mask_budget_fraction():
    """Fraction of True entries should approximate kv_budget_ratio."""
    base = FakeAttention()
    budget = 0.5
    wrapper = H2OEvictionAwareAttention(base, kv_budget_ratio=budget)
    B, H, Tq, Tk = 1, 1, 16, 16
    # Use uniform scores to get predictable behavior
    attn_scores = torch.ones(B, H, Tq, Tk)
    mask = wrapper.h2o_mask(attn_scores)
    # Each query position keeps ~budget fraction of keys
    # Average over T_q dimension
    frac_kept = mask.float().mean(dim=(0, 1, 2)).mean().item()
    assert abs(frac_kept - budget) < 0.15, f"Expected ~{budget}, got {frac_kept:.3f}"


def test_h2o_mask_boolean():
    """Mask must be boolean tensor."""
    base = FakeAttention()
    wrapper = H2OEvictionAwareAttention(base, kv_budget_ratio=0.5)
    attn_scores = torch.randn(1, 2, 4, 4)
    mask = wrapper.h2o_mask(attn_scores)
    assert mask.dtype == torch.bool, f"Expected bool, got {mask.dtype}"


# ── Training Guard Tests ─────────────────────────────────────────────────────

def test_inference_passthrough():
    """In eval mode, should call base_attention directly without mask."""
    base = FakeAttention()
    call_count = [0]
    original_forward = base.forward

    def counted_forward(*args, **kwargs):
        call_count[0] += 1
        return original_forward(*args, **kwargs)

    base.forward = counted_forward
    wrapper = H2OEvictionAwareAttention(base, kv_budget_ratio=0.5)
    wrapper.eval()

    hidden = torch.randn(1, 4, 64)
    wrapper(hidden)
    assert call_count[0] == 1, "Should call base_attention exactly once in eval mode"


# ── _get_parent Tests ────────────────────────────────────────────────────────

def test_get_parent_simple():
    """_get_parent should navigate nested module correctly."""
    class Outer(nn.Module):
        def __init__(self):
            super().__init__()
            self.inner = nn.Linear(4, 4)

    outer = Outer()
    parent, child_name = _get_parent(outer, "inner")
    assert parent is outer
    assert child_name == "inner"


def test_get_parent_nested():
    """_get_parent should handle two-level nesting."""
    class Deep(nn.Module):
        def __init__(self):
            super().__init__()
            self.attn = nn.Linear(4, 4)

    class Middle(nn.Module):
        def __init__(self):
            super().__init__()
            self.layer = Deep()

    mid = Middle()
    parent, child_name = _get_parent(mid, "layer.attn")
    assert parent is mid.layer
    assert child_name == "attn"
