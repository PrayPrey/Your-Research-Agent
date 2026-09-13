"""Tests for train.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from train import (
    EPOCHS_PER_CONDITION,
    FIXED_HPARAMS,
    IMPROVEMENT_THRESHOLD,
    CONDITIONS,
    SEEDS,
    set_all_seeds,
    verify_sft_activation,
)


def test_epochs_per_condition_coverage():
    assert set(EPOCHS_PER_CONDITION.keys()) == set(CONDITIONS)


def test_set_all_seeds_deterministic():
    import numpy as np
    import torch
    set_all_seeds(42)
    a = np.random.rand()
    set_all_seeds(42)
    b = np.random.rand()
    assert a == b


def test_verify_sft_activation_pass():
    # +3 pp on humaneval → should activate
    assert verify_sft_activation(0.15 + 0.04, 0.40, "humaneval_only") is True


def test_verify_sft_activation_fail():
    # No improvement on either benchmark
    assert verify_sft_activation(0.13, 0.43, "humaneval_only") is False


def test_verify_sft_activation_mbpp_only():
    # +3 pp on mbpp only
    assert verify_sft_activation(0.10, 0.45 + 0.04, "mbpp_only") is True


def test_fixed_hparams_present():
    required = {"learning_rate", "bf16", "per_device_train_batch_size", "gradient_accumulation_steps"}
    assert required.issubset(set(FIXED_HPARAMS.keys()))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
