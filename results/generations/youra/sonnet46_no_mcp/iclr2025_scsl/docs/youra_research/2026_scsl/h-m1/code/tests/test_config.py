import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_config, TrainConfig, GDRConfig, ExperimentConfig


def test_load_config():
    cfg = load_config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "waterbirds.yaml"))
    assert isinstance(cfg, ExperimentConfig)
    assert isinstance(cfg.train, TrainConfig)
    assert isinstance(cfg.gdr, GDRConfig)


def test_train_config_fields():
    cfg = load_config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "waterbirds.yaml"))
    assert cfg.train.batch_size == 64
    assert cfg.train.seeds == [1, 2, 3]
    assert cfg.train.epochs == 30


def test_gdr_config_defaults():
    cfg = load_config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "waterbirds.yaml"))
    assert cfg.gdr.early_window_epochs == [2, 4, 6]
    assert cfg.gdr.p_threshold == 0.05
    assert cfg.gdr.min_seeds_pass == 2
