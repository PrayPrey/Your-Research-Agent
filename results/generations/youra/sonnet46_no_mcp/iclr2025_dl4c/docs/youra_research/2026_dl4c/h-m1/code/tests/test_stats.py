"""Tests for A-3 StatsTester (stats.py) - spec compliance tests."""

import os
import sys
import numpy as np
import pandas as pd
import pytest

_ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), "..", "analysis")
sys.path.insert(0, _ANALYSIS_DIR)

from stats import run_wilcoxon_test, check_assumption_a1, compute_phase_stats
from loader import CONDITIONS


class TestRunWilcoxonTest:
    def test_returns_required_keys(self):
        c = np.array([0.8, 0.81, 0.79, 0.82, 0.80])
        u = np.array([0.5, 0.51, 0.49, 0.52, 0.50])
        result = run_wilcoxon_test(c, u)
        for key in ["statistic", "p_value", "passed", "curriculum_mean", "uniform_mean", "delta"]:
            assert key in result, f"Missing key: {key}"

    def test_one_tailed_greater(self):
        # curriculum clearly higher than uniform → should pass
        c = np.array([0.8, 0.81, 0.79, 0.82, 0.80])
        u = np.array([0.5, 0.51, 0.49, 0.52, 0.50])
        result = run_wilcoxon_test(c, u)
        assert result["passed"] is True
        assert result["p_value"] < 0.05

    def test_passed_matches_pvalue_threshold(self):
        c = np.array([0.8, 0.81, 0.79, 0.82, 0.80])
        u = np.array([0.5, 0.51, 0.49, 0.52, 0.50])
        result = run_wilcoxon_test(c, u)
        assert result["passed"] == (result["p_value"] < 0.05)

    def test_curriculum_mean_and_uniform_mean_correct(self):
        c = np.array([0.8, 0.8, 0.8, 0.8, 0.8])
        u = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        result = run_wilcoxon_test(c, u)
        assert abs(result["curriculum_mean"] - 0.8) < 1e-6
        assert abs(result["uniform_mean"] - 0.5) < 1e-6

    def test_delta_equals_curriculum_minus_uniform(self):
        c = np.array([0.8, 0.81, 0.79, 0.82, 0.80])
        u = np.array([0.5, 0.51, 0.49, 0.52, 0.50])
        result = run_wilcoxon_test(c, u)
        assert abs(result["delta"] - (result["curriculum_mean"] - result["uniform_mean"])) < 1e-10


class TestCheckAssumptionA1:
    def test_returns_required_keys(self):
        e = np.array([0.85, 0.86, 0.84, 0.87, 0.85])
        c = np.array([0.80, 0.81, 0.79, 0.82, 0.80])
        result = check_assumption_a1(e, c)
        for key in ["passed", "easy_only_mean", "curriculum_mean", "delta"]:
            assert key in result

    def test_passes_when_easy_only_higher(self):
        e = np.array([0.85, 0.85, 0.85, 0.85, 0.85])
        c = np.array([0.80, 0.80, 0.80, 0.80, 0.80])
        result = check_assumption_a1(e, c)
        assert result["passed"] is True

    def test_fails_when_curriculum_higher(self):
        e = np.array([0.50, 0.50, 0.50, 0.50, 0.50])
        c = np.array([0.80, 0.80, 0.80, 0.80, 0.80])
        result = check_assumption_a1(e, c)
        assert result["passed"] is False


class TestComputePhaseStats:
    def _make_logs(self, n=100):
        logs = {}
        for cond in CONDITIONS:
            rows = [{"step": i + 1, "reward_density": 0.7} for i in range(n)]
            logs[cond] = pd.DataFrame(rows)
        return logs

    def test_returns_all_conditions(self):
        logs = self._make_logs()
        result = compute_phase_stats(logs)
        assert set(result.keys()) == set(CONDITIONS)

    def test_each_condition_has_early_and_late(self):
        logs = self._make_logs()
        result = compute_phase_stats(logs)
        for cond in CONDITIONS:
            assert "early" in result[cond]
            assert "late" in result[cond]

    def test_each_phase_has_mean_and_std(self):
        logs = self._make_logs()
        result = compute_phase_stats(logs)
        for cond in CONDITIONS:
            for phase in ["early", "late"]:
                assert "mean" in result[cond][phase]
                assert "std" in result[cond][phase]
