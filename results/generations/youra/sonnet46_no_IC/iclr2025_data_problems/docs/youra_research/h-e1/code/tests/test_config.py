"""Tests for config.py spec compliance."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ExperimentConfig, CONFIG


def test_config_instantiation():
    cfg = ExperimentConfig()
    assert cfg is not None


def test_factorial_axes():
    assert CONFIG.ppl_thresholds == [20, 35, 50]
    assert CONFIG.dedup_jaccard == [0.7, 0.9]
    assert CONFIG.corpora == ["dolma", "fineweb"]
    assert CONFIG.scales == [70, 160]
    assert CONFIG.seeds == [1, 2, 3]


def test_token_budget():
    assert CONFIG.total_tokens == 50_000_000_000
    assert CONFIG.train_steps == 25_000
    assert CONFIG.batch_size_tokens == 2_000_000


def test_minhash_params():
    assert 0.7 in CONFIG.minhash_params
    assert 0.9 in CONFIG.minhash_params
    assert CONFIG.minhash_params[0.7]["num_buckets"] == 20
    assert CONFIG.minhash_params[0.9]["num_buckets"] == 8


def test_pythia_configs():
    assert 70 in CONFIG.pythia_configs
    assert 160 in CONFIG.pythia_configs
    assert CONFIG.pythia_configs[70]["num_layers"] == 6
    assert CONFIG.pythia_configs[160]["num_layers"] == 12


def test_gate_thresholds():
    assert CONFIG.significance_threshold == 0.05
    assert CONFIG.effect_size_threshold == 0.15
