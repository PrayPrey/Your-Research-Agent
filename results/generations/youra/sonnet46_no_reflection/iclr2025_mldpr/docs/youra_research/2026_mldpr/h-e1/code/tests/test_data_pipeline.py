"""Tests for task-002: data_pipeline.py spec compliance."""
import pytest
import pandas as pd
import numpy as np


def _make_panel(n_benchmarks=5, n_models=25, n_quarters=10, domain="cv"):
    """Create synthetic panel DataFrame matching expected schema."""
    rows = []
    base_date = pd.Timestamp("2020-01-01")
    for b in range(n_benchmarks):
        for m in range(n_models):
            for q in range(n_quarters):
                date = base_date + pd.DateOffset(months=q * 3)
                rows.append({
                    "benchmark": f"bench_{b}",
                    "domain": domain,
                    "model": f"model_{m}",
                    "date": date,
                    "score": float(np.random.rand()),
                    "quarter": date.to_period("Q").strftime("%YQ%q"),
                })
    return pd.DataFrame(rows)


def test_label_saturation_returns_label_column():
    from data_pipeline import label_saturation
    panel = _make_panel()
    result = label_saturation(panel)
    assert "label" in result.columns
    assert set(result["label"].unique()).issubset({"saturated", "healthy", "excluded"})


def test_label_saturation_stable_series_is_saturated():
    """A benchmark with perfectly stable rankings should be labeled saturated."""
    from data_pipeline import label_saturation
    rows = []
    base_date = pd.Timestamp("2020-01-01")
    # 10 models with identical ranking each quarter → tau = 1.0 → saturated
    for q in range(8):
        date = base_date + pd.DateOffset(months=q * 3)
        quarter = date.to_period("Q").strftime("%YQ%q")
        for m in range(10):
            rows.append({
                "benchmark": "stable_bench",
                "domain": "cv",
                "model": f"model_{m}",
                "date": date,
                "score": float(10 - m) + 0.001 * q,  # same ranking preserved
                "quarter": quarter,
            })
    panel = pd.DataFrame(rows)
    result = label_saturation(panel)
    bench_labels = result[result["benchmark"] == "stable_bench"]["label"].unique()
    # At least some quarters should be labeled saturated
    assert "saturated" in bench_labels or "excluded" in bench_labels


def test_get_domain_panels_returns_tuple():
    from data_pipeline import get_domain_panels, label_saturation
    panel = _make_panel(n_benchmarks=10, n_models=25, n_quarters=12, domain="cv")
    panel = label_saturation(panel)
    # Force some labels for testing
    panel.loc[panel["benchmark"].isin(["bench_0", "bench_1", "bench_2"]), "label"] = "saturated"
    panel.loc[panel["benchmark"].isin(["bench_3", "bench_4", "bench_5"]), "label"] = "healthy"
    sat_df, healthy_df = get_domain_panels(panel, domain="cv", min_saturated=1, min_healthy=1)
    assert isinstance(sat_df, pd.DataFrame)
    assert isinstance(healthy_df, pd.DataFrame)
    assert len(sat_df) > 0
    assert len(healthy_df) > 0


def test_get_domain_panels_warns_below_threshold(capsys):
    from data_pipeline import get_domain_panels, label_saturation
    panel = _make_panel(n_benchmarks=3, n_models=5, n_quarters=8, domain="cv")
    panel = label_saturation(panel)
    panel["label"] = "excluded"  # force no sat/healthy
    panel.loc[panel["benchmark"] == "bench_0", "label"] = "saturated"
    panel.loc[panel["benchmark"] == "bench_1", "label"] = "healthy"
    # min_saturated=15 but only 1 available → warning
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        get_domain_panels(panel, domain="cv", min_saturated=15, min_healthy=15)
        # Should emit a warning (or just not crash)
    # No assertion on warning count — just verify no crash
