import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
from config import load_config
from stats_analyzer import StatsAnalyzer


def _make_labels_with_known_variance():
    """Create labels where different groups clearly have different rates."""
    labels = {}
    # Group 1: 100% contaminated
    labels["high_task"] = [1] * 100
    # Group 2: 0% contaminated
    labels["low_task"] = [0] * 100
    # Add more groups with varying rates for Kruskal-Wallis
    for i in range(10):
        rate = i / 10
        n = 50
        c = int(rate * n)
        labels[f"task_{i}"] = [1] * c + [0] * (n - c)
    return labels


def test_kruskal_wallis_with_known_p_less_than_005():
    cfg = load_config()
    analyzer = StatsAnalyzer(cfg)
    labels = _make_labels_with_known_variance()
    result = analyzer.kruskal_wallis(labels)
    assert result["p_value"] < 0.05
    assert result["gate_pass"] is True
    assert "kruskal_stat" in result
    assert "max_pair_diff" in result


def test_assert_gate_raises_when_p_above_threshold():
    cfg = load_config()
    analyzer = StatsAnalyzer(cfg)
    with pytest.raises(AssertionError, match="Gate FAILED"):
        analyzer.assert_gate(0.1)


def test_assert_gate_passes_when_p_below_threshold():
    cfg = load_config()
    analyzer = StatsAnalyzer(cfg)
    analyzer.assert_gate(0.001)  # should not raise


def test_compute_rates_correct_for_known_labels():
    cfg = load_config()
    analyzer = StatsAnalyzer(cfg)
    labels = {
        "task_a": [1, 1, 0, 0],  # rate = 0.5
        "task_b": [1, 1, 1, 1],  # rate = 1.0
        "task_c": [0, 0, 0, 0],  # rate = 0.0
    }
    df = analyzer.compute_rates(labels)
    assert set(df.columns) >= {"subtask", "n_items", "n_contaminated", "rate"}
    row_a = df[df["subtask"] == "task_a"].iloc[0]
    assert row_a["n_items"] == 4
    assert row_a["n_contaminated"] == 2
    assert abs(row_a["rate"] - 0.5) < 1e-9

    row_b = df[df["subtask"] == "task_b"].iloc[0]
    assert abs(row_b["rate"] - 1.0) < 1e-9

    row_c = df[df["subtask"] == "task_c"].iloc[0]
    assert abs(row_c["rate"] - 0.0) < 1e-9
