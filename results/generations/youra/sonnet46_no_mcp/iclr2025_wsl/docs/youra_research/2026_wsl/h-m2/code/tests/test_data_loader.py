"""Tests for h-m1 data_loader.py (tasks 004, 005) — no actual dataset required."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from data_loader import WeightDataset


def _make_checkpoints(n=20, dim=100):
    return [
        {"state_dict": {"w": torch.randn(dim)}, "test_accuracy": float(i) / n}
        for i in range(n)
    ]


def test_weight_dataset_shape():
    ckpts = _make_checkpoints(20, 100)
    ds = WeightDataset(ckpts)
    x, y = ds[0]
    assert x.shape == (100,)
    assert y.shape == ()


def test_z_score_normalization():
    ckpts = _make_checkpoints(50, 64)
    tmp = WeightDataset(ckpts)
    all_flat = torch.stack([tmp._flatten(c["state_dict"]) for c in ckpts])
    mean = all_flat.mean(0)
    std = all_flat.std(0)
    ds = WeightDataset(ckpts, mean, std)
    # Collect all tensors
    tensors = torch.stack([ds[i][0] for i in range(len(ds))])
    # After normalization the overall distribution should be near 0 mean
    assert abs(tensors.mean().item()) < 0.5


def test_dataset_len():
    ckpts = _make_checkpoints(15)
    ds = WeightDataset(ckpts)
    assert len(ds) == 15
