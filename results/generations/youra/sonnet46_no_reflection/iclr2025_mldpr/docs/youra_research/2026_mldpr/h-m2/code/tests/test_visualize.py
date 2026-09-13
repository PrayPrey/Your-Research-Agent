"""Tests for A-8: visualize.py spec compliance (H-M1 API)."""
import pytest
import numpy as np
import pandas as pd
import os


def _make_panel_df(n=100):
    rng = np.random.default_rng(42)
    rows = []
    for i in range(n):
        rows.append({
            "benchmark_id": f"bench_{i % 10}",
            "task": "image-classification",
            "dataset": f"dataset_{i % 5}",
            "quarter": f"202{i//25}Q{(i%4)+1}",
            "submission_count": int(rng.integers(5, 50)),
            "cumulative_count": float(rng.integers(10, 500)),
            "score_var_top10": float(rng.uniform(0.0, 0.1)),
            "sigma_meas": float(rng.uniform(0.01, 0.05)),
            "compression_event": int(rng.integers(0, 2)),
            "domain": "cv",
        })
    return pd.DataFrame(rows)


def _make_spearman_result():
    return {"rho": 0.55, "p_value": 0.001, "n_obs": 200}


def _make_granger_results():
    return {f"bench_{i}": {1: 0.01, 2: 0.02, 3: 0.05, 4: 0.1} for i in range(10)}


def _make_granger_agg():
    return {"min_p_lag2": 0.001, "n_significant_lag2": 20,
            "pct_significant_lag2": 0.5, "median_p_lag2": 0.02,
            "n_benchmarks_tested": 40}


def test_generate_all_figures_creates_pngs(tmp_path):
    import matplotlib
    matplotlib.use("Agg")
    from visualize import generate_all_figures
    panel_df = _make_panel_df()
    spearman_result = _make_spearman_result()
    granger_results = _make_granger_results()
    reverse_results = _make_granger_results()
    granger_agg = _make_granger_agg()
    out_dir = str(tmp_path)
    generate_all_figures(panel_df, spearman_result, granger_results,
                         reverse_results, granger_agg, out_dir)
    assert os.path.exists(os.path.join(out_dir, "gate_metrics.png"))
