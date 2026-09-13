import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from run_experiment import run


def test_run_accepts_parameters(tmp_path):
    # Just verify function is callable with expected signature
    import inspect
    sig = inspect.signature(run)
    params = list(sig.parameters.keys())
    assert "config_path" in params
    assert "device" in params


def test_run_returns_dict_keys(tmp_path):
    # Write a minimal smoke config
    import yaml
    smoke_cfg = {
        "train": {
            "data_root": "/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scsl/docs/youra_research/20260504_scsl/.data_cache/datasets/waterbirds",
            "checkpoint_dir": str(tmp_path / "checkpoints"),
            "max_epochs": 2,
            "checkpoint_epochs": [1, 2],
            "batch_size": 64,
            "lr": 1e-3,
            "momentum": 0.9,
            "weight_decay": 1e-4,
            "seeds": [1],
            "num_workers": 0,
        },
        "dfr": {"C": 1.0, "max_iter": 100, "class_weight": "balanced",
                "solver": "lbfgs", "dfr_seed": 42},
        "analysis": {"t_star_mean": 2.0, "pearson_r_threshold": 0.7, "conditions": [1, 2]},
        "paths": {
            "results_dir": str(tmp_path / "results"),
            "figures_dir": str(tmp_path / "figures"),
            "checkpoint_dir": str(tmp_path / "checkpoints"),
        },
    }
    config_path = str(tmp_path / "smoke.yaml")
    with open(config_path, "w") as f:
        yaml.dump(smoke_cfg, f)

    result = run(config_path, "cpu")
    assert "results_per_seed" in result
    assert "aggregated" in result
    assert "gate" in result
