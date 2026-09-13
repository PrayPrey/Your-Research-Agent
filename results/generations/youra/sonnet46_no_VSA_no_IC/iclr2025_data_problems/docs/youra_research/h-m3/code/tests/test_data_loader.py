"""Tests for data_loader module."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import pytest
from src.data_loader import (
    load_h_e1_trajectories,
    load_eval_cache,
    build_panel_dataframe,
    verify_books3_variance,
)
import config as cfg


def test_load_h_e1_trajectories_returns_dict():
    traj = load_h_e1_trajectories(
        cfg.H_E1_EXPOSURE_DIR, cfg.MODEL_SIZES[:3],
        cfg.CHECKPOINT_STEPS, cfg.PILE_DOMAINS
    )
    assert isinstance(traj, dict)
    assert len(traj) == 3


def test_load_h_e1_available_models():
    traj = load_h_e1_trajectories(
        cfg.H_E1_EXPOSURE_DIR, cfg.MODEL_SIZES,
        cfg.CHECKPOINT_STEPS, cfg.PILE_DOMAINS
    )
    available = [s for s, v in traj.items() if v is not None]
    assert len(available) >= 1, "At least one model size should have H-E1 data"


def test_h_e1_shape():
    traj = load_h_e1_trajectories(
        cfg.H_E1_EXPOSURE_DIR, ["70m"],
        cfg.CHECKPOINT_STEPS, cfg.PILE_DOMAINS
    )
    arr = traj["70m"]
    assert arr is not None
    assert len(arr.shape) == 2
    n_domains, n_ckpts = arr.shape
    assert n_domains == 22, f"Expected 22 domains, got {n_domains}"
    assert n_ckpts == 154, f"Expected 154 checkpoints, got {n_ckpts}"


def test_load_eval_cache_returns_dict():
    ev = load_eval_cache(
        cfg.EVAL_CACHE_DIR, ["70m"], cfg.CHECKPOINT_STEPS, cfg.TASKS
    )
    assert isinstance(ev, dict)
    assert "70m" in ev


def test_build_panel_dataframe_multiindex():
    """Panel has correct MultiIndex structure."""
    traj = load_h_e1_trajectories(
        cfg.H_E1_EXPOSURE_DIR, ["70m", "1b"],
        cfg.CHECKPOINT_STEPS, cfg.PILE_DOMAINS
    )
    ev = load_eval_cache(cfg.EVAL_CACHE_DIR, ["70m", "1b"], cfg.CHECKPOINT_STEPS, cfg.TASKS)

    usable = [s for s in ["70m", "1b"] if traj.get(s) is not None and ev.get(s)]
    if len(usable) < 1:
        pytest.skip("No usable model sizes with both H-E1 and eval data")

    panel_df = build_panel_dataframe(
        {s: traj[s] for s in usable}, ev,
        cfg.CHECKPOINT_STEPS, cfg.PILE_DOMAINS, cfg.TASKS, cfg.MODEL_PARAMS,
        floor_threshold=0.10, min_valid_checkpoints=1,
    )
    assert panel_df.index.names == ["model_size", "checkpoint"]
    assert len(panel_df) > 0


def test_verify_books3_variance_raises_on_zero():
    """verify_books3_variance raises ValueError when Books3 has zero variance."""
    idx = pd.MultiIndex.from_tuples([("m1", 0), ("m1", 1), ("m2", 0), ("m2", 1)],
                                     names=["model_size", "checkpoint"])
    df = pd.DataFrame({"Books3": [0.1, 0.1, 0.1, 0.1], "mmlu": [0.3, 0.4, 0.5, 0.6]}, index=idx)
    with pytest.raises(ValueError, match="Books3"):
        verify_books3_variance(df)


def test_verify_books3_variance_passes_with_variation():
    idx = pd.MultiIndex.from_tuples([("m1", 0), ("m1", 1), ("m2", 0), ("m2", 1)],
                                     names=["model_size", "checkpoint"])
    df = pd.DataFrame({"Books3": [0.1, 0.2, 0.3, 0.4]}, index=idx)
    var = verify_books3_variance(df)
    assert var > 1e-6
