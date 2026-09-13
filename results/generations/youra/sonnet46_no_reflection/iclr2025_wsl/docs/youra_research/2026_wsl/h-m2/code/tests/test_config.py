"""Tests for config.py — task-001."""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ExperimentConfig, get_config, setup_dirs


def test_default_config():
    cfg = ExperimentConfig()
    assert cfg.gate_threshold == 0.60
    assert cfg.min_models == 200
    assert cfg.min_checkpoints == 10
    assert cfg.max_checkpoints == 50
    assert cfg.orbit_basis_dim == 64
    assert cfg.token_dim == 64
    assert cfg.eps == 1e-8
    assert cfg.seed == 1
    assert cfg.device == "cpu"


def test_get_config_returns_experimentconfig():
    cfg = get_config()
    assert isinstance(cfg, ExperimentConfig)


def test_get_config_with_nonexistent_file():
    cfg = get_config("/tmp/nonexistent_config.yaml")
    assert isinstance(cfg, ExperimentConfig)
    assert cfg.gate_threshold == 0.60


def test_setup_dirs_creates_directories(tmp_path):
    cfg = ExperimentConfig()
    cfg.figures_dir = str(tmp_path / "figures")
    cfg.results_dir = str(tmp_path / "results")
    setup_dirs(cfg)
    assert Path(cfg.figures_dir).exists()
    assert Path(cfg.results_dir).exists()
