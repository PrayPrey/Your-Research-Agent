"""Tests for fgo.py module."""

import pytest
import torch
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fgo import create_fgo_mask, fgo_ppo_loss, standard_ppo_loss, verify_fgo_mechanism


def test_create_fgo_mask_basic():
    """Test FGO mask creation."""
    token_ids = torch.tensor([1, 2, 3, 4, 5])
    token_to_line = [1, 1, 2, 2, 3]
    executed_lines = {1, 2}

    mask = create_fgo_mask(token_ids, token_to_line, executed_lines)

    assert mask.shape == token_ids.shape
    assert mask[0] == 1.0
    assert mask[1] == 1.0
    assert mask[2] == 1.0
    assert mask[3] == 1.0
    assert mask[4] == 0.0


def test_create_fgo_mask_no_executed():
    """Test mask when no lines executed."""
    token_ids = torch.tensor([1, 2, 3])
    token_to_line = [1, 2, 3]
    executed_lines = set()

    mask = create_fgo_mask(token_ids, token_to_line, executed_lines)

    assert mask.sum() == 0.0


def test_fgo_ppo_loss_shape():
    """Test FGO PPO loss computation."""
    logprobs = torch.randn(2, 10)
    old_logprobs = torch.randn(2, 10)
    advantages = torch.randn(2, 10)
    mask = torch.ones(2, 10)

    loss = fgo_ppo_loss(logprobs, old_logprobs, advantages, mask)

    assert loss.dim() == 0
    assert loss.isfinite()


def test_fgo_ppo_loss_masked():
    """Test FGO loss with partial mask."""
    logprobs = torch.zeros(2, 10)
    old_logprobs = torch.zeros(2, 10)
    advantages = torch.ones(2, 10)
    mask = torch.zeros(2, 10)
    mask[:, :5] = 1.0

    loss = fgo_ppo_loss(logprobs, old_logprobs, advantages, mask)

    assert loss.isfinite()


def test_standard_ppo_loss():
    """Test standard PPO loss (no masking)."""
    logprobs = torch.randn(2, 10)
    old_logprobs = torch.randn(2, 10)
    advantages = torch.randn(2, 10)

    loss = standard_ppo_loss(logprobs, old_logprobs, advantages)

    assert loss.dim() == 0
    assert loss.isfinite()


def test_verify_fgo_mechanism():
    """Test FGO mechanism verification."""
    mask = torch.zeros(10)
    mask[:7] = 1.0
    logprobs = torch.randn(10)

    verify_fgo_mechanism(mask, logprobs)


def test_verify_fgo_mechanism_fails_all_ones():
    """Test verification fails when no tokens masked."""
    mask = torch.ones(10)
    logprobs = torch.randn(10)

    with pytest.raises(AssertionError):
        verify_fgo_mechanism(mask, logprobs)
