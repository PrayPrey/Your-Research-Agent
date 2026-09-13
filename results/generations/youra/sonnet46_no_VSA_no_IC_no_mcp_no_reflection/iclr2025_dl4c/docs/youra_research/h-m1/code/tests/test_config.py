import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import GRPOConfig, load_config, save_config
import tempfile


def test_default_config():
    cfg = GRPOConfig()
    assert cfg.model_name == "deepseek-ai/deepseek-coder-6.7b-instruct"
    assert cfg.min_test_cases == 5
    assert cfg.group_size == 8
    assert cfg.train_steps == 500
    assert cfg.checkpoint_step == 200
    assert cfg.seed == 42
    assert cfg.reward_mode == "binary"


def test_save_load_config():
    cfg = GRPOConfig(train_steps=100, reward_mode="ratio")
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        path = f.name
    try:
        save_config(cfg, path)
        loaded = load_config(path)
        assert loaded.train_steps == 100
        assert loaded.reward_mode == "ratio"
    finally:
        os.unlink(path)


if __name__ == "__main__":
    test_default_config()
    test_save_load_config()
    print("config tests passed")
