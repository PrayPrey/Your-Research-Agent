import pytest
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import analyzers
import config

TEST_BOOT_N = config.TEST_BOOTSTRAP_N


def test_bca_bootstrap_partial_returns_tuple(synthetic_score_matrix):
    ci_lo, ci_hi = analyzers._bca_bootstrap_partial(
        synthetic_score_matrix, "ECE", "AdvGLUE_drop", "MMLU_acc",
        n_boot=TEST_BOOT_N, seed=42,
    )
    assert isinstance(ci_lo, float)
    assert isinstance(ci_hi, float)
    assert ci_lo <= ci_hi


def test_compute_partial_rho_advglue_keys(synthetic_score_matrix):
    result = analyzers.compute_partial_rho_advglue(
        synthetic_score_matrix, n_boot=TEST_BOOT_N, seed=42
    )
    expected_keys = {
        "rho_partial_advglue", "bca_ci_low", "bca_ci_high",
        "ci_excludes_zero", "passes_threshold",
        "rho_partial_anli", "anli_bca_ci_low", "anli_bca_ci_high",
    }
    assert expected_keys == set(result.keys())


def test_compute_partial_rho_advglue_ci_excludes_zero_logic(synthetic_score_matrix):
    result = analyzers.compute_partial_rho_advglue(
        synthetic_score_matrix, n_boot=TEST_BOOT_N, seed=42
    )
    # Verify ci_excludes_zero logic: True iff ci_lo > 0 OR ci_hi < 0
    ci_lo = result["bca_ci_low"]
    ci_hi = result["bca_ci_high"]
    expected = (ci_lo > 0 or ci_hi < 0)
    assert result["ci_excludes_zero"] == expected


def test_run_loo_logistic_shape(synthetic_score_matrix):
    X = synthetic_score_matrix[config.COMPOSITE_COLS].values
    y = (synthetic_score_matrix["AdvGLUE_drop"] >=
         synthetic_score_matrix["AdvGLUE_drop"].quantile(0.75)).astype(int).values
    y_proba = analyzers._run_loo_logistic(X, y, seed=42)
    assert y_proba.shape == (len(synthetic_score_matrix),)
    assert np.all((y_proba >= 0) & (y_proba <= 1))


def test_compute_loo_auc_keys(synthetic_score_matrix):
    result = analyzers.compute_loo_auc(
        synthetic_score_matrix, config.COMPOSITE_COLS, config.TARGET_COL, seed=42
    )
    assert "auc" in result
    assert "y_proba" in result
    assert "y_true" in result
    assert "feature_cols" in result
    assert 0.0 <= result["auc"] <= 1.0


def test_compute_loo_auc_single_class_raises(synthetic_score_matrix):
    df = synthetic_score_matrix.copy()
    df[config.TARGET_COL] = 0  # all same class
    with pytest.raises(ValueError, match="fewer than 2 classes"):
        analyzers.compute_loo_auc(df, config.COMPOSITE_COLS, config.TARGET_COL, seed=42)


def test_compute_delta_auc_bootstrap_keys(synthetic_score_matrix):
    result = analyzers.compute_delta_auc_bootstrap(
        synthetic_score_matrix,
        config.COMPOSITE_COLS, config.BASELINE_COLS,
        config.TARGET_COL, n_boot=TEST_BOOT_N, seed=42,
    )
    expected_keys = {
        "auc_composite", "auc_baseline", "delta_auc",
        "delta_auc_ci", "ci_excludes_zero",
        "passes_delta_threshold", "passes_auc_threshold",
    }
    assert expected_keys == set(result.keys())
    assert len(result["delta_auc_ci"]) == 2
    assert result["delta_auc_ci"][0] <= result["delta_auc_ci"][1]


def test_evaluate_gate_pass(synthetic_score_matrix):
    delta_pass = {
        "passes_auc_threshold": True,
        "passes_delta_threshold": True,
    }
    assert analyzers.evaluate_gate({}, delta_pass) is True


def test_evaluate_gate_fail(synthetic_score_matrix):
    delta_fail = {
        "passes_auc_threshold": False,
        "passes_delta_threshold": True,
    }
    assert analyzers.evaluate_gate({}, delta_fail) is False
