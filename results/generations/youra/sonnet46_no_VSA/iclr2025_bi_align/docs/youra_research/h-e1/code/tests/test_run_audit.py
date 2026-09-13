"""Tests for H-E1 run_audit.py — spec compliance per 03_logic.md."""

import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from run_audit import (
    exact_join,
    fuzzy_join,
    sensitivity_sweep,
    verify_mechanism_activated,
)


@pytest.fixture
def df_llm():
    return pd.DataFrame({
        "model_name": [
            "meta-llama/Llama-2-7b-hf",
            "mistralai/Mistral-7B-v0.1",
            "tiiuae/falcon-7b",
            "EleutherAI/gpt-neox-20b",
            "bigscience/bloom",
        ],
        "TruthfulQA_MC2": [40.0, 42.0, 35.0, 38.0, 39.0],
        "MMLU": [44.0, 60.0, 26.0, 33.0, 27.0],
    })


@pytest.fixture
def df_bbq():
    return pd.DataFrame({
        "model_name": [
            "meta-llama/Llama-2-7B-hf",
            "mistralai/Mistral-7B-v0.1",
            "tiiuae/falcon-7b",
            "EleutherAI/gpt-neox-20b",
        ],
        "bbq_accuracy": [0.55, 0.60, 0.50, 0.48],
    })


class TestExactJoin:
    def test_inner_join_on_model_name(self, df_llm, df_bbq):
        result = exact_join(df_llm, df_bbq)
        # Exact match: "mistralai/Mistral-7B-v0.1", "tiiuae/falcon-7b", "EleutherAI/gpt-neox-20b"
        assert "TruthfulQA_MC2" in result.columns
        assert "bbq_accuracy" in result.columns
        assert "MMLU" in result.columns

    def test_returns_only_complete_rows(self, df_llm, df_bbq):
        result = exact_join(df_llm, df_bbq)
        assert result[["TruthfulQA_MC2", "bbq_accuracy", "MMLU"]].notna().all().all()

    def test_excludes_non_matching(self, df_llm, df_bbq):
        result = exact_join(df_llm, df_bbq)
        # bloom has no BBQ entry -> excluded
        assert "bigscience/bloom" not in result["model_name"].values


class TestFuzzyJoin:
    def test_returns_three_tuple(self, df_llm, df_bbq):
        out = fuzzy_join(df_llm, df_bbq, threshold=75)
        assert len(out) == 3

    def test_df_complete_has_required_columns(self, df_llm, df_bbq):
        df_complete, _, _ = fuzzy_join(df_llm, df_bbq, threshold=75)
        for col in ["model_name", "TruthfulQA_MC2", "MMLU", "bbq_accuracy"]:
            assert col in df_complete.columns

    def test_fuzzy_match_case_variation(self, df_llm, df_bbq):
        # "meta-llama/Llama-2-7B-hf" (BBQ) vs "meta-llama/Llama-2-7b-hf" (LLM) differ by case
        df_complete, match_rate, _ = fuzzy_join(df_llm, df_bbq, threshold=75)
        assert match_rate > 0.0

    def test_df_matches_columns(self, df_llm, df_bbq):
        _, _, df_matches = fuzzy_join(df_llm, df_bbq, threshold=75)
        if not df_matches.empty:
            assert "bbq_name" in df_matches.columns
            assert "llm_name" in df_matches.columns
            assert "score" in df_matches.columns

    def test_empty_bbq_returns_empty(self, df_llm):
        df_bbq_empty = pd.DataFrame(columns=["model_name", "bbq_accuracy"])
        df_c, mr, df_m = fuzzy_join(df_llm, df_bbq_empty, threshold=75)
        assert len(df_c) == 0
        assert mr == 0.0

    def test_complete_rows_no_nulls(self, df_llm, df_bbq):
        df_complete, _, _ = fuzzy_join(df_llm, df_bbq, threshold=75)
        if not df_complete.empty:
            assert df_complete[["TruthfulQA_MC2", "bbq_accuracy", "MMLU"]].notna().all().all()


class TestSensitivitySweep:
    def test_returns_dataframe_with_expected_columns(self, df_llm, df_bbq):
        result = sensitivity_sweep(df_llm, df_bbq, thresholds=[70, 75, 80])
        assert isinstance(result, pd.DataFrame)
        for col in ["threshold", "N_complete", "match_rate"]:
            assert col in result.columns

    def test_row_count_matches_thresholds(self, df_llm, df_bbq):
        thresholds = [65, 70, 75, 80]
        result = sensitivity_sweep(df_llm, df_bbq, thresholds=thresholds)
        assert len(result) == len(thresholds)


class TestVerifyMechanismActivated:
    def test_all_pass(self, df_llm, df_bbq):
        df_complete = pd.DataFrame({"model_name": ["a"] * 35})
        all_pass, indicators = verify_mechanism_activated(df_complete, 35, 0.70, 10)
        assert all_pass is True
        assert indicators["gate_passed"] is True
        assert indicators["match_rate_acceptable"] is True
        assert indicators["fuzzy_beats_exact"] is True

    def test_gate_fail_n_below_30(self, df_llm, df_bbq):
        df_complete = pd.DataFrame({"model_name": ["a"] * 20})
        all_pass, indicators = verify_mechanism_activated(df_complete, 20, 0.70, 10)
        assert all_pass is False
        assert indicators["gate_passed"] is False

    def test_returns_five_indicator_keys(self):
        df_c = pd.DataFrame({"model_name": ["a"] * 5})
        _, indicators = verify_mechanism_activated(df_c, 5, 0.60, 2)
        expected_keys = {
            "url_check_passed", "join_produced_rows",
            "fuzzy_beats_exact", "gate_passed", "match_rate_acceptable"
        }
        assert set(indicators.keys()) == expected_keys
