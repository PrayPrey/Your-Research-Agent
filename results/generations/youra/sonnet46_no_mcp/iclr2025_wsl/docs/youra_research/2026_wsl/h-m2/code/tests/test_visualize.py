"""Tests for h-m1 visualize.py (task-017)."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from config import ExperimentConfig
from train import TrainHistory
from visualize import (
    plot_gate_metrics,
    plot_l2_distribution,
    plot_training_curve,
    plot_sensitivity_by_decile,
    plot_embedding_scatter,
)


def _cfg_with_tmpdir(d):
    cfg = ExperimentConfig()
    cfg.figures_dir = Path(d)
    return cfg


def test_gate_metrics_creates_file():
    with tempfile.TemporaryDirectory() as d:
        cfg = _cfg_with_tmpdir(d)
        plot_gate_metrics(0.5, 0.6, cfg)
        assert (Path(d) / "gate_metrics.png").exists()


def test_l2_distribution_creates_file():
    with tempfile.TemporaryDirectory() as d:
        cfg = _cfg_with_tmpdir(d)
        plot_l2_distribution([0.1, 0.2, 0.3], [0.5, 0.6, 0.7], cfg)
        assert (Path(d) / "l2_distance_distribution.png").exists()


def test_training_curve_creates_file():
    with tempfile.TemporaryDirectory() as d:
        cfg = _cfg_with_tmpdir(d)
        h = TrainHistory(
            train_loss=[0.5, 0.4],
            val_loss=[0.6, 0.5],
            train_spearman=[0.3, 0.4],
            val_spearman=[0.2, 0.3],
        )
        plot_training_curve(h, cfg)
        assert (Path(d) / "training_curve.png").exists()


def test_sensitivity_by_decile_creates_file():
    with tempfile.TemporaryDirectory() as d:
        cfg = _cfg_with_tmpdir(d)
        plot_sensitivity_by_decile([0.1] * 10, cfg)
        assert (Path(d) / "sensitivity_by_decile.png").exists()


def test_embedding_scatter_creates_file():
    with tempfile.TemporaryDirectory() as d:
        cfg = _cfg_with_tmpdir(d)
        embs = torch.randn(20, 8)
        accs = [float(i) / 20 for i in range(20)]
        plot_embedding_scatter(embs, accs, [], cfg)
        assert (Path(d) / "embedding_scatter.png").exists()
