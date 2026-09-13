import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import ExperimentConfig, load_config


def test_default_values():
    cfg = ExperimentConfig()
    assert cfg.delta_acc_threshold == 0.001
    assert cfg.perm_seeds == list(range(10))
    assert cfg.n_permutations == 10
    assert cfg.sample_seed == 42


def test_load_config_returns_config():
    cfg = load_config()
    assert isinstance(cfg, ExperimentConfig)
    assert cfg.delta_acc_threshold == 0.001


def test_perm_seeds_length():
    cfg = ExperimentConfig()
    assert len(cfg.perm_seeds) == 10
