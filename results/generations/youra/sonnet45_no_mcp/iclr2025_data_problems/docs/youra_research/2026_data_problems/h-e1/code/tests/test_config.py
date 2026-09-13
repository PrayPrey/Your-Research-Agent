"""
Tests for Configuration Module
Verifies all configuration values are properly defined.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    DIVERSITY_SCORES, CONDITIONS, MODEL_CONFIGS,
    TRAINING_CONFIG, CURRICULUM_CONFIG, EXPERIMENT_MATRIX,
    CHECKPOINT_PERCENTAGES, SEEDS
)


def test_diversity_scores():
    """Test diversity scores are defined for all domains."""
    assert len(DIVERSITY_SCORES) == 6, "Should have 6 domains"

    expected_domains = ["Pile-CC", "StackExchange", "Wikipedia", "ArXiv", "Github", "PubMed"]
    for domain in expected_domains:
        assert domain in DIVERSITY_SCORES, f"Missing domain: {domain}"

    # Check scores are in valid range [0, 1]
    for domain, score in DIVERSITY_SCORES.items():
        assert 0.0 <= score <= 1.0, f"{domain} score {score} not in [0, 1]"

    # Check diversity ranking (Pile-CC highest, PubMed lowest)
    assert DIVERSITY_SCORES["Pile-CC"] > DIVERSITY_SCORES["PubMed"]


def test_conditions():
    """Test experimental conditions are defined."""
    assert len(CONDITIONS) == 4, "Should have 4 conditions"
    expected = ["static", "diversity_ranked", "reversed", "shuffled"]
    assert all(c in CONDITIONS for c in expected)


def test_model_configs():
    """Test model configurations for both scales."""
    assert "1B" in MODEL_CONFIGS
    assert "7B" in MODEL_CONFIGS

    # Check 1B config
    config_1b = MODEL_CONFIGS["1B"]
    assert config_1b["n_layer"] == 24
    assert config_1b["n_embd"] == 1536
    assert config_1b["n_head"] == 16
    assert config_1b["vocab_size"] == 50257

    # Check 7B config
    config_7b = MODEL_CONFIGS["7B"]
    assert config_7b["n_layer"] == 32
    assert config_7b["n_embd"] == 4096
    assert config_7b["n_head"] == 32


def test_training_config():
    """Test training hyperparameters."""
    assert "1B" in TRAINING_CONFIG
    assert "7B" in TRAINING_CONFIG

    # Check 1B training config
    train_1b = TRAINING_CONFIG["1B"]
    assert train_1b["lr"] == 3e-4
    assert train_1b["total_steps"] == 100000
    assert train_1b["batch_size"] == 512

    # Check 7B training config
    train_7b = TRAINING_CONFIG["7B"]
    assert train_7b["lr"] == 1.5e-4
    assert train_7b["total_steps"] == 150000
    assert train_7b["batch_size"] == 1024


def test_curriculum_config():
    """Test curriculum parameters."""
    assert CURRICULUM_CONFIG["gaussian_width"] == 0.3
    assert CURRICULUM_CONFIG["min_weight"] == 0.05
    assert CURRICULUM_CONFIG["sequence_length"] == 2048


def test_checkpoint_percentages():
    """Test checkpoint schedule."""
    assert len(CHECKPOINT_PERCENTAGES) == 5
    assert CHECKPOINT_PERCENTAGES == [0.10, 0.25, 0.50, 0.75, 1.0]


def test_seeds():
    """Test random seeds."""
    assert len(SEEDS) == 5
    assert SEEDS == [42, 43, 44, 45, 46]


def test_experiment_matrix():
    """Test experiment matrix has correct size."""
    # 4 conditions × 2 scales × 5 seeds = 40 experiments
    assert len(EXPERIMENT_MATRIX) == 40

    # Check all combinations are present
    conditions_seen = set()
    scales_seen = set()
    seeds_seen = set()

    for exp in EXPERIMENT_MATRIX:
        conditions_seen.add(exp["condition"])
        scales_seen.add(exp["scale"])
        seeds_seen.add(exp["seed"])

    assert conditions_seen == {"static", "diversity_ranked", "reversed", "shuffled"}
    assert scales_seen == {"1B", "7B"}
    assert seeds_seen == {42, 43, 44, 45, 46}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
