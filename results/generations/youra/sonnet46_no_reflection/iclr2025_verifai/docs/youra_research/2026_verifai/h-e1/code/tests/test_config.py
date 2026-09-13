"""Tests for config.py — spec compliance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from config import ExperimentConfig, validate_config, config_from_yaml, config_to_yaml


def test_experiment_config_defaults():
    cfg = ExperimentConfig()
    assert cfg.model_id == "ByteDance-Seed/BFS-Prover-V2-7B"
    assert cfg.beta == 10.0
    assert cfg.lr_start == 5e-6
    assert cfg.lr_end == 5e-7
    assert cfg.batch_size == 16
    assert cfg.num_epochs == 1
    assert cfg.seed == 1
    assert cfg.pass_at_1_threshold == 0.20
    assert cfg.cold_start_rollouts == 16
    assert set(cfg.conditions) == {"A", "B", "P"}
    assert cfg.gate_alpha == 0.05
    assert cfg.gate_direction == "greater"


def test_taxonomy_immutability():
    cfg = ExperimentConfig()
    assert set(cfg.taxonomy.keys()) == {"type_error", "undefined_name", "tactic_failure"}
    assert "type mismatch" in cfg.taxonomy["type_error"]
    assert "unknown identifier" in cfg.taxonomy["undefined_name"]
    assert "tactic failed" in cfg.taxonomy["tactic_failure"]


def test_validate_config_passes():
    cfg = ExperimentConfig()
    validate_config(cfg)  # Should not raise


def test_validate_config_bad_beta():
    cfg = ExperimentConfig()
    cfg.beta = -1.0
    with pytest.raises(AssertionError):
        validate_config(cfg)


def test_validate_config_bad_lr():
    cfg = ExperimentConfig()
    cfg.lr_start = cfg.lr_end  # lr_start must be > lr_end
    with pytest.raises(AssertionError):
        validate_config(cfg)


def test_validate_config_bad_conditions():
    cfg = ExperimentConfig()
    cfg.conditions = ["A", "X"]
    with pytest.raises(AssertionError):
        validate_config(cfg)


def test_config_yaml_roundtrip(tmp_path):
    cfg = ExperimentConfig()
    path = str(tmp_path / "config.yaml")
    config_to_yaml(cfg, path)
    cfg2 = config_from_yaml(path)
    assert cfg2.beta == cfg.beta
    assert cfg2.model_id == cfg.model_id
    assert set(cfg2.conditions) == set(cfg.conditions)
