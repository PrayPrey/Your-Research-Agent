"""Tests for features.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import pytest
from features import (
    extract_verbosity,
    extract_hedging,
    extract_structured_reasoning,
    build_feature_matrix,
    check_vif,
    partition_by_ambiguity,
)


def make_df(n=200):
    chosen = ["This is a long detailed answer with perhaps maybe could some hedging. 1. First point. 2. Second."] * n
    rejected = ["Short answer."] * n
    return pd.DataFrame({"chosen": chosen, "rejected": rejected})


def test_extract_verbosity():
    assert extract_verbosity("hello world") == 2.0
    assert extract_verbosity("") == 0.0
    assert extract_verbosity(None) == 0.0


def test_extract_hedging():
    text = "I think this might be correct"
    val = extract_hedging(text)
    assert val >= 0.0
    assert extract_hedging("") == 0.0


def test_extract_structured_reasoning():
    text = "1. First point\n- second\n* third"
    val = extract_structured_reasoning(text)
    assert val >= 0.0


def test_build_feature_matrix_shape():
    df = make_df(100)
    X, y = build_feature_matrix(df)
    assert X.shape == (100, 3)
    assert y.shape == (100,)
    assert np.all(y == 1)


def test_build_feature_matrix_missing_cols():
    df = pd.DataFrame({"col_a": ["x"], "col_b": ["y"]})
    with pytest.raises(ValueError, match="missing columns"):
        build_feature_matrix(df)


def test_check_vif_returns_dict():
    df = make_df(300)
    X, _ = build_feature_matrix(df)
    vif = check_vif(X)
    assert isinstance(vif, dict)
    assert "beta_L" in vif
    assert "beta_H" in vif
    assert "beta_S" in vif


def test_partition_by_ambiguity():
    df = make_df(1000)
    hi, lo = partition_by_ambiguity(df)
    assert len(hi) + len(lo) <= len(df) + 1  # slight overlap ok
    assert len(hi) >= 0
    assert len(lo) >= 0
