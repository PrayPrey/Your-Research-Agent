"""Tests for config.py — ExperimentConfig loading."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import yaml


def test_config_import():
    from config import (TrainConfig, ProbeConfig, GateConfig,
                        DatasetPathConfig, ExperimentConfig, load_config)
    assert TrainConfig is not None
    assert ExperimentConfig is not None


def test_load_config_waterbirds(tmp_path):
    from config import load_config, ExperimentConfig
    cfg_data = {
        "train": {
            "dataset": "waterbirds",
            "data_root": "./data/waterbirds",
            "checkpoint_dir": "./checkpoints/waterbirds",
            "epochs": 300,
        },
        "probe": {"C": 1.0, "max_iter": 1000},
        "gate": {"min_window_fraction": 0.10, "p_threshold": 0.05},
        "paths": {"waterbirds_root": "./data/waterbirds"},
        "results_dir": "./results/h-e1",
    }
    cfg_file = tmp_path / "wb.yaml"
    with open(str(cfg_file), "w") as f:
        yaml.dump(cfg_data, f)

    cfg = load_config(str(cfg_file))
    assert isinstance(cfg, ExperimentConfig)
    assert cfg.train.dataset == "waterbirds"
    assert cfg.train.epochs == 300
    assert cfg.probe.C == 1.0
    assert cfg.gate.min_window_fraction == 0.10


def test_train_config_defaults():
    from config import TrainConfig
    cfg = TrainConfig(
        dataset="waterbirds",
        data_root="./data",
        checkpoint_dir="./ckpts",
        epochs=300,
    )
    assert cfg.checkpoint_interval == 2
    assert cfg.batch_size == 128
    assert cfg.lr == 1e-3
    assert cfg.momentum == 0.9
    assert cfg.weight_decay == 1e-4
    assert cfg.seeds == [1, 2, 3, 4, 5]


def test_probe_config_defaults():
    from config import ProbeConfig
    cfg = ProbeConfig()
    assert cfg.C == 1.0
    assert cfg.max_iter == 1000
    assert cfg.solver == "lbfgs"
    assert cfg.random_state == 42


def test_gate_config_defaults():
    from config import GateConfig
    cfg = GateConfig()
    assert cfg.min_window_fraction == 0.10
    assert cfg.p_threshold == 0.05
    assert cfg.min_seeds == 3
