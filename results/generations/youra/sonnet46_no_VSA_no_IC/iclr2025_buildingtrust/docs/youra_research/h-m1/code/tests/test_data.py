"""Tests for H-M1 data module."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from data import build_score_dataframe, verify_n_common


def test_build_score_dataframe():
    df = build_score_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 10
    assert set(["model_name", "bbq_disambig", "bbq_ambig", "mmlu"]).issubset(df.columns)
    assert df["bbq_disambig"].notna().all()
    assert df["bbq_ambig"].notna().all()
    assert df["mmlu"].notna().all()
    # all scores in [0, 1]
    assert (df["bbq_disambig"].between(0, 1)).all()
    assert (df["bbq_ambig"].between(0, 1)).all()
    assert (df["mmlu"].between(0, 1)).all()


def test_verify_n_common():
    df = build_score_dataframe()
    n = verify_n_common(df)
    assert n == len(df)
    assert n >= 10


def test_verify_n_common_fails_small():
    small_df = pd.DataFrame({"bbq_disambig": [0.5] * 5, "bbq_ambig": [0.5] * 5, "mmlu": [0.5] * 5})
    with pytest.raises(AssertionError):
        verify_n_common(small_df, min_n=10)
