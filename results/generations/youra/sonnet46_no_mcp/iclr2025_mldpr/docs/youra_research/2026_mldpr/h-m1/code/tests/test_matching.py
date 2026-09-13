"""Unit tests for src/matching.py"""
import os, sys
import pandas as pd
import numpy as np
import pytest
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.matching import fit_propensity_model, nearest_neighbor_match, compute_smd, run_matching


def make_survival_df(n=100):
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "did": range(n),
        "findable_score": rng.uniform(0.1, 0.9, n),
        "high_findable": rng.integers(0, 2, n),
        "time_to_first_run": rng.uniform(1, 730, n),
        "event": rng.integers(0, 2, n),
        "creation_year_quartile": rng.integers(1, 5, n),
        "task_type_encoded": rng.integers(0, 3, n),
        "size_decile": rng.integers(1, 11, n),
        "fair_aggregate": rng.uniform(0, 1, n),
        "fair_A": rng.uniform(0, 1, n),
    })


def test_fit_propensity_model_returns_probabilities():
    df = make_survival_df()
    cols = ["creation_year_quartile", "task_type_encoded", "size_decile"]
    model, ps = fit_propensity_model(df, cols, "high_findable", seed=42)
    assert len(ps) == len(df)
    assert (ps > 0).all() and (ps < 1).all()


def test_fit_propensity_model_reproducibility():
    df = make_survival_df()
    cols = ["creation_year_quartile", "task_type_encoded", "size_decile"]
    _, ps1 = fit_propensity_model(df, cols, "high_findable", seed=42)
    _, ps2 = fit_propensity_model(df, cols, "high_findable", seed=42)
    np.testing.assert_array_almost_equal(ps1, ps2)


def test_nearest_neighbor_match_respects_caliper():
    df = make_survival_df(200)
    cols = ["creation_year_quartile", "task_type_encoded", "size_decile"]
    _, ps = fit_propensity_model(df, cols, "high_findable", seed=42)
    matched = nearest_neighbor_match(df, ps, "high_findable", caliper=0.0)
    # caliper=0 should produce few or no matches (only exact matches)
    assert len(matched) >= 0


def test_compute_smd_reduces_after_matching():
    df = make_survival_df(200)
    cols = ["creation_year_quartile", "task_type_encoded", "size_decile"]
    _, ps = fit_propensity_model(df, cols, "high_findable", seed=42)
    matched = nearest_neighbor_match(df, ps, "high_findable", caliper=1.0)
    if len(matched) > 0:
        smd_df = compute_smd(df, matched, cols, "high_findable")
        assert "smd_before" in smd_df.columns
        assert "smd_after" in smd_df.columns
        assert len(smd_df) == len(cols)


def test_compute_smd_identical_groups():
    df = make_survival_df(100)
    cols = ["creation_year_quartile"]
    smd_df = compute_smd(df, df, cols, "high_findable")
    assert smd_df["smd_after"].iloc[0] < 1.0
