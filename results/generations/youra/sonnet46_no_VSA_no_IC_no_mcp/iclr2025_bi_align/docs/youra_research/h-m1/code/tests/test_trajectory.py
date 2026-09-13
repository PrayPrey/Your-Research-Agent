"""Spec compliance tests for src/analysis/trajectory.py."""
import numpy as np
import pandas as pd
import pytest

from src.analysis.trajectory import (
    run_rm_monotonicity_test,
    detect_peak_reversal,
    compute_divergence,
    run_analysis,
)

# Canonical data matching coste_digitized.csv
KL = np.array([0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
RM = np.array([0.12, 0.48, 0.81, 1.24, 1.55, 1.78, 1.92, 2.01, 2.06, 2.08])
GOLD = np.array([0.52, 0.58, 0.61, 0.63, 0.61, 0.57, 0.53, 0.48, 0.43, 0.38])


class TestMonotonicity:
    def test_returns_required_keys(self):
        r = run_rm_monotonicity_test(KL, RM)
        for key in ("rho_rm_kl", "p_rho", "monotone_pass", "reason"):
            assert key in r

    def test_coste_passes(self):
        r = run_rm_monotonicity_test(KL, RM)
        assert r["rho_rm_kl"] > 0.8
        assert r["p_rho"] < 0.05
        assert r["monotone_pass"] == True

    def test_insufficient_data(self):
        r = run_rm_monotonicity_test(KL[:2], RM[:2])
        assert r["monotone_pass"] is False
        assert np.isnan(r["rho_rm_kl"])


class TestPeakReversal:
    def test_returns_required_keys(self):
        r = detect_peak_reversal(KL, GOLD)
        for key in ("peak_idx", "peak_kl", "reversal_confirmed", "peak_kl_valid", "reason"):
            assert key in r

    def test_coste_reversal_confirmed(self):
        r = detect_peak_reversal(KL, GOLD)
        assert r["reversal_confirmed"] is True
        assert r["peak_kl_valid"] is True
        assert 1.0 <= r["peak_kl"] <= 9.0

    def test_no_reversal_monotone_increasing(self):
        gold_mono = np.linspace(0.5, 0.9, 10)
        r = detect_peak_reversal(KL, gold_mono)
        assert r["reversal_confirmed"] is False


class TestDivergence:
    def test_returns_required_keys(self):
        r = compute_divergence(RM, GOLD)
        for key in ("divergence_curve", "divergence_final", "divergence_positive", "divergence_max", "reason"):
            assert key in r

    def test_curve_shape(self):
        r = compute_divergence(RM, GOLD)
        assert r["divergence_curve"].shape == RM.shape

    def test_final_positive(self):
        r = compute_divergence(RM, GOLD)
        assert r["divergence_final"] > 0
        assert r["divergence_positive"] is True

    def test_curve_values(self):
        r = compute_divergence(RM, GOLD)
        expected = RM - GOLD
        np.testing.assert_allclose(r["divergence_curve"], expected)


class TestRunAnalysis:
    def test_gate_passes_on_coste(self):
        df = pd.DataFrame({"kl_budget": KL, "rm_score": RM, "gold_preference": GOLD})
        r = run_analysis(df)
        assert r["gate_pass"] is True
        assert r["n_kl_levels"] == 10
        assert "divergence_curve" in r

    def test_baseline_values(self):
        df = pd.DataFrame({"kl_budget": KL, "rm_score": RM, "gold_preference": GOLD})
        r = run_analysis(df)
        assert r["baseline_rm"] == pytest.approx(RM[0])
        assert r["baseline_gold"] == pytest.approx(GOLD[0])
