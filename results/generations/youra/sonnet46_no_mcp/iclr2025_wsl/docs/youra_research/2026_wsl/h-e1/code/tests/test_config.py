"""Tests for config.py (task-003)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ExperimentConfig, VisualizationConfig


def test_experiment_config_defaults():
    cfg = ExperimentConfig()
    assert cfg.zoo_name == "mnist_cnn"
    assert cfg.seed == 42
    assert cfg.n_per_decile == 50
    assert cfg.n_deciles == 10
    assert cfg.acc_threshold == 0.01
    assert cfg.cosine_dist_threshold == 0.1
    assert cfg.orbit_proportion_gate == 0.05
    assert cfg.bn_verify_sample_size == 5


def test_n_pairs_property():
    cfg = ExperimentConfig()
    assert cfg.n_pairs == 500  # 50 * 10


def test_path_coercion():
    cfg = ExperimentConfig(data_dir="./data", results_dir="./results", figures_dir="./figures")
    assert isinstance(cfg.data_dir, Path)
    assert isinstance(cfg.results_dir, Path)
    assert isinstance(cfg.figures_dir, Path)


def test_visualization_config_defaults():
    vis = VisualizationConfig()
    assert vis.dpi == 150
