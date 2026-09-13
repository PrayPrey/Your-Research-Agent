"""Tests for train.py — tasks 009-010."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from config import TrainingConfig
from train import get_training_args


def make_cfg(**kwargs):
    defaults = dict(
        model_name="meta-llama/Llama-2-7b-hf",
        condition="baseline",
        output_dir="/tmp/test_train_args",
    )
    defaults.update(kwargs)
    return TrainingConfig(**defaults)


def test_get_training_args_gradient_checkpointing():
    """gradient_checkpointing must be True (required for 32k seq len)."""
    cfg = make_cfg()
    args = get_training_args(cfg)
    assert args.gradient_checkpointing is True


def test_get_training_args_optimizer():
    """Optimizer must be adamw_torch."""
    cfg = make_cfg()
    args = get_training_args(cfg)
    assert args.optim == "adamw_torch"


def test_get_training_args_ddp():
    """ddp_find_unused_parameters must be False."""
    cfg = make_cfg()
    args = get_training_args(cfg)
    assert args.ddp_find_unused_parameters is False


def test_get_training_args_remove_unused_columns():
    """remove_unused_columns must be False (needed for custom dataset)."""
    cfg = make_cfg()
    args = get_training_args(cfg)
    assert args.remove_unused_columns is False


def test_get_training_args_fields_mapped():
    """All TrainingConfig fields should be correctly mapped."""
    cfg = make_cfg(
        num_train_epochs=2,
        learning_rate=1e-4,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        seed=123,
    )
    args = get_training_args(cfg)
    assert args.num_train_epochs == 2
    assert args.learning_rate == 1e-4
    assert args.per_device_train_batch_size == 2
    assert args.gradient_accumulation_steps == 8
    assert args.seed == 123


def test_get_training_args_save_strategy():
    """save_strategy should be 'no' (final adapter only)."""
    cfg = make_cfg()
    args = get_training_args(cfg)
    assert args.save_strategy == "no"
