"""Tests for A-5 RewardDensityAnalyzer (analyze_reward_density.py) - spec compliance."""

import json
import os
import sys
import numpy as np
import pandas as pd
import pytest

_ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), "..", "analysis")
sys.path.insert(0, _ANALYSIS_DIR)

from analyze_reward_density import run_analysis, save_results, print_summary
from loader import CONDITIONS


def _make_logs(tmpdir, n_rows=2500):
    os.makedirs(tmpdir, exist_ok=True)
    for cond in CONDITIONS:
        density = 0.8 if cond == "curriculum" else (0.85 if cond == "easy_only" else 0.5)
        rows = [{"step": i + 1, "reward_density": density} for i in range(n_rows)]
        pd.DataFrame(rows).to_csv(
            os.path.join(tmpdir, f"reward_density_{cond}.csv"), index=False
        )


class TestRunAnalysis:
    def test_returns_gate_passed_bool(self, tmp_path):
        log_dir = str(tmp_path / "logs")
        fig_dir = str(tmp_path / "figures")
        _make_logs(log_dir)
        result = run_analysis(log_dir=log_dir, figures_dir=fig_dir)
        assert "gate_passed" in result
        assert isinstance(result["gate_passed"], bool)

    def test_returns_wilcoxon_dict(self, tmp_path):
        log_dir = str(tmp_path / "logs")
        fig_dir = str(tmp_path / "figures")
        _make_logs(log_dir)
        result = run_analysis(log_dir=log_dir, figures_dir=fig_dir)
        assert "wilcoxon" in result
        for key in ["statistic", "p_value", "passed", "curriculum_mean", "uniform_mean", "delta"]:
            assert key in result["wilcoxon"]

    def test_generates_4_figures(self, tmp_path):
        log_dir = str(tmp_path / "logs")
        fig_dir = str(tmp_path / "figures")
        _make_logs(log_dir)
        result = run_analysis(log_dir=log_dir, figures_dir=fig_dir)
        assert len(result["figure_paths"]) == 4
        for path in result["figure_paths"]:
            assert os.path.exists(path)

    def test_curriculum_higher_means_gate_pass(self, tmp_path):
        log_dir = str(tmp_path / "logs")
        fig_dir = str(tmp_path / "figures")
        _make_logs(log_dir, n_rows=2500)
        result = run_analysis(log_dir=log_dir, figures_dir=fig_dir)
        # curriculum (0.8) >> uniform (0.5), should pass
        assert result["wilcoxon"]["curriculum_mean"] > result["wilcoxon"]["uniform_mean"]


class TestSaveResults:
    def test_writes_json_file(self, tmp_path):
        results = {
            "gate_passed": True,
            "wilcoxon": {"statistic": 15.0, "p_value": 0.031, "passed": True,
                         "curriculum_mean": 0.8, "uniform_mean": 0.5, "delta": 0.3},
            "assumption_a1": {"passed": True, "easy_only_mean": 0.85,
                               "curriculum_mean": 0.8, "delta": 0.05},
            "phase_stats": {},
            "figure_paths": [],
            "results_path": str(tmp_path / "wilcoxon_results.json"),
        }
        out_path = save_results(results, str(tmp_path))
        assert os.path.exists(out_path)

    def test_json_has_required_schema_fields(self, tmp_path):
        results = {
            "gate_passed": True,
            "wilcoxon": {"statistic": 15.0, "p_value": 0.031, "passed": True,
                         "curriculum_mean": 0.8, "uniform_mean": 0.5, "delta": 0.3},
            "assumption_a1": {"passed": True, "easy_only_mean": 0.85,
                               "curriculum_mean": 0.8, "delta": 0.05},
            "phase_stats": {},
            "figure_paths": [],
            "results_path": str(tmp_path / "wilcoxon_results.json"),
        }
        out_path = save_results(results, str(tmp_path))
        with open(out_path) as f:
            loaded = json.load(f)
        assert "gate_passed" in loaded
        assert "wilcoxon" in loaded
        assert isinstance(loaded["gate_passed"], bool)


class TestPrintSummary:
    def test_runs_without_error(self, capsys):
        results = {
            "gate_passed": True,
            "wilcoxon": {"statistic": 15.0, "p_value": 0.031, "passed": True,
                         "curriculum_mean": 0.8, "uniform_mean": 0.5, "delta": 0.3},
            "assumption_a1": {"passed": True, "easy_only_mean": 0.85,
                               "curriculum_mean": 0.8, "delta": 0.05},
        }
        print_summary(results)
        captured = capsys.readouterr()
        assert "PASSED" in captured.out or "FAILED" in captured.out
