import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from config import ExperimentConfig, TrainConfig, DFRConfig, AnalysisConfig, PathConfig
from visualizer import Visualizer


@pytest.fixture
def cfg(tmp_path):
    return ExperimentConfig(
        train=TrainConfig(),
        dfr=DFRConfig(),
        analysis=AnalysisConfig(conditions=[1, 2, 10, 20, 30]),
        paths=PathConfig(
            results_dir=str(tmp_path / "results"),
            figures_dir=str(tmp_path / "figures"),
            checkpoint_dir=str(tmp_path / "checkpoints"),
        ),
    )


@pytest.fixture
def synthetic_data():
    seeds = [1, 2, 3]
    epochs = [1, 2, 10, 20, 30]
    results_per_seed = {}
    for seed in seeds:
        results_per_seed[seed] = {}
        for i, e in enumerate(epochs):
            results_per_seed[seed][e] = {
                "erm_wga": 0.5,
                "dfr_wga": 0.5 + 0.01 * i,
                "wga_improvement": 0.01 * i,
            }
    aggregated = {
        e: {
            "mean_erm_wga": 0.5,
            "mean_dfr_wga": 0.5 + 0.01 * i,
            "mean_wga_improvement": 0.01 * i,
            "std_wga_improvement": 0.001,
        }
        for i, e in enumerate(epochs)
    }
    corr = {
        "pearson_r": 0.95,
        "pearson_p_onetailed": 0.01,
        "epochs_past_tstar": [-1, 0, 8, 18, 28],
        "improvements": [0.0, 0.01, 0.02, 0.03, 0.04],
    }
    return results_per_seed, aggregated, corr


def test_save_all_returns_4_paths(cfg, synthetic_data):
    viz = Visualizer(cfg)
    results_per_seed, aggregated, corr = synthetic_data
    paths = viz.save_all(results_per_seed, aggregated, corr, t_star=2.0)
    assert len(paths) == 4


def test_save_all_files_exist(cfg, synthetic_data):
    viz = Visualizer(cfg)
    results_per_seed, aggregated, corr = synthetic_data
    paths = viz.save_all(results_per_seed, aggregated, corr, t_star=2.0)
    for p in paths:
        assert os.path.exists(p), f"Figure not created: {p}"


def test_plot_functions_no_error(cfg, synthetic_data):
    viz = Visualizer(cfg)
    results_per_seed, aggregated, corr = synthetic_data
    path = viz.plot_gate_metrics(aggregated, 0.95, 2.0)
    assert os.path.exists(path)
