import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import json
import yaml

SMOKE_TEST_CONFIG = {
    "train": {
        "data_root": "/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scsl/docs/youra_research/20260504_scsl/.data_cache/datasets/waterbirds",
        "checkpoint_dir": "./checkpoints_test",
        "max_epochs": 2,
        "checkpoint_epochs": [1, 2],
        "batch_size": 64,
        "lr": 1e-3,
        "momentum": 0.9,
        "weight_decay": 1e-4,
        "seeds": [1],
        "num_workers": 0,
    },
    "dfr": {
        "C": 1.0,
        "max_iter": 1000,
        "class_weight": "balanced",
        "solver": "lbfgs",
        "dfr_seed": 42,
    },
    "analysis": {
        "t_star_mean": 2.0,
        "pearson_r_threshold": 0.7,
        "conditions": [1, 2],
    },
    "paths": {
        "results_dir": "./results_test",
        "figures_dir": "./figures_test",
        "checkpoint_dir": "./checkpoints_test",
    },
}

EXPECTED_FEATURE_DIM = 2048
TIMEOUT_SECONDS = 300


@pytest.fixture
def smoke_config_path(tmp_path):
    path = str(tmp_path / "smoke.yaml")
    cfg = SMOKE_TEST_CONFIG.copy()
    cfg["train"]["checkpoint_dir"] = str(tmp_path / "checkpoints_test")
    cfg["paths"]["results_dir"] = str(tmp_path / "results_test")
    cfg["paths"]["figures_dir"] = str(tmp_path / "figures_test")
    cfg["paths"]["checkpoint_dir"] = str(tmp_path / "checkpoints_test")
    with open(path, "w") as f:
        yaml.dump(cfg, f)
    return path


def test_feature_dim(smoke_config_path):
    from run_experiment import run
    result = run(smoke_config_path, "cpu")
    seed = 1
    epoch = 1
    # Check first condition
    metrics = result["results_per_seed"][seed][epoch]
    assert metrics["feature_dim"] == EXPECTED_FEATURE_DIM


def test_dfr_wga_positive(smoke_config_path):
    from run_experiment import run
    result = run(smoke_config_path, "cpu")
    for seed, seed_data in result["results_per_seed"].items():
        for epoch, metrics in seed_data.items():
            assert metrics["dfr_wga"] >= 0.0


def test_results_json_created(smoke_config_path, tmp_path):
    from run_experiment import run
    result = run(smoke_config_path, "cpu")
    assert "json_path" in result
    assert os.path.exists(result["json_path"])
    with open(result["json_path"]) as f:
        data = json.load(f)
    assert "hypothesis_id" in data
    assert data["hypothesis_id"] == "h-m4"
