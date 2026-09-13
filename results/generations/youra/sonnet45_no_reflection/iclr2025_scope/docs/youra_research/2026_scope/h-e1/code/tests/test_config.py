"""
Test suite for config.py - Specification compliance tests
Tests API signatures, YAML I/O, and all required fields from PRD
"""
import pytest
import yaml
import tempfile
import os
from pathlib import Path


def test_dataconfig_exists():
    """Test DataConfig class exists with required fields"""
    from config import DataConfig

    config = DataConfig()
    assert hasattr(config, 'glue_tasks')
    assert hasattr(config, 'superglue_tasks')
    assert hasattr(config, 'max_length')
    assert hasattr(config, 'batch_size')
    assert hasattr(config, 'num_workers')
    assert config.max_length == 512
    assert config.batch_size == 32


def test_modelconfig_exists():
    """Test ModelConfig class exists with required fields"""
    from config import ModelConfig

    config = ModelConfig()
    assert hasattr(config, 'model_name')
    assert hasattr(config, 'lora_rank')
    assert hasattr(config, 'lora_alpha')
    assert hasattr(config, 'lora_dropout')
    assert hasattr(config, 'num_lora_experts')
    assert hasattr(config, 'top_k')
    assert hasattr(config, 'target_modules')
    assert config.lora_rank in [8, 16]
    assert config.top_k == 2


def test_trainingconfig_exists():
    """Test TrainingConfig class exists with required fields"""
    from config import TrainingConfig

    config = TrainingConfig()
    assert hasattr(config, 'learning_rate')
    assert hasattr(config, 'weight_decay')
    assert hasattr(config, 'num_epochs')
    assert hasattr(config, 'gradient_accumulation_steps')
    assert hasattr(config, 'warmup_steps')
    assert hasattr(config, 'alignment_loss_weight')
    assert hasattr(config, 'aux_loss_weight')
    assert hasattr(config, 'seed')
    assert hasattr(config, 'mixed_precision')
    assert config.learning_rate == 3e-4
    assert config.seed == 42


def test_experimentconfig_exists():
    """Test ExperimentConfig class exists with required fields"""
    from config import ExperimentConfig, DataConfig, ModelConfig, TrainingConfig

    config = ExperimentConfig(
        data=DataConfig(),
        model=ModelConfig(),
        training=TrainingConfig(),
        output_dir='./output',
        checkpoint_dir='./checkpoints',
        figures_dir='./figures'
    )
    assert hasattr(config, 'data')
    assert hasattr(config, 'model')
    assert hasattr(config, 'training')
    assert hasattr(config, 'output_dir')
    assert hasattr(config, 'checkpoint_dir')
    assert hasattr(config, 'figures_dir')


def test_experimentconfig_from_yaml():
    """Test ExperimentConfig.from_yaml() method signature"""
    from config import ExperimentConfig

    # Create temp YAML file
    test_config = {
        'data': {
            'glue_tasks': ['cola', 'sst2'],
            'superglue_tasks': ['boolq'],
            'max_length': 512,
            'batch_size': 32,
            'num_workers': 4
        },
        'model': {
            'model_name': 'mistralai/Mixtral-8x7B-v0.1',
            'lora_rank': 8,
            'lora_alpha': 16,
            'lora_dropout': 0.05,
            'num_lora_experts': 8,
            'top_k': 2,
            'target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj']
        },
        'training': {
            'learning_rate': 3e-4,
            'weight_decay': 0.01,
            'num_epochs': 5,
            'gradient_accumulation_steps': 4,
            'warmup_steps': 500,
            'alignment_loss_weight': 0.01,
            'aux_loss_weight': 0.01,
            'seed': 42,
            'mixed_precision': 'bf16'
        },
        'output_dir': './outputs',
        'checkpoint_dir': './checkpoints',
        'figures_dir': './figures'
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(test_config, f)
        temp_path = f.name

    try:
        config = ExperimentConfig.from_yaml(temp_path)
        assert config.data.max_length == 512
        assert config.model.lora_rank == 8
        assert config.training.seed == 42
        assert config.output_dir == './outputs'
    finally:
        os.unlink(temp_path)


def test_experimentconfig_to_yaml():
    """Test ExperimentConfig.to_yaml() method signature"""
    from config import ExperimentConfig

    config = ExperimentConfig.get_default()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name

    try:
        config.to_yaml(temp_path)
        assert os.path.exists(temp_path)

        # Verify YAML is valid
        with open(temp_path, 'r') as f:
            loaded = yaml.safe_load(f)
        assert 'data' in loaded
        assert 'model' in loaded
        assert 'training' in loaded
    finally:
        os.unlink(temp_path)


def test_config_roundtrip():
    """Test config can be saved and loaded without data loss"""
    from config import ExperimentConfig

    config1 = ExperimentConfig.get_default()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name

    try:
        config1.to_yaml(temp_path)
        config2 = ExperimentConfig.from_yaml(temp_path)

        assert config2.data.max_length == config1.data.max_length
        assert config2.model.lora_rank == config1.model.lora_rank
        assert config2.training.seed == config1.training.seed
    finally:
        os.unlink(temp_path)
