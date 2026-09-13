"""Tests for H-M4 analysis module — spec compliance."""
import sys
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

# Add code dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis import (
    compute_kendall_tau, compute_spearman, compute_delta_r2,
    compute_cross_model_gap, bootstrap_gap_ci, verify_mechanism_activated,
    run_analysis, TauResult, SpearmanResult, DeltaR2Result, GapResult, H_M4_Results,
)
from data_loader import build_df_long


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def simple_5_model_data():
    """5 models × 50 tasks synthetic data with known properties."""
    np.random.seed(42)
    models = ["gpt-4o-mini", "deepseek-coder-v2-lite", "claude-3-haiku", "codellama-34b", "codellama-13b"]
    tasks = [f"task_{i}" for i in range(50)]
    rows = []
    # Contract rates inversely related to pass@1 (orthogonal scenario)
    contract_base = {"gpt-4o-mini": 0.5, "deepseek-coder-v2-lite": 0.7,
                     "claude-3-haiku": 0.6, "codellama-34b": 0.4, "codellama-13b": 0.3}
    for m in models:
        for t in tasks:
            rate = np.clip(contract_base[m] + np.random.normal(0, 0.05), 0, 1)
            rows.append({"model_id": m, "task_id": t, "contract_satisfaction_rate": rate})
    return pd.DataFrame(rows)


@pytest.fixture
def pass_at_1_dict():
    return {
        "gpt-4o-mini": 0.778,
        "deepseek-coder-v2-lite": 0.787,
        "claude-3-haiku": 0.695,
        "codellama-34b": 0.625,
        "codellama-13b": 0.555,
    }


@pytest.fixture
def df_long(simple_5_model_data, pass_at_1_dict):
    task_meta = {}
    return build_df_long(simple_5_model_data, pass_at_1_dict, task_meta)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestComputeKendallTau:
    def test_returns_tau_result(self):
        x = np.array([0.5, 0.7, 0.6, 0.4, 0.3])
        y = np.array([0.778, 0.787, 0.695, 0.625, 0.555])
        result = compute_kendall_tau(x, y)
        assert isinstance(result, TauResult)

    def test_tau_in_range(self):
        x = np.array([0.5, 0.7, 0.6, 0.4, 0.3])
        y = np.array([0.778, 0.787, 0.695, 0.625, 0.555])
        result = compute_kendall_tau(x, y)
        assert -1.0 <= result.tau <= 1.0

    def test_pvalue_in_range(self):
        x = np.array([0.5, 0.7, 0.6, 0.4, 0.3])
        y = np.array([0.778, 0.787, 0.695, 0.625, 0.555])
        result = compute_kendall_tau(x, y)
        assert 0.0 <= result.pvalue <= 1.0

    def test_null_distribution_nonempty(self):
        """Exact permutation: null distribution has entries."""
        x = np.array([0.5, 0.7, 0.6, 0.4, 0.3])
        y = np.array([0.778, 0.787, 0.695, 0.625, 0.555])
        result = compute_kendall_tau(x, y)
        assert len(result.null_distribution) >= 100  # at least 100 permutations

    def test_perfect_positive_correlation(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = compute_kendall_tau(x, y)
        assert abs(result.tau - 1.0) < 1e-6

    def test_perfect_negative_correlation(self):
        x = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = compute_kendall_tau(x, y)
        assert abs(result.tau - (-1.0)) < 1e-6


class TestComputeSpearman:
    def test_returns_spearman_result(self):
        x = np.array([0.5, 0.7, 0.6, 0.4, 0.3])
        y = np.array([0.778, 0.787, 0.695, 0.625, 0.555])
        result = compute_spearman(x, y)
        assert isinstance(result, SpearmanResult)
        assert -1.0 <= result.rho <= 1.0
        assert 0.0 <= result.pvalue <= 1.0


class TestComputeDeltaR2:
    def test_returns_delta_r2_result(self, df_long):
        result = compute_delta_r2(df_long)
        assert isinstance(result, DeltaR2Result)

    def test_r2_values_in_range(self, df_long):
        result = compute_delta_r2(df_long)
        assert 0.0 <= result.r2_full <= 1.0
        assert 0.0 <= result.r2_reduced <= 1.0

    def test_has_converged_flag(self, df_long):
        result = compute_delta_r2(df_long)
        assert isinstance(result.converged, bool)
        assert isinstance(result.fallback_ols, bool)


class TestComputeCrossModelGap:
    def test_returns_gap_result(self, df_long):
        result = compute_cross_model_gap(df_long)
        assert isinstance(result, GapResult)

    def test_gap_nonnegative(self, df_long):
        result = compute_cross_model_gap(df_long)
        assert result.gap >= 0.0

    def test_ci_ordering(self, df_long):
        result = compute_cross_model_gap(df_long)
        assert result.ci_low <= result.gap <= result.ci_high

    def test_best_worst_are_model_ids(self, df_long):
        result = compute_cross_model_gap(df_long)
        model_ids = df_long["model_id"].unique()
        assert result.best_model in model_ids
        assert result.worst_model in model_ids


class TestRunAnalysis:
    def test_returns_h_m4_results(self, simple_5_model_data, df_long, pass_at_1_dict):
        result = run_analysis(simple_5_model_data, df_long, pass_at_1_dict)
        assert isinstance(result, H_M4_Results)

    def test_gate_flags_are_bool(self, simple_5_model_data, df_long, pass_at_1_dict):
        result = run_analysis(simple_5_model_data, df_long, pass_at_1_dict)
        assert isinstance(result.gate_pass, bool)
        assert isinstance(result.gate_partial, bool)

    def test_not_both_pass_and_partial(self, simple_5_model_data, df_long, pass_at_1_dict):
        result = run_analysis(simple_5_model_data, df_long, pass_at_1_dict)
        assert not (result.gate_pass and result.gate_partial)

    def test_mechanism_activates(self, simple_5_model_data, df_long, pass_at_1_dict):
        result = run_analysis(simple_5_model_data, df_long, pass_at_1_dict)
        activated, indicators = verify_mechanism_activated(result)
        assert indicators["tau_computed"]
        assert indicators["delta_R2_computed"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
