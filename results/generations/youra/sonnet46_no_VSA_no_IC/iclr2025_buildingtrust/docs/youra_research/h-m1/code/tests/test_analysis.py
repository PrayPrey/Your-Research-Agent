"""Tests for H-M1 analysis module."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis import compute_raw_spearman, compute_partial_spearman, evaluate_gate, run_full_analysis


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "model_name":   [f"M{i}" for i in range(14)],
        "bbq_disambig": [0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.55, 0.62, 0.68, 0.73, 0.78],
        "bbq_ambig":    [0.82, 0.77, 0.72, 0.67, 0.62, 0.57, 0.52, 0.47, 0.42, 0.50, 0.58, 0.64, 0.70, 0.75],
        "mmlu":         [0.86, 0.70, 0.64, 0.54, 0.46, 0.28, 0.56, 0.42, 0.46, 0.51, 0.54, 0.63, 0.68, 0.78],
        "winogrande":   [0.87, 0.78, 0.78, 0.70, 0.66, 0.66, 0.82, 0.62, 0.67, 0.70, 0.74, 0.75, 0.72, 0.74],
    })


def test_compute_raw_spearman(sample_df):
    result = compute_raw_spearman(sample_df)
    assert "raw_rho" in result
    assert "raw_p" in result
    assert result["n"] == 14
    assert -1 <= result["raw_rho"] <= 1
    assert 0 <= result["raw_p"] <= 1


def test_compute_partial_spearman_mmlu(sample_df):
    result = compute_partial_spearman(sample_df, covar="mmlu")
    assert "partial_rho" in result
    assert "p_value" in result
    assert "ci95" in result
    assert result["n"] == 14
    assert -1 <= result["partial_rho"] <= 1
    assert 0 <= result["p_value"] <= 1
    assert len(result["ci95"]) == 2


def test_compute_partial_spearman_winogrande(sample_df):
    result = compute_partial_spearman(sample_df, covar="winogrande")
    assert result["covar"] == "winogrande"
    assert -1 <= result["partial_rho"] <= 1


def test_evaluate_gate():
    assert evaluate_gate(0.5, 0.03) is True
    assert evaluate_gate(0.3, 0.03) is False
    assert evaluate_gate(0.5, 0.06) is False
    assert evaluate_gate(0.4, 0.05) is False  # strictly greater


def test_compute_partial_spearman_missing_covar(sample_df):
    with pytest.raises(AssertionError):
        compute_partial_spearman(sample_df, covar="nonexistent")


def test_run_full_analysis(sample_df):
    results = run_full_analysis(sample_df)
    assert "raw" in results
    assert "primary" in results
    assert "gate_pass" in results
    assert isinstance(results["gate_pass"], bool)
    assert "mmlu_explains_variance" in results
