#!/usr/bin/env python3
"""Minimal self-check for H-M4 core functions."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from run import (
    build_monthly_df,
    detect_saturation_date,
    compute_saturation_error,
    sensitivity_grid,
    verify_mechanism_activated,
)


def make_synthetic_df():
    """Synthetic logistic-shaped monthly series that clearly saturates (long tail)."""
    months = np.arange(0, 50, dtype=float)
    K = 0.90
    r = 0.5
    t0 = 10.0
    scores = K / (1 + np.exp(-r * (months - t0)))
    return months, scores


def test_build_monthly_df():
    t, y = make_synthetic_df()
    mdf = build_monthly_df(t, y, "glue")
    assert "top3_mean" in mdf.columns
    assert "monthly_gain" in mdf.columns
    assert "calendar_month" in mdf.columns
    assert len(mdf) >= 12
    print("PASS: build_monthly_df")


def test_detect_saturation():
    t, y = make_synthetic_df()
    mdf = build_monthly_df(t, y, "glue")
    K = 0.90
    sat_date, sat_idx = detect_saturation_date(mdf, K)
    assert sat_date is not None, "criterion should fire on saturated series"
    assert sat_idx is not None
    print(f"PASS: detect_saturation_date -> {sat_date} (month {sat_idx})")


def test_compute_error():
    err = compute_saturation_error("2019-09", "2019-09")
    assert err == 0, f"same month error should be 0, got {err}"
    err = compute_saturation_error("2019-10", "2019-09")
    assert err == 1, f"1-month error, got {err}"
    err = compute_saturation_error(None, "2019-09")
    assert err == float("inf")
    print("PASS: compute_saturation_error")


def test_verify_mechanism():
    results = {
        "glue":      {"sat_date": "2019-09", "sat_error_months": 0.0},
        "superglue": {"sat_date": "2021-06", "sat_error_months": 0.0},
    }
    activated, gate_pass, indicators = verify_mechanism_activated(results)
    assert activated
    assert gate_pass
    print("PASS: verify_mechanism_activated")


def test_sensitivity_grid():
    t, y = make_synthetic_df()
    mdf = build_monthly_df(t, y, "glue")
    K = 0.90
    grid = sensitivity_grid(mdf, K, [0.95, 0.99], [0.02, 0.05], "2019-09")
    assert len(grid) == 4
    print("PASS: sensitivity_grid")


if __name__ == "__main__":
    test_build_monthly_df()
    test_detect_saturation()
    test_compute_error()
    test_verify_mechanism()
    test_sensitivity_grid()
    print("\nAll tests PASSED")
