"""Tests for data.py — data assembly functions."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add code/ to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import N_COMMON_MIN, ROBUSTNESS_SCORES


def make_test_df(n=12, seed=42):
    """Create synthetic test DataFrame matching master DataFrame schema."""
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "model_name":    [f"model_{i}" for i in range(n)],
        "bbq_disambig":  rng.uniform(0.4, 0.9, n),
        "bbq_ambig":     rng.uniform(0.3, 0.8, n),
        "mmlu":          rng.uniform(0.3, 0.9, n),
        "winogrande":    rng.uniform(0.4, 0.9, n),
        "glue_score":    rng.uniform(0.4, 0.85, n),
        "advglue_score": rng.uniform(0.2, 0.6, n),
        "anli_r1_score": rng.uniform(0.3, 0.7, n),
        "anli_r3_score": rng.uniform(0.2, 0.6, n),
    })


class TestBuildRobustnessScores:
    def test_returns_dataframe(self):
        from data import build_robustness_scores
        df = build_robustness_scores()
        assert isinstance(df, pd.DataFrame)

    def test_has_required_columns(self):
        from data import build_robustness_scores
        df = build_robustness_scores()
        for col in ["model_name", "glue_score", "advglue_score", "anli_r1_score", "anli_r3_score"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_no_none_scores(self):
        from data import build_robustness_scores
        df = build_robustness_scores()
        assert not df.isnull().any().any(), "Should have no NaN values"

    def test_scores_in_valid_range(self):
        from data import build_robustness_scores
        df = build_robustness_scores()
        for col in ["glue_score", "advglue_score", "anli_r1_score", "anli_r3_score"]:
            assert (df[col] >= 0).all() and (df[col] <= 1).all(), f"{col} out of [0,1]"

    def test_at_least_n_common_min_models(self):
        from data import build_robustness_scores
        df = build_robustness_scores()
        assert len(df) >= N_COMMON_MIN, f"Need >= {N_COMMON_MIN} models, got {len(df)}"


class TestVerifyPreconditions:
    def test_passes_valid_df(self):
        from data import verify_preconditions
        df = make_test_df(n=12)
        n = verify_preconditions(df)
        assert n == 12

    def test_fails_if_n_too_small(self):
        from data import verify_preconditions
        df = make_test_df(n=5)
        with pytest.raises(AssertionError, match="N=5"):
            verify_preconditions(df)

    def test_fails_if_column_missing(self):
        from data import verify_preconditions
        df = make_test_df(n=12)
        df = df.drop(columns=["advglue_score"])
        with pytest.raises(AssertionError, match="Missing columns"):
            verify_preconditions(df)
