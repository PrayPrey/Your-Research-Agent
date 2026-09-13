"""Tests for config.py — E1 spec compliance."""
import os
import sys
import tempfile

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import (
    DatasetConfig,
    EvaluationConfig,
    ExperimentConfig,
    ModelConfig,
    OutputConfig,
    SamplingConfig,
    load_config,
)


def test_sampling_config_defaults():
    cfg = SamplingConfig()
    assert cfg.n_samples == 10
    assert cfg.temperature == 1.0
    assert cfg.top_p == 0.9
    assert cfg.seed == 42
    assert cfg.max_new_tokens == 50
    assert cfg.n_few_shot == 5


def test_model_config_defaults():
    cfg = ModelConfig()
    assert cfg.dtype == "bfloat16"
    assert cfg.device_map == "auto"
    assert cfg.quantization is None


def test_experiment_config_instantiation():
    cfg = ExperimentConfig()
    assert cfg.hypothesis_id == "h-e1"
    assert cfg.hypothesis_type == "EXISTENCE"
    assert isinstance(cfg.sampling, SamplingConfig)
    assert isinstance(cfg.evaluation, EvaluationConfig)
    assert isinstance(cfg.output, OutputConfig)


def test_load_config_from_yaml():
    yaml_content = {
        "hypothesis_id": "h-e1",
        "hypothesis_type": "EXISTENCE",
        "sampling": {
            "n_samples": 10,
            "temperature": 1.0,
            "top_p": 0.9,
            "seed": 42,
            "max_new_tokens": 50,
            "n_few_shot": 5,
        },
        "models": {
            "small": {"hf_id": "meta-llama/Meta-Llama-3-8B", "dtype": "bfloat16", "device_map": "auto"},
            "large": {"hf_id": "meta-llama/Meta-Llama-3-70B", "dtype": "bfloat16", "quantization": "8bit", "device_map": "auto"},
            "entailment": {"hf_id": "microsoft/deberta-large-mnli"},
        },
        "datasets": {
            "primary": [
                {"name": "trivia_qa", "hf_id": "mandarjoshi/trivia_qa", "config": "rc.nocontext", "split": "test", "size": 17944},
                {"name": "natural_questions", "hf_id": "google-research-datasets/natural_questions", "config": "default", "split": "validation", "size": 3610},
            ],
            "secondary": [
                {"name": "truthful_qa", "hf_id": "truthful_qa", "config": "mc1_targets", "split": "validation", "size": 817},
            ],
        },
        "evaluation": {"bootstrap_resamples": 1000, "alpha": 0.05, "batch_size_8b": 16, "batch_size_70b": 4, "checkpoint_every": 500},
        "output": {"base_dir": "h-e1", "figures_dir": "h-e1/figures", "results_dir": "h-e1/results", "code_dir": "h-e1/code"},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(yaml_content, f)
        tmp_path = f.name
    try:
        cfg = load_config(tmp_path)
        assert cfg.hypothesis_id == "h-e1"
        assert "small" in cfg.models
        assert "large" in cfg.models
        assert "entailment" in cfg.models
        assert cfg.models["large"].quantization == "8bit"
        assert len(cfg.datasets_primary) == 2
        assert cfg.datasets_primary[0].name == "trivia_qa"
        assert cfg.evaluation.bootstrap_resamples == 1000
    finally:
        os.unlink(tmp_path)
