"""Tests for analysis.py — statistical computation functions."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def make_test_df(n=12, seed=42):
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


class TestComputeRawRhoAll:
    def test_returns_expected_keys(self):
        from analysis import compute_raw_rho_all
        df = make_test_df()
        result = compute_raw_rho_all(df)
        for key in ["rho_fair_raw", "rho_advglue_raw", "rho_anli_raw", "delta_rho_raw", "n"]:
            assert key in result, f"Missing key: {key}"

    def test_rho_values_in_range(self):
        from analysis import compute_raw_rho_all
        result = compute_raw_rho_all(make_test_df())
        for key in ["rho_fair_raw", "rho_advglue_raw", "rho_anli_raw"]:
            assert -1.0 <= result[key] <= 1.0, f"{key} out of range"

    def test_delta_raw_equals_fair_minus_mean(self):
        from analysis import compute_raw_rho_all
        result = compute_raw_rho_all(make_test_df())
        expected = result["rho_fair_raw"] - np.mean([result["rho_advglue_raw"], result["rho_anli_raw"]])
        assert abs(result["delta_rho_raw"] - expected) < 1e-9


class TestComputePartialRho:
    def test_returns_expected_keys(self):
        from analysis import compute_partial_rho
        df = make_test_df()
        result = compute_partial_rho(df, "bbq_disambig", "bbq_ambig", "mmlu")
        for key in ["rho", "p_value", "ci95", "n"]:
            assert key in result, f"Missing key: {key}"

    def test_rho_in_range(self):
        from analysis import compute_partial_rho
        result = compute_partial_rho(make_test_df(), "bbq_disambig", "bbq_ambig", "mmlu")
        assert -1.0 <= result["rho"] <= 1.0

    def test_ci95_has_two_elements(self):
        from analysis import compute_partial_rho
        result = compute_partial_rho(make_test_df(), "bbq_disambig", "bbq_ambig", "mmlu")
        assert len(result["ci95"]) == 2
        assert result["ci95"][0] <= result["rho"] <= result["ci95"][1]

    def test_missing_covar_raises(self):
        from analysis import compute_partial_rho
        df = make_test_df().drop(columns=["mmlu"])
        with pytest.raises(AssertionError, match="covar 'mmlu' not in DataFrame"):
            compute_partial_rho(df, "bbq_disambig", "bbq_ambig", "mmlu")

    def test_works_with_winogrande_covar(self):
        from analysis import compute_partial_rho
        result = compute_partial_rho(make_test_df(), "bbq_disambig", "bbq_ambig", "winogrande")
        assert "rho" in result


class TestFisherZTestDifference:
    def test_positive_delta_gives_positive_z(self):
        from analysis import fisher_z_test_difference
        result = fisher_z_test_difference(rho1=0.7, rho2=0.2, n=13)
        assert result["z_stat"] > 0, "z_stat should be positive when rho1 > rho2"

    def test_p_value_in_range(self):
        from analysis import fisher_z_test_difference
        result = fisher_z_test_difference(rho1=0.65, rho2=0.15, n=13)
        assert 0.0 <= result["p_value_two_tailed"] <= 1.0

    def test_returns_expected_keys(self):
        from analysis import fisher_z_test_difference
        result = fisher_z_test_difference(rho1=0.6, rho2=0.2, n=12)
        for key in ["z_stat", "p_value_two_tailed", "z_rho1", "z_rho2", "se_diff"]:
            assert key in result, f"Missing key: {key}"

    def test_raises_on_rho_equals_1(self):
        from analysis import fisher_z_test_difference
        with pytest.raises(ValueError, match="|rho1|"):
            fisher_z_test_difference(rho1=1.0, rho2=0.3, n=12)

    def test_raises_on_n_too_small(self):
        from analysis import fisher_z_test_difference
        with pytest.raises(ValueError, match="n=3"):
            fisher_z_test_difference(rho1=0.6, rho2=0.2, n=3)

    def test_symmetric_in_z_stat(self):
        """z_stat magnitude same regardless of direction."""
        from analysis import fisher_z_test_difference
        r1 = fisher_z_test_difference(rho1=0.6, rho2=0.2, n=13)
        r2 = fisher_z_test_difference(rho1=0.2, rho2=0.6, n=13)
        assert abs(abs(r1["z_stat"]) - abs(r2["z_stat"])) < 1e-9


class TestEvaluateGate:
    def test_passes_at_threshold(self):
        from analysis import evaluate_gate
        assert evaluate_gate(0.2) is True

    def test_fails_below_threshold(self):
        from analysis import evaluate_gate
        assert evaluate_gate(0.19) is False

    def test_passes_above_threshold(self):
        from analysis import evaluate_gate
        assert evaluate_gate(0.5) is True
