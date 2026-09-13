"""Tests for src/score_fuji.py (task-006 through task-009)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from src.score_fuji import (
    _parse_fuji_response,
    _load_cache,
    _save_cache,
    fuji_fallback_proxy,
)


def _make_cohort(n=5):
    return pd.DataFrame({
        "did": list(range(1, n + 1)),
        "landing_page_url": [f"https://www.openml.org/d/{i}" for i in range(1, n + 1)],
        "NumberOfInstances": [100.0 * i for i in range(1, n + 1)],
        "NumberOfFeatures": [10.0 * i for i in range(1, n + 1)],
        "MajorityClassPercentage": [50.0] * n,
    })


def test_parse_fuji_response_ok():
    resp = {
        "results": [
            {"metric_identifier": f"FsF-F1-{i:02d}D",
             "score": {"earned": 1, "total": 1}}
            for i in range(17)
        ]
    }
    result = _parse_fuji_response(42, resp)
    assert result["did"] == 42
    assert result["status"] == "ok"
    assert 0.0 <= result["fair_aggregate"] <= 1.0
    assert isinstance(result["sub_criteria"], list)


def test_parse_fuji_response_empty():
    result = _parse_fuji_response(1, {"results": []})
    assert result["status"] == "parse_error"
    assert result["fair_aggregate"] == 0.0


def test_cache_roundtrip(tmp_path):
    cache_dir = str(tmp_path)
    data = {"did": 1, "fair_aggregate": 0.5, "status": "ok"}
    _save_cache(cache_dir, 1, data)
    loaded = _load_cache(cache_dir, 1)
    assert loaded is not None
    assert loaded["fair_aggregate"] == 0.5


def test_cache_miss(tmp_path):
    result = _load_cache(str(tmp_path), 9999)
    assert result is None


def test_fuji_fallback_proxy_schema():
    cohort = _make_cohort(10)
    result = fuji_fallback_proxy(cohort)
    assert isinstance(result, pd.DataFrame)
    required_cols = ["did", "fair_aggregate", "fair_F", "fair_A",
                     "fair_I", "fair_R", "sub_criteria", "status"]
    for col in required_cols:
        assert col in result.columns, f"Missing column: {col}"
    assert (result["status"] == "fallback").all()
    assert result["fair_aggregate"].between(0, 1).all()


def test_fuji_fallback_proxy_values_in_range():
    cohort = _make_cohort(20)
    result = fuji_fallback_proxy(cohort)
    assert (result["fair_aggregate"] >= 0.0).all()
    assert (result["fair_aggregate"] <= 1.0).all()


def test_fuji_fallback_proxy_graceful_missing_columns():
    cohort = pd.DataFrame({"did": [1, 2], "landing_page_url": ["u1", "u2"]})
    result = fuji_fallback_proxy(cohort)
    assert len(result) == 2
    assert (result["status"] == "fallback").all()
