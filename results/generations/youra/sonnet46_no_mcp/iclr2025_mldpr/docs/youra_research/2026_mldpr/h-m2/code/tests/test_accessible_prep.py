"""Tests for accessible_prep module."""
import pytest
import numpy as np
import pandas as pd
from src.accessible_prep import compute_12m_run_counts, compute_accessible_score, validate_preconditions, build_analysis_df


@pytest.fixture
def datasets_df():
    return pd.DataFrame({
        "did": [1, 2, 3, 4, 5, 6],
        "upload_date": pd.to_datetime(["2019-01-01", "2019-02-01", "2019-03-01", "2019-04-01", "2019-05-01", "2019-06-01"]),
    })


@pytest.fixture
def runs_df():
    return pd.DataFrame({
        "did": [1, 1, 1, 2, 2, 3, 4, 4, 4, 4],
        "upload_time": pd.to_datetime([
            "2019-02-01", "2019-06-01", "2020-06-01",  # did=1: 2 within 365d
            "2019-03-01", "2019-04-01",  # did=2: 2 within 365d
            "2019-04-01",  # did=3: 1
            "2019-05-01", "2019-06-01", "2019-07-01", "2019-08-01",  # did=4: 4
        ]),
    })


@pytest.fixture
def fair_scores_df():
    return pd.DataFrame({
        "did": [1, 2, 3, 4, 5, 6],
        "fair_A": [0.9, 0.8, 0.7, 0.3, 0.2, 0.1],
        "fair_F": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    })


def test_compute_12m_run_counts_basic(datasets_df, runs_df):
    result = compute_12m_run_counts(datasets_df, runs_df, window_days=365)
    assert "run_count_12m" in result.columns
    assert result[result["did"] == 1]["run_count_12m"].iloc[0] == 2  # 3rd run is beyond 365d


def test_compute_12m_run_counts_empty_runs(datasets_df):
    result = compute_12m_run_counts(datasets_df, pd.DataFrame(columns=["did", "upload_time"]))
    assert (result["run_count_12m"] == 0).all()


def test_compute_12m_run_counts_none_runs(datasets_df):
    result = compute_12m_run_counts(datasets_df, None)
    assert (result["run_count_12m"] == 0).all()


def test_compute_accessible_score_median_split(datasets_df, fair_scores_df):
    result = compute_accessible_score(datasets_df, fair_scores_df)
    assert "high_accessible" in result.columns
    assert result["high_accessible"].sum() == 3  # top 3 of 6


def test_compute_accessible_score_preserves_columns(datasets_df, fair_scores_df):
    result = compute_accessible_score(datasets_df, fair_scores_df)
    assert "did" in result.columns
    assert "fair_A" in result.columns


def test_validate_preconditions_raises():
    df = pd.DataFrame({"high_accessible": [1, 1, 1, 0, 0]})
    with pytest.raises(ValueError, match="Insufficient"):
        validate_preconditions(df, min_pairs=10)


def test_validate_preconditions_passes():
    df = pd.DataFrame({"high_accessible": [1]*50 + [0]*50})
    validate_preconditions(df, min_pairs=30)  # should not raise


def test_validate_preconditions_missing_col():
    df = pd.DataFrame({"x": [1, 2, 3]})
    with pytest.raises(ValueError, match="missing"):
        validate_preconditions(df)


def test_build_analysis_df(datasets_df, runs_df, fair_scores_df):
    result = build_analysis_df(datasets_df, runs_df, fair_scores_df, min_pairs=2)
    assert "run_count_12m" in result.columns
    assert "high_accessible" in result.columns


def test_compute_12m_window_180(datasets_df, runs_df):
    result = compute_12m_run_counts(datasets_df, runs_df, window_days=180)
    # did=1: only "2019-02-01" is within 180d of "2019-01-01"
    assert result[result["did"] == 1]["run_count_12m"].iloc[0] >= 1


def test_compute_accessible_score_all_same():
    df = pd.DataFrame({"did": [1, 2, 3], "upload_date": ["2019-01-01"]*3})
    fair = pd.DataFrame({"did": [1, 2, 3], "fair_A": [0.5, 0.5, 0.5]})
    result = compute_accessible_score(df, fair)
    # All at median → all high (>=)
    assert result["high_accessible"].sum() == 3
