"""test_partial_corr.py — Unit tests for PartialCorrAnalyzer."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from partial_corr import PartialCorrAnalyzer, run_partial_correlation_analysis
import config


class TestPartialCorrAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return PartialCorrAnalyzer(n_bootstrap=100, seed=config.TEST_SEED)

    def test_full_partial_corr_returns_dict(self, analyzer, mock_model_df):
        result = analyzer.full_partial_corr(mock_model_df)
        assert "rho" in result
        assert "p_value" in result
        assert "n" in result
        assert result["n"] == 30
        assert -1.0 <= result["rho"] <= 1.0

    def test_full_partial_corr_ci(self, analyzer, mock_model_df):
        result = analyzer.full_partial_corr(mock_model_df)
        assert result["ci_low"] <= result["ci_high"]

    def test_family_partial_corr_shape(self, analyzer, mock_model_df):
        family_df = analyzer.family_partial_corr(mock_model_df)
        # Should have ≥1 family (LLaMA=12, Mistral=10, Qwen=8 — all ≥5)
        assert len(family_df) >= 1
        assert "family" in family_df.columns
        assert "rho" in family_df.columns
        assert "sign_consistent" in family_df.columns

    def test_family_partial_corr_skips_small_families(self, analyzer, mock_model_df):
        # Filter to only 3 LLaMA models — should be skipped
        tiny = mock_model_df[mock_model_df["model_family"] == "LLaMA"].head(3)
        tiny_df = pd.concat([tiny, mock_model_df[mock_model_df["model_family"] != "LLaMA"]])
        family_df = analyzer.family_partial_corr(tiny_df)
        llama_rows = family_df[family_df["family"] == "LLaMA"]
        assert len(llama_rows) == 0  # skipped due to n<5

    def test_holm_correction_output_shape(self, analyzer):
        p_vals = np.array([0.01, 0.04, 0.08])
        reject, p_corrected = analyzer.holm_correction(p_vals)
        assert len(reject) == 3
        assert len(p_corrected) == 3

    def test_run_all_structure(self, analyzer, mock_model_df):
        results = analyzer.run_all(mock_model_df)
        assert "full" in results
        assert "family_df" in results
        assert "n_consistent_positive" in results
        assert isinstance(results["n_consistent_positive"], int)

    def test_top_level_function(self, mock_model_df):
        results = run_partial_correlation_analysis(mock_model_df)
        assert "full" in results
        assert "rho" in results["full"]
