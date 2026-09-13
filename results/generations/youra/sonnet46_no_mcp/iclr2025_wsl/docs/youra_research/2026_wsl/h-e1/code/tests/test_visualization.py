"""Tests for visualization.py (task-008)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from visualization import generate_all_figures
from config import ExperimentConfig


def _make_mock_data():
    distances = [
        {"decile": i % 10, "cosine_dist": 0.05 + 0.1 * (i % 5), "is_orbit_candidate": bool(i % 2)}
        for i in range(50)
    ]
    pairs = []
    for i in range(50):
        m1 = {"state_dict": {"weights_flat": torch.ones(10)}, "test_accuracy": 0.9, "_flat_weights": True}
        m2 = {"state_dict": {"weights_flat": torch.randn(10)}, "test_accuracy": 0.91, "_flat_weights": True}
        pairs.append((m1, m2, i % 10))
    orbit_proportion = 0.5
    per_decile = {d: 0.5 for d in range(10)}
    return distances, pairs, orbit_proportion, per_decile


def test_generate_all_figures(tmp_path):
    distances, pairs, orbit_proportion, per_decile = _make_mock_data()
    cfg = ExperimentConfig(
        data_dir=tmp_path / "data",
        results_dir=tmp_path / "results",
        figures_dir=tmp_path / "figures",
    )
    generate_all_figures(distances, pairs, orbit_proportion, per_decile, cfg)

    # 4 PNG files must exist and be non-empty
    expected = [
        "gate_metrics.png",
        "cosine_dist_histogram.png",
        "acc_vs_distance.png",
        "per_decile_proportion.png",
    ]
    for fname in expected:
        fpath = cfg.figures_dir / fname
        assert fpath.exists(), f"Missing figure: {fname}"
        assert fpath.stat().st_size > 0, f"Empty figure: {fname}"
