"""Tests for bn_verify.py (task-005)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from bn_verify import verify_bn_free, verify_zoo_bn_free


def _make_clean_state_dict():
    return {
        "conv1.weight": torch.randn(32, 1, 3, 3),
        "conv1.bias": torch.randn(32),
        "fc1.weight": torch.randn(128, 64),
        "fc1.bias": torch.randn(128),
    }


def _make_bn_state_dict():
    sd = _make_clean_state_dict()
    sd["bn1.running_mean"] = torch.zeros(32)
    sd["bn1.running_var"] = torch.ones(32)
    return sd


def test_verify_bn_free_clean():
    assert verify_bn_free(_make_clean_state_dict()) is True


def test_verify_bn_free_with_bn():
    assert verify_bn_free(_make_bn_state_dict()) is False


def test_verify_zoo_bn_free_deterministic():
    checkpoints = [{"state_dict": _make_clean_state_dict()} for _ in range(10)]
    r1 = verify_zoo_bn_free(checkpoints, sample_size=5, seed=42)
    r2 = verify_zoo_bn_free(checkpoints, sample_size=5, seed=42)
    assert r1 == r2 is True


def test_verify_zoo_bn_free_detects_bn():
    checkpoints = [{"state_dict": _make_bn_state_dict()} for _ in range(5)]
    assert verify_zoo_bn_free(checkpoints, sample_size=3, seed=0) is False
