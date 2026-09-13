"""Tests for A-3: Checkpoint Linear Probe Battery (spec compliance)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from config import ProbeConfig


def test_probe_import():
    from probe import extract_features, fit_probe, run_probe_battery, run_all_seeds
    assert extract_features is not None
    assert fit_probe is not None
    assert run_probe_battery is not None
    assert run_all_seeds is not None


def test_extract_features_shape():
    """extract_features must return (N,2048), (N,), (N,) arrays."""
    from probe import extract_features
    from train import build_model

    model = build_model(pretrained=False)
    model.eval()

    # Synthetic loader
    N = 8
    images = torch.randn(N, 3, 224, 224)
    core_labels = torch.randint(0, 2, (N,))
    spurious_labels = torch.randint(0, 2, (N,))
    batch = {"image": images, "core_label": core_labels, "spurious_label": spurious_labels}
    loader = [batch]

    feats, core_arr, spur_arr = extract_features(model, loader, device="cpu")
    assert feats.shape == (N, 2048), f"Expected (8, 2048), got {feats.shape}"
    assert core_arr.shape == (N,)
    assert spur_arr.shape == (N,)


def test_extract_features_model_eval():
    """extract_features must call model.eval() and use no_grad."""
    from probe import extract_features
    from train import build_model

    model = build_model(pretrained=False)
    model.train()  # Start in train mode
    N = 4
    loader = [{"image": torch.randn(N, 3, 224, 224),
               "core_label": torch.zeros(N, dtype=torch.long),
               "spurious_label": torch.zeros(N, dtype=torch.long)}]
    extract_features(model, loader, device="cpu")
    # After extract_features, model should be in eval mode
    assert not model.training


def test_fit_probe_returns_float():
    from probe import fit_probe
    cfg = ProbeConfig()
    rng = np.random.RandomState(42)
    feats = rng.randn(50, 2048).astype(np.float32)
    labels = rng.randint(0, 2, 50)
    acc = fit_probe(feats, labels, cfg)
    assert isinstance(acc, float)
    assert 0.0 <= acc <= 1.0


def test_fit_probe_hyperparams():
    """fit_probe must use C=1.0, solver=lbfgs, max_iter=1000."""
    from probe import fit_probe
    from unittest.mock import patch, MagicMock

    cfg = ProbeConfig(C=1.0, max_iter=1000, solver="lbfgs", random_state=42)
    mock_probe = MagicMock()
    mock_probe.score.return_value = 0.75

    with patch("probe.LogisticRegression", return_value=mock_probe) as mock_lr:
        feats = np.random.randn(20, 10).astype(np.float32)
        labels = np.random.randint(0, 2, 20)
        fit_probe(feats, labels, cfg)
        mock_lr.assert_called_once_with(
            C=1.0, max_iter=1000, solver="lbfgs", random_state=42
        )


def test_run_probe_battery_dataframe_schema(tmp_path):
    """run_probe_battery must return DataFrame with [epoch, spurious_acc, core_acc, delta]."""
    from probe import run_probe_battery
    from train import build_model
    from config import ExperimentConfig, TrainConfig, ProbeConfig, GateConfig, DatasetPathConfig
    import pandas as pd
    from PIL import Image

    # Build minimal waterbirds
    wb_root = tmp_path / "waterbirds"
    wb_root.mkdir()
    img_dir = wb_root / "images"
    img_dir.mkdir()
    rows = []
    for i in range(4):
        fname = f"b{i}.jpg"
        Image.new("RGB", (256, 256)).save(str(img_dir / fname))
        rows.append({"img_id": i, "img_filename": f"images/{fname}",
                     "y": i % 2, "split": 1, "place": (i+1)%2,
                     "place_filename": "/p/p.jpg"})
    pd.DataFrame(rows).to_csv(str(wb_root / "metadata.csv"), index=False)

    # Build checkpoint
    ckpt_dir = tmp_path / "ckpts" / "waterbirds"
    seed_dir = ckpt_dir / "seed_1"
    seed_dir.mkdir(parents=True)
    model = build_model(pretrained=False)
    torch.save(model.state_dict(), str(seed_dir / "epoch_002.pt"))

    cfg = ExperimentConfig(
        train=TrainConfig(
            dataset="waterbirds",
            data_root=str(wb_root),
            checkpoint_dir=str(ckpt_dir),
            epochs=2,
            checkpoint_interval=2,
            batch_size=4,
            seeds=[1],
            num_workers=0,
        ),
        probe=ProbeConfig(),
        gate=GateConfig(),
        paths=DatasetPathConfig(),
        results_dir=str(tmp_path / "results"),
    )
    df = run_probe_battery(cfg, seed=1, device="cpu")
    assert isinstance(df, pd.DataFrame)
    for col in ["epoch", "spurious_acc", "core_acc", "delta"]:
        assert col in df.columns, f"Missing column: {col}"


def test_run_all_seeds_has_seed_column(tmp_path):
    """run_all_seeds must add 'seed' column to combined DataFrame."""
    from probe import run_all_seeds
    from train import build_model
    from config import ExperimentConfig, TrainConfig, ProbeConfig, GateConfig, DatasetPathConfig
    import pandas as pd
    from PIL import Image

    wb_root = tmp_path / "waterbirds"
    wb_root.mkdir()
    img_dir = wb_root / "images"
    img_dir.mkdir()
    rows = []
    for i in range(4):
        fname = f"b{i}.jpg"
        Image.new("RGB", (256, 256)).save(str(img_dir / fname))
        rows.append({"img_id": i, "img_filename": f"images/{fname}",
                     "y": i % 2, "split": 1, "place": (i+1)%2,
                     "place_filename": "/p/p.jpg"})
    pd.DataFrame(rows).to_csv(str(wb_root / "metadata.csv"), index=False)

    ckpt_dir = tmp_path / "ckpts" / "waterbirds"
    for seed in [1, 2]:
        seed_dir = ckpt_dir / f"seed_{seed}"
        seed_dir.mkdir(parents=True)
        model = build_model(pretrained=False)
        torch.save(model.state_dict(), str(seed_dir / "epoch_002.pt"))

    cfg = ExperimentConfig(
        train=TrainConfig(
            dataset="waterbirds",
            data_root=str(wb_root),
            checkpoint_dir=str(ckpt_dir),
            epochs=2,
            checkpoint_interval=2,
            batch_size=4,
            seeds=[1, 2],
            num_workers=0,
        ),
        probe=ProbeConfig(),
        gate=GateConfig(),
        paths=DatasetPathConfig(),
        results_dir=str(tmp_path / "results"),
    )
    df = run_all_seeds(cfg, device="cpu")
    assert "seed" in df.columns
    assert set(df["seed"].unique()) == {1, 2}
