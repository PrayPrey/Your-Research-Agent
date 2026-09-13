"""Tests for config.py — spec compliance."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ExperimentConfig, get_config


def test_experiment_config_defaults():
    cfg = ExperimentConfig()
    assert cfg.seed == 42
    assert cfg.ngram_n == 13
    assert cfg.stratum_percentile == 75.0
    assert cfg.minkpp_k == 0.20
    assert cfg.bootstrap_n == 10_000
    assert cfg.contamination_rate == 0.10
    assert "pile" in cfg.corpora
    assert "mmlu" in cfg.benchmarks


def test_experiment_config_validate():
    cfg = ExperimentConfig()
    cfg.validate()  # Should not raise


def test_get_config():
    cfg = get_config()
    assert isinstance(cfg, ExperimentConfig)
    assert cfg.seed == 42
