"""Tests for task-007: run_experiment.py orchestration."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config, ExperimentConfig


def test_config_loads():
    """get_config() returns ExperimentConfig instance."""
    cfg = get_config()
    assert isinstance(cfg, ExperimentConfig)
    assert cfg.n_stochastic_samples == 5
    assert cfg.seed == 42
    assert cfg.n_bootstrap == 1000


def test_config_gate_thresholds():
    """Gate thresholds match spec."""
    cfg = get_config()
    assert cfg.min_auroc_gap == 0.05
    assert cfg.bonferroni_k == 3
    assert abs(cfg.alpha / cfg.bonferroni_k - 0.0167) < 0.001


def test_config_model_id():
    """LLM model ID is correct."""
    cfg = get_config()
    assert "llama" in cfg.llm_model_id.lower() or "Llama" in cfg.llm_model_id


def test_auroc_direction_all_higher_is_hallucinated():
    """All methods: higher score → more hallucinated."""
    cfg = get_config()
    for method, direction in cfg.auroc_higher_is_more_hallucinated.items():
        assert direction is True, f"{method} should have higher=hallucinated"
