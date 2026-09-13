"""test_evaluate.py — Unit tests for GateEvaluator."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from evaluate import GateEvaluator, evaluate_experiment
import config


@pytest.fixture
def evaluator():
    return GateEvaluator()


@pytest.fixture
def passing_family_df():
    return pd.DataFrame({
        "family": ["LLaMA", "Mistral", "Qwen"],
        "rho": [0.55, 0.48, 0.41],
        "p_value": [0.02, 0.04, 0.03],
        "n": [12, 10, 8],
        "sign_consistent": [True, True, True],
    })


@pytest.fixture
def failing_family_df():
    return pd.DataFrame({
        "family": ["LLaMA", "Mistral", "Qwen"],
        "rho": [-0.1, 0.05, -0.2],
        "p_value": [0.6, 0.8, 0.5],
        "n": [12, 10, 8],
        "sign_consistent": [False, True, False],
    })


class TestGateEvaluator:
    def test_gate_pass(self, evaluator, passing_family_df):
        result = evaluator.evaluate_gate(rho=0.52, p_value=0.003, family_results=passing_family_df)
        assert result["gate"] == "PASS"
        assert result["conditions_met"] == 3

    def test_gate_fail(self, evaluator, failing_family_df):
        result = evaluator.evaluate_gate(rho=0.05, p_value=0.7, family_results=failing_family_df)
        assert result["gate"] == "FAIL"
        assert result["conditions_met"] == 0

    def test_gate_partial(self, evaluator, passing_family_df):
        # rho passes, p fails
        result = evaluator.evaluate_gate(rho=0.45, p_value=0.08, family_results=passing_family_df)
        assert result["gate"] == "PARTIAL"
        assert 1 <= result["conditions_met"] <= 2

    def test_baseline_corr(self, evaluator, mock_model_df):
        result = evaluator.baseline_corr(mock_model_df)
        assert "rho" in result
        assert "p_val" in result
        assert -1.0 <= result["rho"] <= 1.0

    def test_check_vif_returns_dict(self, evaluator, mock_model_df):
        vif = evaluator.check_vif(mock_model_df)
        assert "RI" in vif
        assert "PC1" in vif
        assert "mean_confidence" in vif
        for k, v in vif.items():
            assert v >= 1.0, f"VIF for {k} should be >=1"

    def test_vif_below_threshold(self, evaluator, mock_model_df):
        vif = evaluator.check_vif(mock_model_df)
        for k, v in vif.items():
            assert v < config.VIF_THRESHOLD, f"VIF for {k}={v:.2f} exceeds threshold"

    def test_cooks_distance(self, evaluator, mock_model_df):
        result = evaluator.cooks_distance(mock_model_df)
        assert "flagged_models" in result
        assert "d_values" in result
        assert len(result["d_values"]) == 30

    def test_fisher_z_test(self, evaluator, mock_model_df):
        result = evaluator.fisher_z_test(mock_model_df)
        assert "z_stat" in result
        assert "p_val" in result

    def test_run_all_secondary(self, evaluator, mock_model_df, passing_family_df):
        result = evaluator.run_all_secondary(mock_model_df, passing_family_df)
        assert "baseline_corr" in result
        assert "vif" in result
        assert "cooks" in result
        assert "fisher_z" in result

    def test_evaluate_experiment_top_level(self, mock_model_df, mock_partial_corr_results):
        gate, secondary = evaluate_experiment(mock_model_df, mock_partial_corr_results)
        assert gate["gate"] in ("PASS", "PARTIAL", "FAIL")
        assert "baseline_corr" in secondary
