"""Integration smoke test for H-M1: mock H-E1 CSV/JSON, assert gate fields present."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add code/ to path
_CODE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_CODE_DIR))

from data_loader import load_residual_cov, load_paper_count_star_idx
from analyzer import analyze, compute_global_variance, split_segments, run_f_test, run_brown_forsythe
from verifier import verify_mechanism_activated


def _make_mock_csv(tmp_path: Path, n: int = 111) -> Path:
    """Create a minimal pwc_cov_computed.csv with N=111 rows."""
    rng = np.random.default_rng(42)
    paper_counts = np.arange(1, n + 1)
    cov = rng.uniform(0.1, 0.9, n)
    residual_cov = rng.normal(0, 0.1, n)
    df = pd.DataFrame({
        "benchmark_name": [f"bench_{i}" for i in range(n)],
        "paper_count": paper_counts,
        "cov": cov,
        "residual_cov": residual_cov,
    })
    csv_path = tmp_path / "pwc_cov_computed.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


def _make_mock_json(tmp_path: Path, breakpoint_idx: int = 34) -> Path:
    """Create a minimal H-E1 experiment_results.json."""
    data = {"breakpoint_idx": breakpoint_idx, "paper_count_star": 39.0, "gate_passed": True}
    json_path = tmp_path / "experiment_results.json"
    json_path.write_text(json.dumps(data))
    return json_path


def test_load_residual_cov_shape(tmp_path):
    csv_path = _make_mock_csv(tmp_path)
    paper_counts, residual_cov = load_residual_cov(csv_path)
    assert len(paper_counts) == 111
    assert len(residual_cov) == 111
    assert paper_counts.dtype == int


def test_load_residual_cov_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_residual_cov(tmp_path / "nonexistent.csv")


def test_load_residual_cov_wrong_n(tmp_path):
    csv_path = _make_mock_csv(tmp_path, n=50)
    with pytest.raises(ValueError):
        load_residual_cov(csv_path)


def test_load_paper_count_star_idx_from_json(tmp_path):
    csv_path = _make_mock_csv(tmp_path)
    paper_counts, residual_cov = load_residual_cov(csv_path)
    json_path = _make_mock_json(tmp_path, breakpoint_idx=34)
    idx = load_paper_count_star_idx(json_path, paper_counts, residual_cov)
    assert idx == 34


def test_compute_global_variance():
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    var, mean = compute_global_variance(arr)
    assert abs(var - np.var(arr, ddof=1)) < 1e-10
    assert abs(mean - np.mean(arr)) < 1e-10


def test_split_segments_correct():
    arr = np.arange(10, dtype=float)
    pre, post = split_segments(arr, 4)
    assert len(pre) == 4
    assert len(post) == 6


def test_split_segments_too_small():
    arr = np.arange(10, dtype=float)
    with pytest.raises(ValueError, match="< 3"):
        split_segments(arr, 2)


def test_run_f_test_ratio_one():
    # pre with same distribution as global => ratio ~ 1, p ~ 0.5
    rng = np.random.default_rng(0)
    full = rng.normal(0, 1, 111)
    global_var = float(np.var(full, ddof=1))
    pre = full[:34]
    F, p, ratio = run_f_test(pre, global_var, 111)
    assert F > 0
    assert 0.0 <= p <= 1.0
    assert abs(ratio - F) < 1e-10


def test_run_brown_forsythe():
    rng = np.random.default_rng(1)
    pre = rng.normal(0, 1, 34)
    post = rng.normal(0, 1, 77)
    bf_stat, bf_p = run_brown_forsythe(pre, post)
    assert bf_stat >= 0
    assert 0.0 <= bf_p <= 1.0


def test_analyze_returns_all_fields(tmp_path):
    csv_path = _make_mock_csv(tmp_path)
    _, residual_cov = load_residual_cov(csv_path)
    results = analyze(residual_cov, 34)
    required = [
        "n_pre", "n_post", "global_variance", "global_mean",
        "pre_variance", "pre_mean", "post_variance", "post_mean",
        "F_stat", "p_one_tailed", "variance_ratio_pre_global",
        "pre_mean_positive", "bf_stat", "bf_p", "gate_passed"
    ]
    for key in required:
        assert key in results, f"Missing key: {key}"


def test_verify_mechanism_activated_indicators(tmp_path):
    csv_path = _make_mock_csv(tmp_path)
    _, residual_cov = load_residual_cov(csv_path)
    results = analyze(residual_cov, 34)
    activated, indicators = verify_mechanism_activated(results)
    assert isinstance(activated, bool)
    for key in ["pre_var_computed", "global_var_computed", "ratio_above_one", "f_stat_computed", "p_value_computed"]:
        assert key in indicators
