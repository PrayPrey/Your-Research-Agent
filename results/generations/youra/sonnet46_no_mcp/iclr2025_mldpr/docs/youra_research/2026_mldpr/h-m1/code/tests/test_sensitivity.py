"""Unit tests for src/sensitivity.py"""
import os, sys
import pandas as pd
import numpy as np
import pytest
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.sensitivity import run_sa1_fuji_threshold, run_sa3_observation_windows, run_all_sensitivity


def make_cfg():
    return types.SimpleNamespace(
        CALIPER_FACTOR=0.2, CALIPER_RELAXED_FACTOR=0.3,
        MIN_MATCHED_PAIRS=10, SMD_THRESHOLD=0.3, SEED=42,
        LOG_RANK_ALPHA=0.05, COX_HR_GATE=1.2, SCHOENFELD_ALPHA=0.05,
    )


def make_survival_df(n=200):
    rng = np.random.default_rng(7)
    findable = rng.uniform(0.1, 0.9, n)
    return pd.DataFrame({
        "did": range(n),
        "findable_score": findable,
        "high_findable": (findable > np.median(findable)).astype(int),
        "time_to_first_run": rng.uniform(1, 730, n),
        "event": rng.integers(0, 2, n),
        "creation_year_quartile": rng.integers(1, 5, n),
        "task_type_encoded": rng.integers(0, 3, n),
        "size_decile": rng.integers(1, 11, n),
        "fair_aggregate": rng.uniform(0, 1, n),
        "fair_F": rng.uniform(0, 1, n),
        "fair_A": rng.uniform(0, 1, n),
        "upload_date": pd.date_range("2018-01-01", periods=n, freq="30D"),
        "first_run_timestamp": pd.date_range("2018-06-01", periods=n, freq="30D"),
    })


def test_run_sa1_returns_required_keys():
    df = make_survival_df()
    cfg = make_cfg()
    result = run_sa1_fuji_threshold(df, cfg)
    assert "log_rank_p" in result
    assert result["label"] == "sa1"


def test_run_sa3_observation_windows_returns_list():
    df = make_survival_df()
    cfg = make_cfg()
    result = run_sa3_observation_windows(df, cfg, windows=[180, 365])
    assert isinstance(result, list)
    assert len(result) == 2
    assert "window_days" in result[0]


def test_run_sa3_recommendation_non_empty():
    df = make_survival_df()
    cfg = make_cfg()
    result = run_sa3_observation_windows(df, cfg, windows=[730])
    assert len(result) == 1
