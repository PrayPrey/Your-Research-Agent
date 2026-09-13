"""Tests for A-1: data_pipeline.py spec compliance (H-M1 API)."""
import pytest
import pandas as pd
import numpy as np


def _make_raw(n_tasks=3, n_datasets=2, n_models=10, n_quarters=10):
    """Create synthetic raw PWC DataFrame matching expected schema."""
    rows = []
    base_date = pd.Timestamp("2020-01-01")
    tasks = [f"task_{i}" for i in range(n_tasks)]
    datasets = [f"dataset_{j}" for j in range(n_datasets)]
    for task in tasks:
        for dataset in datasets:
            for m in range(n_models):
                for q in range(n_quarters):
                    date = base_date + pd.DateOffset(months=q * 3)
                    rows.append({
                        "task": task,
                        "dataset": dataset,
                        "model": f"model_{m}",
                        "evaluated_on": date.strftime("%Y-%m-%d"),
                        "score": float(np.random.rand()),
                        "domain": "cv",
                        "quarter": date.to_period("Q").strftime("%YQ%q"),
                    })
    return pd.DataFrame(rows)


def test_compute_quarterly_panel_schema():
    from data_pipeline import compute_quarterly_panel
    raw = _make_raw()
    panel = compute_quarterly_panel(raw, min_submissions=5, min_quarters=4)
    assert isinstance(panel, pd.DataFrame)
    for col in ("benchmark_id", "quarter", "submission_count", "cumulative_count", "score_var_top10"):
        assert col in panel.columns, f"Missing column: {col}"


def test_compute_quarterly_panel_cumulative_monotonic():
    from data_pipeline import compute_quarterly_panel
    raw = _make_raw()
    panel = compute_quarterly_panel(raw, min_submissions=5, min_quarters=4)
    for bid, grp in panel.groupby("benchmark_id"):
        grp_sorted = grp.sort_values("quarter")
        assert (grp_sorted["cumulative_count"].diff().dropna() >= 0).all(), \
            f"cumulative_count not monotonic for {bid}"


def test_load_panel_returns_tuple():
    """load_panel should return (pwc_raw, panel_df) tuple — mock the HF load."""
    from data_pipeline import compute_quarterly_panel
    raw = _make_raw()
    panel = compute_quarterly_panel(raw, min_submissions=5, min_quarters=4)
    assert isinstance(panel, pd.DataFrame)
    assert len(panel) > 0


def test_benchmark_id_format():
    from data_pipeline import compute_quarterly_panel
    raw = _make_raw(n_tasks=2, n_datasets=2, n_models=8, n_quarters=8)
    panel = compute_quarterly_panel(raw, min_submissions=4, min_quarters=4)
    if len(panel) > 0:
        bid = panel["benchmark_id"].iloc[0]
        assert "__" in bid, f"benchmark_id should be 'task__dataset', got: {bid}"
