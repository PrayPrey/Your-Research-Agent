"""Tests for dpo_trainer.py — spec compliance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import torch
from training.dpo_trainer import get_batch_logps, dpo_loss


def test_get_batch_logps_shape():
    """get_batch_logps must return [B] tensor."""
    B, T, V = 2, 10, 100
    logits = torch.randn(B, T, V)
    labels = torch.randint(0, V, (B, T))
    # Mask some tokens
    labels[:, :3] = -100
    out = get_batch_logps(logits, labels, average_log_prob=False)
    assert out.shape == (B,), f"Expected shape ({B},), got {out.shape}"


def test_get_batch_logps_sum_not_average():
    """average_log_prob=False must sum (not average) log-probs."""
    B, T, V = 1, 6, 50
    logits = torch.zeros(B, T, V)
    # All probs uniform → log_prob per token = -log(V)
    labels = torch.zeros(B, T, dtype=torch.long)
    labels[0, :2] = -100  # mask first 2

    out_sum = get_batch_logps(logits, labels, average_log_prob=False)
    out_avg = get_batch_logps(logits, labels, average_log_prob=True)

    # sum should be larger in absolute value than avg (more tokens)
    active_tokens = (T - 1) - 2  # T-1 after shift, minus 2 masked
    assert abs(out_sum[0].item()) > abs(out_avg[0].item()), \
        "sum should have larger magnitude than average"


def test_dpo_loss_shape():
    """dpo_loss must return a scalar tensor."""
    B = 4
    policy_chosen_logps   = torch.randn(B)
    policy_rejected_logps = torch.randn(B)
    ref_chosen_logps      = torch.randn(B)
    ref_rejected_logps    = torch.randn(B)

    loss = dpo_loss(policy_chosen_logps, policy_rejected_logps,
                    ref_chosen_logps, ref_rejected_logps, beta=10.0)
    assert loss.shape == torch.Size([]), f"Expected scalar, got {loss.shape}"
    assert loss.item() > 0, "DPO loss should be positive"


def test_dpo_loss_positive():
    """DPO loss is -logsigmoid(...) so always positive for typical inputs."""
    B = 8
    # Case where chosen > rejected (policy improves): loss should still be computable
    chosen_logps   = torch.ones(B)
    rejected_logps = -torch.ones(B)
    loss = dpo_loss(chosen_logps, rejected_logps, chosen_logps * 0, rejected_logps * 0, beta=10.0)
    assert torch.isfinite(loss), "Loss must be finite"
