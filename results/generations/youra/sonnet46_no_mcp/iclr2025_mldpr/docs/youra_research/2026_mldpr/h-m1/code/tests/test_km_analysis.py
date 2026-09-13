"""Unit tests for src/km_analysis.py"""
import os, sys
import pandas as pd
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.km_analysis import run_km_unadjusted, run_km_matched


def make_survival_df(n=100):
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "time_to_first_run": rng.uniform(1, 730, n),
        "event": rng.integers(0, 2, n),
        "high_findable": rng.integers(0, 2, n),
        "findable_score": rng.uniform(0.1, 0.9, n),
    })


def test_run_km_unadjusted_returns_p_value():
    df = make_survival_df()
    result = run_km_unadjusted(df)
    assert "baseline_log_rank_p" in result
    p = result["baseline_log_rank_p"]
    assert 0.0 <= p <= 1.0


def test_run_km_matched_returns_required_keys():
    df = make_survival_df()
    result = run_km_matched(df)
    assert "log_rank_p" in result
    assert "median_ttfr_high" in result
    assert "median_ttfr_low" in result


def test_run_km_matched_p_value_in_range():
    df = make_survival_df()
    result = run_km_matched(df)
    assert 0.0 <= result["log_rank_p"] <= 1.0
