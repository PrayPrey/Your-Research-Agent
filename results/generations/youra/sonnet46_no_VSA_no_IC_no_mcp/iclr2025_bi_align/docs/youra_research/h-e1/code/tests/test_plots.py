import pandas as pd
import pytest
from pathlib import Path
from src.visualization.plots import plot_dual_axis, plot_comparison


def _make_df(n=8):
    return pd.DataFrame({
        "kl_budget": [float(i) for i in range(n)],
        "rm_score": [i * 0.3 for i in range(n)],
        "gold_preference": [0.5 + i * 0.02 for i in range(n)],
    })


def test_dual_axis_saves_file(tmp_path):
    df = _make_df()
    path = plot_dual_axis(df, "TestDataset", str(tmp_path))
    assert Path(path).exists()
    assert "dual_axis_testdataset.png" in path


def test_comparison_saves_file(tmp_path):
    df = _make_df()
    results = [{"passed": True, "n_kl_levels": 8}]
    path = plot_comparison(results, [df], ["TestDataset"], str(tmp_path))
    assert Path(path).exists()
    assert "comparison_both_datasets.png" in path


def test_dual_axis_uses_correct_columns(tmp_path):
    df = _make_df()
    # No KeyError means columns are accessed correctly
    path = plot_dual_axis(df, "DS", str(tmp_path))
    assert Path(path).exists()
