import sys
import os
import pandas as pd
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_loader import load_score_matrix
from analyzers import (
    _bca_bootstrap_spearman,
    _bca_bootstrap_partial,
    compute_internal_consistency,
    compute_partial_corr_bca,
    compute_confound_magnitude,
    compute_discriminant_validity,
    compute_decoding_invariance,
    evaluate_gate,
)
import config

SCORE_MATRIX_PATH = config.SCORE_MATRIX_PATH


@pytest.fixture(scope="module")
def df():
    return load_score_matrix(SCORE_MATRIX_PATH)


def test_bca_spearman_deterministic(df):
    ci1 = _bca_bootstrap_spearman(df, "ECE", "Brier", 500, seed=42)
    ci2 = _bca_bootstrap_spearman(df, "ECE", "Brier", 500, seed=42)
    assert ci1 == ci2


def test_bca_partial_deterministic(df):
    ci1 = _bca_bootstrap_partial(df, "ECE", "TruthfulQA_pct", "MMLU_acc", 500, seed=42)
    ci2 = _bca_bootstrap_partial(df, "ECE", "TruthfulQA_pct", "MMLU_acc", 500, seed=42)
    assert ci1 == ci2


def test_bca_direction(df):
    ci = _bca_bootstrap_spearman(df, "ECE", "TruthfulQA_pct", 500, seed=42)
    assert ci[0] < 0 and ci[1] < 0, f"Expected negative CI for ECE-TruthfulQA, got {ci}"


def test_internal_consistency_expected_range(df):
    result = compute_internal_consistency(df, "ECE", "Brier", 500, seed=42)
    assert result["rho"] >= 0.30, f"Expected rho >= 0.30, got {result['rho']}"


def test_internal_consistency_ci_bounds(df):
    result = compute_internal_consistency(df, "ECE", "Brier", 500, seed=42)
    assert result["bca_ci_low"] < result["rho"] < result["bca_ci_high"]


def test_internal_consistency_passes_threshold(df):
    result = compute_internal_consistency(df, "ECE", "Brier", 500, seed=42)
    assert result["passes_threshold"] == (result["rho"] >= config.INTERNAL_THRESHOLD)


def test_partial_corr_gate_pass(df):
    result = compute_partial_corr_bca(df, "ECE", "TruthfulQA_pct", "MMLU_acc", 500, seed=42)
    assert abs(result["rho_partial"]) >= 0.40, f"Expected |partial_rho| >= 0.40, got {result['rho_partial']}"


def test_ci_excludes_zero(df):
    result = compute_partial_corr_bca(df, "ECE", "TruthfulQA_pct", "MMLU_acc", 500, seed=42)
    assert result["ci_excludes_zero"], "BCa CI should exclude zero for primary gate"


def test_confound_magnitude(df):
    from scipy.stats import spearmanr
    raw_rho = float(spearmanr(df["ECE"], df["TruthfulQA_pct"]).statistic)
    partial = compute_partial_corr_bca(df, "ECE", "TruthfulQA_pct", "MMLU_acc", 500, seed=42)
    result = compute_confound_magnitude(raw_rho, partial["rho_partial"])
    assert 0.0 < result["survival_fraction"] <= 1.0, f"survival_fraction out of range: {result['survival_fraction']}"


def test_discriminant_validity_low(df):
    result = compute_discriminant_validity(df, "ECE", "HumanEval_pass1", "MMLU_acc", 500, seed=42)
    assert abs(result["rho_partial"]) < 0.20, f"Expected |partial_rho| < 0.20, got {result['rho_partial']}"


def test_decoding_invariance_skipped():
    df_empty = pd.DataFrame()
    df_greedy = pd.DataFrame({"ECE": [0.1], "TruthfulQA_pct": [0.5], "MMLU_acc": [0.6]})
    result = compute_decoding_invariance(df_greedy, df_empty, "ECE", "TruthfulQA_pct", "MMLU_acc", 100, seed=42)
    assert result["skipped"] is True


def test_decoding_invariance_threshold():
    result = compute_decoding_invariance(pd.DataFrame(), pd.DataFrame(), "ECE", "TruthfulQA_pct", "MMLU_acc", 100, seed=42)
    assert result["passes_threshold"] == False
    assert result["skipped"] == True


def test_evaluate_gate_pass():
    partial_result = {"rho_partial": -0.55, "ci_excludes_zero": True, "passes_threshold": True}
    assert evaluate_gate(partial_result, 0.40) is True


def test_evaluate_gate_fail_magnitude():
    partial_result = {"rho_partial": -0.30, "ci_excludes_zero": True, "passes_threshold": False}
    assert evaluate_gate(partial_result, 0.40) is False


def test_evaluate_gate_fail_ci():
    partial_result = {"rho_partial": -0.55, "ci_excludes_zero": False, "passes_threshold": False}
    assert evaluate_gate(partial_result, 0.40) is False
