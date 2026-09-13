import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
import pandas as pd
import analysis
from config import INDICATORS, COVARIATE, GATE_PAIRS, GATE_THRESHOLD


def _make_df(n=30, seed=42):
    rng = np.random.default_rng(seed)
    # Create correlated data so partial corr is meaningful
    base = rng.normal(0, 1, n)
    df = pd.DataFrame({
        "ECE": np.abs(base + rng.normal(0, 0.3, n)),
        "Brier": np.abs(base + rng.normal(0, 0.3, n)),
        "TruthfulQA_pct": 50 - 10 * base + rng.normal(0, 5, n),
        "AdvGLUE_drop": 0.1 * base + rng.normal(0, 0.05, n),
        "ANLI_drop": 0.05 * base + rng.normal(0, 0.02, n),
        "MMLU_acc": 0.6 + 0.05 * rng.normal(0, 1, n),
    })
    df["TruthfulQA_pct"] = df["TruthfulQA_pct"].clip(0, 100)
    df["MMLU_acc"] = df["MMLU_acc"].clip(0.3, 0.9)
    return df


def test_compute_partial_corr_matrix_shape():
    df = _make_df()
    result = analysis.compute_partial_corr_matrix(df, INDICATORS, COVARIATE)
    assert len(result) == 10  # C(5,2) = 10 pairs
    for col in ["x", "y", "rho", "ci_low", "ci_high", "p_value"]:
        assert col in result.columns


def test_compute_partial_corr_matrix_rho_range():
    df = _make_df()
    result = analysis.compute_partial_corr_matrix(df, INDICATORS, COVARIATE)
    valid = result["rho"].dropna()
    assert (valid >= -1.0).all() and (valid <= 1.0).all()


def test_bca_bootstrap_ci_returns_tuple():
    df = _make_df()
    lo, hi = analysis.bca_bootstrap_ci(df, "ECE", "TruthfulQA_pct", COVARIATE, n_boot=100)
    assert isinstance(lo, float)
    assert isinstance(hi, float)
    assert lo <= hi


def test_run_factor_analysis_shape():
    df = _make_df()
    fa, loadings, var_exp, kmo = analysis.run_factor_analysis(df, INDICATORS)
    assert loadings.shape[0] == len(INDICATORS)
    assert isinstance(var_exp, float)
    assert isinstance(kmo, float)


def test_compute_tucker_congruence_identical():
    v = np.array([0.8, 0.7, 0.6, 0.5, 0.4])
    cong = analysis.compute_tucker_congruence(v.reshape(-1, 1), v.reshape(-1, 1))
    assert abs(cong - 1.0) < 1e-6


def test_compute_tucker_congruence_range():
    rng = np.random.default_rng(0)
    a = rng.normal(0, 1, (5, 1))
    b = rng.normal(0, 1, (5, 1))
    c = analysis.compute_tucker_congruence(a, b)
    assert -1.0 <= c <= 1.0


def test_run_loo_logistic_returns_keys():
    df = _make_df()
    result = analysis.run_loo_logistic(df, ["ECE", "TruthfulQA_pct", "Brier"])
    assert "auc" in result
    assert "auc_mmlu_only" in result


def test_evaluate_gates_structure():
    df = _make_df()
    corr_df = analysis.compute_partial_corr_matrix(df, INDICATORS, COVARIATE)
    gate = analysis.evaluate_gates(corr_df, GATE_PAIRS, GATE_THRESHOLD)
    assert "PASS" in gate
    assert "results" in gate
    assert len(gate["results"]) == len(GATE_PAIRS)
    assert isinstance(gate["PASS"], bool)
    for r in gate["results"]:
        assert "pair" in r
        assert "rho" in r
        assert "ci" in r
        assert "passes" in r
