"""Unit tests for src/visualize.py"""
import os, sys
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.visualize import plot_gate_metrics, plot_cox_forest, generate_all_figures


def test_plot_gate_metrics_creates_file(tmp_path):
    path = plot_gate_metrics(0.03, 1.5, str(tmp_path))
    assert os.path.exists(path)
    assert path.endswith(".png")


def test_plot_cox_forest_creates_file(tmp_path):
    path = plot_cox_forest(1.5, 1.1, 2.0, str(tmp_path))
    assert os.path.exists(path)


def test_generate_all_figures_returns_paths(tmp_path):
    results = {
        "log_rank_p": 0.03,
        "cox_hr": 1.5,
        "cox_ci_lower": 1.1,
        "cox_ci_upper": 2.0,
        "kmf_high": None,
        "kmf_low": None,
        "median_ttfr_high": 100.0,
        "median_ttfr_low": 200.0,
        "smd_df": pd.DataFrame({"covariate": ["x"], "smd_before": [0.2], "smd_after": [0.05]}),
        "ablations": {},
        "ps_before": pd.Series([0.3, 0.5, 0.7]),
        "ps_after": pd.Series([0.4, 0.5, 0.6]),
    }
    paths = generate_all_figures(results, str(tmp_path))
    assert len(paths) >= 4
