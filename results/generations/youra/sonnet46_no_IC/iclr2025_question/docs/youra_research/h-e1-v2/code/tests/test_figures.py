"""Spec tests for A-7 figures incl. new plot_entropy_heatmap (task-008)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import visualize
from visualize import plot_entropy_heatmap

CELLS = [f"{m}/{d}" for m in ("llama2", "mistral", "llama3")
         for d in ("triviaqa", "truthfulqa")]


def _fake_cache_df(n=30):
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "example_id": range(n),
        "split": ["selection"] * (n // 2) + ["test"] * (n - n // 2),
        "label": [i % 2 for i in range(n)],
    })
    for i in range(1, 33):
        df[f"entropy_L{i}"] = rng.uniform(2, 9, n)
    return df


def test_entropy_heatmap_returns_valid_path(tmp_path, monkeypatch):
    monkeypatch.setattr(visualize, "FIGURES_DIR", str(tmp_path))
    p = plot_entropy_heatmap(_fake_cache_df(), "llama2", "triviaqa")
    assert isinstance(p, Path) and p.exists() and p.stat().st_size > 0
    assert p.name == "entropy_heatmap_llama2.png"


def test_entropy_heatmap_missing_selection_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(visualize, "FIGURES_DIR", str(tmp_path))
    df = _fake_cache_df()
    df["split"] = "pending"
    with pytest.raises(ValueError):
        plot_entropy_heatmap(df, "llama2", "triviaqa")


def test_all_five_figures_render_nonempty(tmp_path, monkeypatch):
    """FR-5.2..5.6: all 5 PNGs exist and are non-empty (synthetic data)."""
    monkeypatch.setattr(visualize, "FIGURES_DIR", str(tmp_path))
    rng = np.random.default_rng(1)
    gate_results, auroc_grids, retained = {}, {}, {}
    for c in CELLS:
        retained[c] = list(range(4, 32))
        auroc_grids[c] = rng.uniform(0.5, 0.7, (len(retained[c]), 3))
        gate_results[c] = {"best_auroc": 0.6, "gate_pass": True,
                           "best_layer": 20, "best_signal": "entropy",
                           "final_layer_entropy_auroc": 0.52,
                           "depth_beats_final": True}
    paths = [visualize.plot_gate_bar_chart(gate_results),
             visualize.plot_auroc_heatmap(auroc_grids, retained),
             visualize.plot_auroc_vs_depth(auroc_grids, retained),
             visualize.plot_degeneracy_report(retained),
             visualize.plot_entropy_heatmap(_fake_cache_df(), "llama2", "triviaqa")]
    assert len(paths) == 5
    for p in paths:
        assert Path(p).exists() and Path(p).stat().st_size > 0
