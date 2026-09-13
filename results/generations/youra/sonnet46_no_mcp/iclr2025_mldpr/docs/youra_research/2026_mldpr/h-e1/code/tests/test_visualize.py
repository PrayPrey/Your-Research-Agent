"""Tests for src/visualize.py (task-012)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import types
import tempfile
from src.visualize import plot_fair_distribution, plot_cv_summary, generate_figures


def _make_scored(n=200):
    rng = np.random.default_rng(0)
    scores = rng.uniform(0, 1, n)
    return pd.DataFrame({
        "did": range(n),
        "fair_aggregate": scores,
        "fair_F": scores * 0.9,
        "fair_A": scores * 0.8,
        "fair_I": scores * 0.7,
        "fair_R": scores * 1.0,
        "status": ["ok"] * n,
        "upload_date_ordinal": rng.integers(700000, 740000, n),
    })


def test_plot_fair_distribution_creates_file():
    scored = _make_scored()
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "test_dist.png")
        plot_fair_distribution(scored, "fair_aggregate", 0.5, out_path)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 1000


def test_plot_cv_summary_creates_file():
    metrics = {"cv": 0.28, "n_high": 650, "n_low": 350}
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "test_cv.png")
        plot_cv_summary(metrics, out_path)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 1000


def test_generate_figures_creates_at_least_two_pngs():
    scored = _make_scored()
    metrics = {"cv": 0.28, "n_high": 650, "n_low": 350,
               "mean_fair": 0.5, "std_fair": 0.14}
    cfg = types.SimpleNamespace(FAIR_THRESHOLD=0.5)
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_figures(scored, metrics, tmpdir, cfg)
        pngs = [f for f in os.listdir(tmpdir) if f.endswith(".png")]
        assert len(pngs) >= 2
