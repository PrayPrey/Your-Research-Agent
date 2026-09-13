"""Unit tests for src/survival_prep.py"""
import os, sys
import pandas as pd
import numpy as np
import pytest
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.survival_prep import compute_time_to_first_run, encode_covariates, validate_preconditions


def make_cohort(n=50):
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "did": range(n),
        "upload_date": pd.date_range("2018-01-01", periods=n, freq="30D"),
        "first_run_timestamp": pd.date_range("2018-06-01", periods=n, freq="30D"),
        "run_count": rng.integers(10, 100, n),
        "task_type": rng.choice(["supervised_classification", "supervised_regression"], n),
        "NumberOfInstances": rng.integers(100, 10000, n).astype(float),
        "findable_score": rng.uniform(0.1, 0.9, n),
        "high_findable": rng.integers(0, 2, n),
    })


def test_compute_time_to_first_run_event_flag():
    cohort = make_cohort()
    result = compute_time_to_first_run(cohort, observation_window_days=730)
    assert "event" in result.columns
    assert "time_to_first_run" in result.columns
    assert result["event"].isin([0, 1]).all()


def test_compute_time_to_first_run_censoring():
    cohort = make_cohort(10)
    cohort["first_run_timestamp"] = pd.NaT  # all censored
    result = compute_time_to_first_run(cohort, observation_window_days=730)
    assert result["event"].sum() == 0
    assert (result["time_to_first_run"] == 730).all()


def test_encode_covariates_decile_range():
    cohort = make_cohort()
    result = encode_covariates(cohort)
    assert "size_decile" in result.columns
    assert result["size_decile"].between(1, 10).all()


def test_validate_preconditions_returns_dict():
    cohort = make_cohort()
    cohort = compute_time_to_first_run(cohort, 730)
    cfg = types.SimpleNamespace(MIN_MATCHED_PAIRS=100)
    result = validate_preconditions(cohort, cfg)
    assert isinstance(result, dict)
    assert "mechanism_exists" in result
