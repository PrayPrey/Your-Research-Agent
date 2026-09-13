"""Tests for h-m1 config.py (task-003)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ExperimentConfig, VisualizationConfig, set_seed
import random, numpy as np, torch


def test_config_defaults():
    cfg = ExperimentConfig()
    assert cfg.seed == 42
    assert cfg.epochs == 150
    assert cfg.batch_size == 32
    assert cfg.lr == 1e-3
    assert cfg.embed_dim == 128
    assert cfg.sensitivity_gate == 0.3
    assert cfg.spearman_target == 0.5
    assert cfg.target_params_min == 475_000
    assert cfg.target_params_max == 525_000
    assert cfg.min_pairs == 50


def test_config_post_init():
    cfg = ExperimentConfig()
    assert isinstance(cfg.data_dir, Path)
    assert isinstance(cfg.results_dir, Path)
    assert isinstance(cfg.figures_dir, Path)
    assert isinstance(cfg.he1_code_dir, Path)


def test_set_seed_reproducibility():
    set_seed(0)
    a = random.random()
    set_seed(0)
    b = random.random()
    assert a == b


def test_visualization_config():
    vcfg = VisualizationConfig()
    assert vcfg.dpi == 150
    assert vcfg.colormap == "tab10"
