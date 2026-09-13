import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from analyze import compute_mean_early_gdr, run_wilcoxon_test, check_gate
from config import GDRConfig


def test_compute_mean_early_gdr():
    gdr_series = [2.0, 1.5, 1.2] + [1.0] * 12
    result = compute_mean_early_gdr(gdr_series, early_epochs=[2, 4, 6], checkpoint_interval=2)
    expected = (2.0 + 1.5 + 1.2) / 3
    assert abs(result - expected) < 1e-6


def test_run_wilcoxon_returns_dict():
    spurious = np.array([1.5, 1.3, 1.2])
    core = np.array([1.0, 0.9, 0.8])
    result = run_wilcoxon_test(spurious, core)
    assert "stat" in result
    assert "p_value" in result
    assert isinstance(result["stat"], float)
    assert isinstance(result["p_value"], float)


def test_run_wilcoxon_significant():
    # Need n>=6 for Wilcoxon to reach p<0.05; use 6 consistent differences
    spurious = np.array([1.5, 1.4, 1.3, 1.2, 1.15, 1.1])
    core = np.array([0.8, 0.75, 0.7, 0.65, 0.6, 0.55])
    result = run_wilcoxon_test(spurious, core)
    assert result["p_value"] < 0.05


def test_check_gate_pass():
    cfg = GDRConfig(min_seeds_pass=2, p_threshold=0.05)
    analysis = {
        "mean_early_gdr_per_seed": {1: 1.5, 2: 1.3, 3: 1.2},
        "wilcoxon_results": {
            1: {"p_value": 0.03},
            2: {"p_value": 0.04},
            3: {"p_value": 0.02},
        },
    }
    assert check_gate(analysis, cfg) is True


def test_check_gate_fail():
    cfg = GDRConfig(min_seeds_pass=2, p_threshold=0.05)
    analysis = {
        "mean_early_gdr_per_seed": {1: 0.8, 2: 0.7, 3: 0.9},
        "wilcoxon_results": {
            1: {"p_value": 0.3},
            2: {"p_value": 0.4},
            3: {"p_value": 0.5},
        },
    }
    assert check_gate(analysis, cfg) is False
