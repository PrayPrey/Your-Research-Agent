"""Tests for A-4: Statistical Analysis and Gate Evaluation (spec compliance)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import pandas as pd

from config import ExperimentConfig, TrainConfig, ProbeConfig, GateConfig, DatasetPathConfig


def make_cfg(tmp_path=None):
    return ExperimentConfig(
        train=TrainConfig(
            dataset="waterbirds",
            data_root="./data/waterbirds",
            checkpoint_dir="./checkpoints",
            epochs=20,
            seeds=[1, 2, 3],
        ),
        probe=ProbeConfig(),
        gate=GateConfig(min_window_fraction=0.10, p_threshold=0.05),
        paths=DatasetPathConfig(),
        results_dir=str(tmp_path / "results") if tmp_path else "./results",
    )


def make_results_df(n_epochs=20, n_seeds=3, delta_pattern="positive_early"):
    """Generate synthetic results DataFrame for testing."""
    records = []
    for seed in range(1, n_seeds + 1):
        for t in range(2, n_epochs + 1, 2):
            if delta_pattern == "positive_early":
                spurious = 0.7 + 0.1 * (t / n_epochs)
                core = 0.5 + 0.2 * (t / n_epochs)
            elif delta_pattern == "negative":
                spurious = 0.5
                core = 0.8
            else:
                spurious = 0.6
                core = 0.6
            delta = spurious - core
            records.append({"epoch": t, "spurious_acc": spurious,
                             "core_acc": core, "delta": delta, "seed": seed})
    return pd.DataFrame(records)


def test_analyze_import():
    from analyze import (compute_delta_series, find_contiguous_window,
                         paired_ttest, evaluate_gate, run_analysis)
    assert compute_delta_series is not None


def test_compute_delta_series():
    from analyze import compute_delta_series
    df = pd.DataFrame({"spurious_acc": [0.8, 0.7], "core_acc": [0.6, 0.6], "seed": [1, 1]})
    result = compute_delta_series(df)
    assert "delta" in result.columns
    np.testing.assert_allclose(result["delta"].values, [0.2, 0.1], atol=1e-6)


def test_find_contiguous_window_positive():
    from analyze import find_contiguous_window
    # All positive
    delta_mean = np.array([0.1, 0.2, 0.15, 0.05, 0.01])
    epochs = np.array([2, 4, 6, 8, 10])
    start, end, frac = find_contiguous_window(delta_mean, epochs)
    assert frac == 1.0  # All positive


def test_find_contiguous_window_partial():
    from analyze import find_contiguous_window
    delta_mean = np.array([0.2, 0.1, -0.1, 0.05, -0.2])
    epochs = np.array([2, 4, 6, 8, 10])
    start, end, frac = find_contiguous_window(delta_mean, epochs)
    assert frac == 2/5  # 2 contiguous positive at start


def test_paired_ttest_significant():
    from analyze import paired_ttest
    # delta clearly > 0
    delta = np.array([[0.2, 0.25, 0.18], [0.22, 0.2, 0.21]])  # (n_seeds=2, n_epochs=3) -> transposed
    delta_by_seed = np.array([[0.2, 0.25, 0.18], [0.22, 0.2, 0.21]])
    t, p = paired_ttest(delta_by_seed)
    assert isinstance(t, float)
    assert isinstance(p, float)
    assert 0.0 <= p <= 1.0


def test_evaluate_gate_pass():
    from analyze import evaluate_gate
    cfg = make_cfg()
    result = evaluate_gate(window_fraction=0.5, p_value=0.01, cfg=cfg)
    assert result["pass"] is True
    assert result["decision"] == "PASS"
    assert result["gate"] == "MUST_WORK"


def test_evaluate_gate_fail_window():
    from analyze import evaluate_gate
    cfg = make_cfg()
    result = evaluate_gate(window_fraction=0.05, p_value=0.01, cfg=cfg)
    assert result["pass"] is False
    assert result["decision"] == "FAIL"


def test_evaluate_gate_fail_pvalue():
    from analyze import evaluate_gate
    cfg = make_cfg()
    result = evaluate_gate(window_fraction=0.5, p_value=0.1, cfg=cfg)
    assert result["pass"] is False


def test_run_analysis_saves_json(tmp_path):
    from analyze import run_analysis
    cfg = make_cfg(tmp_path)
    df = make_results_df()
    result = run_analysis(df, cfg)
    json_path = os.path.join(cfg.results_dir, "h-e1_results.json")
    assert os.path.exists(json_path)
    assert "gate_pass" in result
    assert "window_fraction" in result
    assert "per_seed" in result


def test_run_analysis_schema(tmp_path):
    from analyze import run_analysis
    cfg = make_cfg(tmp_path)
    df = make_results_df()
    result = run_analysis(df, cfg)
    required_keys = ["hypothesis_id", "dataset", "gate_pass", "window_fraction",
                     "p_value", "gap_area", "t_star_mean", "t_star_std", "per_seed"]
    for k in required_keys:
        assert k in result, f"Missing key: {k}"
    assert result["hypothesis_id"] == "h-e1"
