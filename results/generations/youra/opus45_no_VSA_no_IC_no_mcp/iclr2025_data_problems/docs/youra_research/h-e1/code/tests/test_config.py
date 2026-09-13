"""Tests for configuration module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    MODEL_CONFIG,
    TRAIN_CONFIG,
    SWEEP_CONFIGS,
    CurationConfig,
    DEDUP_MINHASH_PARAMS,
)


def test_model_config():
    assert MODEL_CONFIG["vocab_size"] == 50257
    assert MODEL_CONFIG["n_layer"] == 12
    assert MODEL_CONFIG["n_head"] == 12
    assert MODEL_CONFIG["n_embd"] == 768


def test_train_config():
    assert TRAIN_CONFIG["total_tokens"] == 10_000_000_000
    assert TRAIN_CONFIG["batch_size"] == 512
    assert TRAIN_CONFIG["seq_len"] == 1024
    tokens_per_step = TRAIN_CONFIG["batch_size"] * TRAIN_CONFIG["seq_len"]
    expected_steps = TRAIN_CONFIG["total_tokens"] // tokens_per_step
    assert abs(TRAIN_CONFIG["max_steps"] - expected_steps) <= 1


def test_sweep_configs():
    assert len(SWEEP_CONFIGS) == 15
    config_ids = [c.config_id for c in SWEEP_CONFIGS]
    assert "C0" in config_ids
    assert "C9" in config_ids
    assert "D0" in config_ids
    assert "D4" in config_ids

    c0 = next(c for c in SWEEP_CONFIGS if c.config_id == "C0")
    assert c0.perplexity_pct is None
    assert c0.dedup == "none"

    d4 = next(c for c in SWEEP_CONFIGS if c.config_id == "D4")
    assert d4.perplexity_pct == 50
    assert d4.dedup == "exact_plus_fuzzy"


def test_dedup_params():
    assert "fuzzy_0.7" in DEDUP_MINHASH_PARAMS
    assert "exact" in DEDUP_MINHASH_PARAMS
    assert DEDUP_MINHASH_PARAMS["exact"]["exact"] is True
    assert DEDUP_MINHASH_PARAMS["fuzzy_0.7"]["jaccard_threshold"] == 0.7


if __name__ == "__main__":
    test_model_config()
    test_train_config()
    test_sweep_configs()
    test_dedup_params()
    print("All config tests passed!")
