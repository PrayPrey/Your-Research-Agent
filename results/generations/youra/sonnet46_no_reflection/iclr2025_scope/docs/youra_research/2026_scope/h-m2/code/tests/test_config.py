import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import (
    ExperimentConfig, LoRAConfig, LocretConfig, TrainingConfig,
    DatasetConfig, StabilityConfig, PathConfig, validate_config,
    load_config, save_config
)
import tempfile, yaml


def test_default_config():
    cfg = ExperimentConfig()
    assert cfg.lora.r == 16
    assert cfg.lora.lora_alpha == 32
    assert cfg.locret.kv_budget_ratio == 0.5
    assert cfg.training.seeds == [42, 123, 456]
    assert cfg.stability.divergence_threshold == 2.0


def test_validate_config_passes():
    cfg = ExperimentConfig()
    validate_config(cfg)  # should not raise


def test_validate_config_invalid_budget():
    cfg = ExperimentConfig()
    cfg.locret.kv_budget_ratio = 1.5
    try:
        validate_config(cfg)
        assert False, "Should have raised"
    except AssertionError:
        pass


def test_save_load_roundtrip():
    cfg = ExperimentConfig()
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        path = f.name
    save_config(cfg, path)
    cfg2 = load_config(path)
    assert cfg2.lora.r == cfg.lora.r
    assert cfg2.training.seeds == cfg.training.seeds
    assert cfg2.locret.kv_budget_ratio == cfg.locret.kv_budget_ratio
    os.unlink(path)


def test_glue_tasks_present():
    cfg = ExperimentConfig()
    assert "mnli" in cfg.dataset.glue_tasks
    assert "sst2" in cfg.dataset.glue_tasks
    assert "qnli" in cfg.dataset.glue_tasks


def test_longbench_tasks_present():
    cfg = ExperimentConfig()
    assert "narrativeqa" in cfg.dataset.longbench_tasks
    assert "qasper" in cfg.dataset.longbench_tasks
    assert "multifieldqa_en" in cfg.dataset.longbench_tasks
