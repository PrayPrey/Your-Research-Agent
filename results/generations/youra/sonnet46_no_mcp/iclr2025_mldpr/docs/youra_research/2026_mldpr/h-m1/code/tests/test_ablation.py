"""Unit tests for src/ablation.py"""
import os, sys
import pandas as pd
import numpy as np
import pytest
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.ablation import run_ablation_a, run_ablation_b, run_all_ablations


def make_cfg():
    return types.SimpleNamespace(
        CALIPER_FACTOR=0.2, CALIPER_RELAXED_FACTOR=0.3,
        MIN_MATCHED_PAIRS=10, SMD_THRESHOLD=0.3, SEED=42,
        LOG_RANK_ALPHA=0.05, COX_HR_GATE=1.2, SCHOENFELD_ALPHA=0.05,
    )


def make_survival_df(n=200):
    rng = np.random.default_rng(42)
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
    })


def test_run_ablation_a_returns_required_keys():
    df = make_survival_df()
    cfg = make_cfg()
    result = run_ablation_a(df, cfg)
    assert "log_rank_p" in result
    assert "cox_hr" in result
    assert "n_matched_pairs" in result
    assert result["label"] == "ablation_a"


def test_run_ablation_b_uses_accessible_score():
    df = make_survival_df()
    cfg = make_cfg()
    result = run_ablation_b(df, cfg)
    assert result["label"] == "ablation_b"
    assert "log_rank_p" in result


def test_run_all_ablations_returns_three_labels():
    df = make_survival_df()
    cfg = make_cfg()
    result = run_all_ablations(df, cfg)
    assert "ablation_a" in result
    assert "ablation_b" in result
    assert "ablation_c" in result
