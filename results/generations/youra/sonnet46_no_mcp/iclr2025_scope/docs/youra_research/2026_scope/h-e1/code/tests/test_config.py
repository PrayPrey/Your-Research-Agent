"""Tests for config.py — task-001 and task-002."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from config import LoRAConfig, TrainingConfig, get_all_configs, validate_config


def test_lora_config_defaults():
    cfg = LoRAConfig()
    assert cfg.rank == 16
    assert cfg.alpha == 32
    assert cfg.dropout == 0.05
    assert cfg.target_modules == ["q_proj", "v_proj"]


def test_training_config_defaults():
    cfg = TrainingConfig(
        model_name="meta-llama/Llama-2-7b-hf",
        condition="baseline",
        output_dir="/tmp/test_output",
    )
    assert cfg.max_seq_length == 32768
    assert cfg.gradient_accumulation_steps == 16
    assert cfg.num_train_epochs == 1
    assert cfg.learning_rate == 2e-4
    assert cfg.seed == 42
    assert cfg.kv_budget_ratio == 0.5


def test_get_all_configs_returns_four():
    configs = get_all_configs()
    assert len(configs) == 4


def test_get_all_configs_conditions():
    configs = get_all_configs()
    conditions = [c.condition for c in configs]
    assert conditions.count("baseline") == 2
    assert conditions.count("eviction-aware") == 2


def test_get_all_configs_models():
    configs = get_all_configs()
    models = [c.model_name for c in configs]
    assert "meta-llama/Llama-2-7b-hf" in models
    assert "mistralai/Mistral-7B-v0.1" in models


def test_validate_config_valid(tmp_path):
    cfg = TrainingConfig(
        model_name="meta-llama/Llama-2-7b-hf",
        condition="baseline",
        output_dir=str(tmp_path / "out"),
    )
    validate_config(cfg)  # Should not raise


def test_validate_config_bad_condition(tmp_path):
    cfg = TrainingConfig(
        model_name="meta-llama/Llama-2-7b-hf",
        condition="invalid",
        output_dir=str(tmp_path / "out"),
    )
    with pytest.raises(AssertionError):
        validate_config(cfg)


def test_validate_config_bad_kv_ratio(tmp_path):
    cfg = TrainingConfig(
        model_name="meta-llama/Llama-2-7b-hf",
        condition="baseline",
        output_dir=str(tmp_path / "out"),
        kv_budget_ratio=1.5,
    )
    with pytest.raises(AssertionError):
        validate_config(cfg)


def test_validate_config_fp16_bf16_conflict(tmp_path):
    cfg = TrainingConfig(
        model_name="meta-llama/Llama-2-7b-hf",
        condition="baseline",
        output_dir=str(tmp_path / "out"),
        fp16=True,
        bf16=True,
    )
    with pytest.raises(AssertionError):
        validate_config(cfg)
