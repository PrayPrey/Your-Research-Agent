"""Tests for configuration module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from config import (
    DataConfig, ModelConfig, RegularizationConfig, TrainingConfig,
    EvaluationConfig, ExperimentConfig,
    get_baseline_config, get_proposed_config, get_implicit_control_config
)


def test_data_config_defaults():
    """Test DataConfig has correct defaults."""
    config = DataConfig()
    assert config.dataset_name == "allenai/c4"
    assert config.subset == "en"
    assert config.tokenizer_name == "gpt2"
    assert config.seq_length == 512


def test_model_config_defaults():
    """Test ModelConfig has correct defaults."""
    config = ModelConfig()
    assert config.vocab_size == 50257
    assert config.n_layer == 12
    assert config.n_embd == 768
    assert config.n_head == 12


def test_experiment_config_post_init():
    """Test ExperimentConfig computes total_steps."""
    config = ExperimentConfig()
    assert config.total_steps > 0
    expected_steps = config.data.total_tokens // (
        config.data.batch_size *
        config.training.gradient_accumulation_steps *
        config.data.seq_length
    )
    assert config.total_steps == expected_steps


def test_baseline_config():
    """Test baseline config has lambda=0."""
    config = get_baseline_config()
    assert config.variant == "baseline"
    assert config.regularization.lambda_init == 0.0
    assert config.regularization.adaptive_tuning is False


def test_proposed_config():
    """Test proposed config has regularization enabled."""
    config = get_proposed_config()
    assert config.variant == "proposed"
    assert config.regularization.lambda_init > 0
    assert config.regularization.adaptive_tuning is True


def test_implicit_control_config():
    """Test implicit control config."""
    config = get_implicit_control_config()
    assert config.variant == "implicit_control"
    assert config.regularization.lambda_init == 0.0
