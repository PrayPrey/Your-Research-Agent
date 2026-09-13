"""Unit tests for src/cox_analysis.py"""
import os, sys
import pandas as pd
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.cox_analysis import fit_cox, run_cox_primary


def make_matched_df(n=100):
    rng = np.random.default_rng(1)
    findable = rng.uniform(0.1, 0.9, n)
    ttfr = np.maximum(1, 730 - findable * 500 + rng.normal(0, 50, n))
    return pd.DataFrame({
        "time_to_first_run": ttfr,
        "event": rng.integers(0, 2, n),
        "findable_score": findable,
        "high_findable": (findable > 0.5).astype(int),
    })


def test_fit_cox_returns_positive_hr():
    df = make_matched_df()
    cph, hr, ci_lower, ci_upper = fit_cox(df, formula="findable_score")
    assert hr > 0


def test_fit_cox_ci_ordering():
    df = make_matched_df()
    cph, hr, ci_lower, ci_upper = fit_cox(df, formula="findable_score")
    assert ci_lower < hr < ci_upper


def test_run_cox_primary_returns_required_keys():
    df = make_matched_df()
    result = run_cox_primary(df, predictor_col="findable_score")
    assert "cox_hr" in result
    assert "cox_ci_lower" in result
    assert "cox_ci_upper" in result
    assert "cox_p" in result
    assert result["cox_hr"] > 0
