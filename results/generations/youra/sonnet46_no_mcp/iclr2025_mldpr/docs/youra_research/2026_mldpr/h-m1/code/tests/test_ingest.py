"""Unit tests for src/ingest.py"""
import os
import sys
import json
import tempfile
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.ingest import load_he1_scores, build_merged_cohort, fetch_run_timestamps


def make_he1_csv(tmp_path):
    df = pd.DataFrame({
        "did": [1, 2, 3],
        "fair_aggregate": [0.3, 0.7, 0.5],
        "fair_F": [0.2, 0.8, 0.5],
        "fair_A": [0.4, 0.6, 0.5],
        "fair_I": [0.3, 0.7, 0.5],
        "fair_R": [0.3, 0.7, 0.5],
        "status": ["fallback", "fallback", "error"],
    })
    path = str(tmp_path / "fair_scores.csv")
    df.to_csv(path, index=False)
    return path


def test_load_he1_scores_valid_csv(tmp_path):
    path = make_he1_csv(tmp_path)
    df = load_he1_scores(path)
    assert "did" in df.columns
    assert "fair_aggregate" in df.columns
    assert len(df) == 2  # status='error' row filtered out


def test_load_he1_scores_missing_columns(tmp_path):
    bad_csv = str(tmp_path / "bad.csv")
    pd.DataFrame({"did": [1], "fair_aggregate": [0.5]}).to_csv(bad_csv, index=False)
    with pytest.raises(ValueError, match="Missing required columns"):
        load_he1_scores(bad_csv)


def test_load_he1_scores_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_he1_scores("/nonexistent/path.csv")


def test_build_merged_cohort_min_run_filter():
    he1 = pd.DataFrame({
        "did": [1, 2, 3],
        "fair_aggregate": [0.3, 0.7, 0.5],
        "fair_F": [0.2, 0.8, 0.5],
        "fair_A": [0.4, 0.6, 0.5],
        "fair_I": [0.3, 0.7, 0.5],
        "fair_R": [0.3, 0.7, 0.5],
        "status": ["fallback"] * 3,
    })
    run_data = pd.DataFrame({
        "did": [1, 2, 3],
        "first_run_timestamp": [pd.Timestamp("2019-01-01"), pd.Timestamp("2020-01-01"), None],
        "run_count": [5, 15, 0],
    })
    metadata = pd.DataFrame({
        "did": [1, 2, 3],
        "upload_date": pd.to_datetime(["2018-01-01", "2018-06-01", "2019-01-01"]),
        "task_type": ["supervised_classification"] * 3,
        "NumberOfInstances": [1000.0, 2000.0, 500.0],
    })
    cohort = build_merged_cohort(he1, run_data, metadata, min_run_count=10)
    assert len(cohort) == 1  # only did=2 has run_count>=10
    assert cohort.iloc[0]["did"] == 2


def test_fetch_run_timestamps_cache_hit(tmp_path):
    cache_dir = str(tmp_path / "cache")
    os.makedirs(cache_dir)
    rec = {"did": 42, "first_run_timestamp": "2020-01-01 00:00:00", "run_count": 10}
    with open(os.path.join(cache_dir, "42_runs.json"), "w") as f:
        json.dump(rec, f)
    result = fetch_run_timestamps([42], cache_dir)
    assert len(result) == 1
    assert result.iloc[0]["did"] == 42
    assert result.iloc[0]["run_count"] == 10
