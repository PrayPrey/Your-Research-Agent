"""Tests for data_loader.py — task-002."""
import pytest
import torch
import tempfile
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import TrajectoryDataset


def make_fake_zoo(tmp_dir: Path, n_models: int = 5, n_epochs: int = 15) -> Path:
    """Create a fake CNN Zoo directory with state dicts."""
    zoo_dir = tmp_dir / "cnn_zoo"
    zoo_dir.mkdir()
    for m in range(n_models):
        model_dir = zoo_dir / f"model_{m:04d}"
        model_dir.mkdir()
        for e in range(n_epochs):
            ckpt_dir = model_dir / f"checkpoint_{e:06d}"
            ckpt_dir.mkdir()
            state_dict = {"layer.weight": torch.randn(4, 4), "layer.bias": torch.zeros(4)}
            torch.save(state_dict, str(ckpt_dir / "checkpoints"))
    return zoo_dir


def test_discover_models_returns_valid_list(tmp_path):
    zoo_dir = make_fake_zoo(tmp_path, n_models=3, n_epochs=15)
    ds = TrajectoryDataset(zoo_dir, min_checkpoints=10)
    models = ds.discover_models()
    assert len(models) == 3
    assert all(isinstance(m, Path) for m in models)


def test_discover_models_filters_short_trajectories(tmp_path):
    zoo_dir = make_fake_zoo(tmp_path, n_models=2, n_epochs=5)
    ds = TrajectoryDataset(zoo_dir, min_checkpoints=10)
    models = ds.discover_models()
    assert len(models) == 0


def test_load_trajectory_returns_state_dicts(tmp_path):
    zoo_dir = make_fake_zoo(tmp_path, n_models=1, n_epochs=20)
    ds = TrajectoryDataset(zoo_dir, min_checkpoints=10)
    models = ds.discover_models()
    trajectory = ds.load_trajectory(models[0])
    assert len(trajectory) >= 10
    assert isinstance(trajectory[0], dict)
    assert "layer.weight" in trajectory[0]


def test_load_trajectory_respects_max_checkpoints(tmp_path):
    zoo_dir = make_fake_zoo(tmp_path, n_models=1, n_epochs=100)
    ds = TrajectoryDataset(zoo_dir, min_checkpoints=10, max_checkpoints=50)
    models = ds.discover_models()
    trajectory = ds.load_trajectory(models[0])
    assert len(trajectory) <= 50


def test_iter_trajectories_yields_pairs(tmp_path):
    zoo_dir = make_fake_zoo(tmp_path, n_models=3, n_epochs=15)
    ds = TrajectoryDataset(zoo_dir, min_checkpoints=10)
    pairs = list(ds.iter_trajectories())
    assert len(pairs) == 3
    for model_id, trajectory in pairs:
        assert isinstance(model_id, str)
        assert isinstance(trajectory, list)
        assert len(trajectory) >= 10


def test_iter_trajectories_n_models_limit(tmp_path):
    zoo_dir = make_fake_zoo(tmp_path, n_models=5, n_epochs=15)
    ds = TrajectoryDataset(zoo_dir, min_checkpoints=10)
    pairs = list(ds.iter_trajectories(n_models=2))
    assert len(pairs) == 2


def test_len_returns_count(tmp_path):
    zoo_dir = make_fake_zoo(tmp_path, n_models=4, n_epochs=12)
    ds = TrajectoryDataset(zoo_dir, min_checkpoints=10)
    assert len(ds) == 4


def test_empty_zoo_dir(tmp_path):
    empty_dir = tmp_path / "empty_zoo"
    empty_dir.mkdir()
    ds = TrajectoryDataset(empty_dir, min_checkpoints=10)
    models = ds.discover_models()
    assert models == []
    assert len(ds) == 0


def test_nonexistent_zoo_dir(tmp_path):
    ds = TrajectoryDataset(tmp_path / "nonexistent", min_checkpoints=10)
    models = ds.discover_models()
    assert models == []
