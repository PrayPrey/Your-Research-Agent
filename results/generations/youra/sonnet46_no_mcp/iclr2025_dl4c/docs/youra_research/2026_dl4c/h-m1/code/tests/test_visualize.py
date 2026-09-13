"""Tests for A-4 Visualizer (visualize.py) - spec compliance tests."""

import os
import sys
import numpy as np
import pandas as pd
import pytest

_ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), "..", "analysis")
sys.path.insert(0, _ANALYSIS_DIR)

from visualize import (
    plot_early_phase_bar,
    plot_timeseries,
    plot_wilcoxon_boxplot,
    plot_phase_comparison,
    CONDITIONS,
)
from stats import compute_phase_stats


def _make_mini_logs(n=50):
    logs = {}
    for cond in CONDITIONS:
        logs[cond] = pd.DataFrame({
            "step": list(range(1, n + 1)),
            "reward_density": [0.7 if cond == "curriculum" else 0.5] * n
        })
    return logs


def _make_phase_stats(logs):
    return compute_phase_stats(logs)


class TestPlotEarlyPhaseBar:
    def test_creates_png_file(self, tmp_path):
        logs = _make_mini_logs()
        ps = _make_phase_stats(logs)
        out = plot_early_phase_bar(ps, str(tmp_path))
        assert os.path.exists(out)
        assert out.endswith(".png")

    def test_output_filename_correct(self, tmp_path):
        logs = _make_mini_logs()
        ps = _make_phase_stats(logs)
        out = plot_early_phase_bar(ps, str(tmp_path))
        assert "reward_density_early_phase_bar" in out


class TestPlotTimeseries:
    def test_creates_png_file(self, tmp_path):
        logs = _make_mini_logs()
        out = plot_timeseries(logs, str(tmp_path))
        assert os.path.exists(out)

    def test_output_filename_correct(self, tmp_path):
        logs = _make_mini_logs()
        out = plot_timeseries(logs, str(tmp_path))
        assert "reward_density_timeseries" in out


class TestPlotWilcoxonBoxplot:
    def test_creates_png_file(self, tmp_path):
        c = np.array([0.8, 0.81, 0.79, 0.82, 0.80])
        u = np.array([0.5, 0.51, 0.49, 0.52, 0.50])
        out = plot_wilcoxon_boxplot(c, u, 0.031, str(tmp_path))
        assert os.path.exists(out)

    def test_output_filename_correct(self, tmp_path):
        c = np.array([0.8, 0.81, 0.79, 0.82, 0.80])
        u = np.array([0.5, 0.51, 0.49, 0.52, 0.50])
        out = plot_wilcoxon_boxplot(c, u, 0.031, str(tmp_path))
        assert "reward_density_wilcoxon_boxplot" in out


class TestPlotPhaseComparison:
    def test_creates_png_file(self, tmp_path):
        logs = _make_mini_logs()
        ps = _make_phase_stats(logs)
        out = plot_phase_comparison(ps, str(tmp_path))
        assert os.path.exists(out)

    def test_output_filename_correct(self, tmp_path):
        logs = _make_mini_logs()
        ps = _make_phase_stats(logs)
        out = plot_phase_comparison(ps, str(tmp_path))
        assert "reward_density_phase_comparison" in out
