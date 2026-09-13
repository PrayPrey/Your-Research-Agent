"""Tests for src/collect_openml.py (task-005)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from src.collect_openml import deduplicate_cohort, build_cohort


def test_deduplicate_cohort_removes_duplicates():
    df = pd.DataFrame({
        "name": ["ds1", "ds1", "ds2"],
        "version": [1, 2, 1],
        "did": [1, 2, 3],
    })
    result = deduplicate_cohort(df)
    assert len(result) == 2
    assert result[result["name"] == "ds1"].iloc[0]["version"] == 2


def test_deduplicate_cohort_empty():
    df = pd.DataFrame(columns=["name", "version", "did"])
    result = deduplicate_cohort(df)
    assert len(result) == 0


def test_build_cohort_returns_dataframe():
    """Smoke test: build_cohort returns a non-empty DataFrame with expected columns."""
    import types
    cfg = types.SimpleNamespace(
        OPENML_UPLOAD_DATE_MIN="2018-01-01",
        OPENML_TASK_TYPES=["supervised_classification", "supervised_regression"],
        max_datasets=50,
    )
    df = build_cohort(cfg)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "did" in df.columns
    assert "landing_page_url" in df.columns
    assert df["landing_page_url"].str.startswith("https://www.openml.org/d/").all()


def test_build_cohort_no_duplicate_names():
    import types
    cfg = types.SimpleNamespace(
        OPENML_UPLOAD_DATE_MIN="2018-01-01",
        OPENML_TASK_TYPES=["supervised_classification", "supervised_regression"],
        max_datasets=100,
    )
    df = build_cohort(cfg)
    if "name" in df.columns:
        assert df["name"].duplicated().sum() == 0
