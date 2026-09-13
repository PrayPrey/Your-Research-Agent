"""Tests for config.py spec compliance."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG, CONDITIONS


def test_config_has_required_keys():
    required = [
        "model_id", "num_generations", "max_new_tokens", "temperature",
        "learning_rate", "per_device_train_batch_size", "gradient_accumulation_steps",
        "max_steps", "save_steps", "seed", "curriculum_step",
        "output_dir", "log_dir", "results_dir", "figures_dir",
        "reward_timeout", "reward_epsilon",
    ]
    for key in required:
        assert key in CONFIG, f"Missing key: {key}"


def test_config_values():
    assert CONFIG["num_generations"] == 8
    assert CONFIG["max_steps"] == 5000
    assert CONFIG["curriculum_step"] == 2500
    assert CONFIG["save_steps"] == 500
    assert CONFIG["seed"] == 42
    assert CONFIG["learning_rate"] == 1e-6
    assert CONFIG["per_device_train_batch_size"] == 1
    assert CONFIG["gradient_accumulation_steps"] == 8


def test_conditions():
    assert CONDITIONS == ["curriculum", "uniform", "easy_only", "hard_only"]
    assert len(CONDITIONS) == 4
