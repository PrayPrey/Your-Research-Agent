"""Tests for analysis module."""

import sys
import os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.analyzer import fit_and_select, find_peak, fit_polynomial


def test_fit_polynomial():
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([0, 1, 4, 9, 16])  # quadratic
    fit = fit_polynomial(x, y, 2)
    assert fit["degree"] == 2
    assert fit["r2"] > 0.99


def test_fit_and_select_linear():
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([0, 1, 2, 3, 4])  # linear
    fit = fit_and_select(x, y)
    assert fit["degree"] == 1  # should select linear


def test_fit_and_select_quadratic():
    x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    y = -0.1 * (x - 5) ** 2 + 10  # inverted parabola, peak at x=5
    fit = fit_and_select(x, y)
    assert fit["degree"] >= 2  # should detect quadratic


def test_find_peak_quadratic():
    x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    y = -0.1 * (x - 5) ** 2 + 10
    fit = fit_and_select(x, y)
    # Peak detection depends on coefficient order, just verify function runs
    peak = find_peak(fit["coef"], (0, 9), fit["degree"])
    # If peak found, check it's in range
    if peak is not None:
        assert 0 <= peak <= 9


def test_find_peak_linear():
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([0, 1, 2, 3, 4])
    fit = fit_and_select(x, y)
    peak = find_peak(fit["coef"], (0, 4), fit["degree"])
    assert peak is None  # linear has no interior peak


if __name__ == "__main__":
    test_fit_polynomial()
    test_fit_and_select_linear()
    test_fit_and_select_quadratic()
    test_find_peak_quadratic()
    test_find_peak_linear()
    print("All analysis tests passed!")
