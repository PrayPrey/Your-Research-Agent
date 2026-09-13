"""
Test suite for train.py, evaluate.py, visualize.py, and main.py
Basic API and integration tests for Tasks A-6, A-7, A-8
"""
import pytest
import torch
import numpy as np
from unittest.mock import Mock, MagicMock


def test_trainer_exists():
    """Test Trainer class exists with required methods"""
    from train import Trainer
    assert hasattr(Trainer, '__init__')
    assert hasattr(Trainer, 'train_epoch')
    assert hasattr(Trainer, 'validate')


def test_trainer_init():
    """Test Trainer can be initialized"""
    from train import Trainer
    from config import TrainingConfig

    # Mock components
    model = Mock()
    train_loader = Mock()
    val_loader = Mock()
    config = TrainingConfig()

    trainer = Trainer(model, train_loader, val_loader, config, device='cpu')
    assert trainer is not None
    assert trainer.model == model
    assert trainer.config == config


def test_setup_optimizer():
    """Test optimizer setup"""
    from train import setup_optimizer
    from config import TrainingConfig

    model = Mock()
    model.parameters = Mock(return_value=[torch.nn.Parameter(torch.randn(10))])
    config = TrainingConfig()

    optimizer = setup_optimizer(model, config)
    assert optimizer is not None


def test_setup_scheduler():
    """Test scheduler setup"""
    from train import setup_scheduler
    from config import TrainingConfig
    from torch.optim import AdamW

    model = Mock()
    model.parameters = Mock(return_value=[torch.nn.Parameter(torch.randn(10))])
    config = TrainingConfig()

    optimizer = AdamW(model.parameters(), lr=config.learning_rate)
    scheduler = setup_scheduler(optimizer, config)
    assert scheduler is not None


def test_evaluator_exists():
    """Test Evaluator class exists"""
    from evaluate import Evaluator
    assert hasattr(Evaluator, '__init__')
    assert hasattr(Evaluator, 'evaluate_task')
    assert hasattr(Evaluator, 'compute_super_additive_gain')


def test_evaluator_init():
    """Test Evaluator initialization"""
    from evaluate import Evaluator
    from config import DataConfig

    model = Mock()
    config = DataConfig()

    evaluator = Evaluator(model, config, device='cpu')
    assert evaluator is not None
    assert evaluator.model == model


def test_compute_super_additive_gain():
    """Test super-additive gain computation"""
    from evaluate import Evaluator
    from config import DataConfig

    evaluator = Evaluator(None, DataConfig())

    baseline = 0.75
    lora_only = 0.80
    moe_only = 0.78
    proposed = 0.85

    gain = evaluator.compute_super_additive_gain(baseline, lora_only, moe_only, proposed)

    # Expected: 0.85 - (0.80 + 0.78 - 0.75) = 0.85 - 0.83 = 0.02
    assert abs(gain - 0.02) < 0.001


def test_compute_expert_utilization_entropy():
    """Test expert utilization entropy"""
    from evaluate import compute_expert_utilization_entropy

    # Uniform distribution (high entropy)
    expert_probs = torch.ones(100, 8) / 8
    entropy = compute_expert_utilization_entropy(expert_probs)
    assert entropy > 0


def test_compute_routing_alignment():
    """Test routing alignment computation"""
    from evaluate import compute_routing_alignment

    # Identical distributions (high correlation)
    lora_probs = torch.rand(100, 8)
    moe_probs = lora_probs.clone()

    correlation = compute_routing_alignment(lora_probs, moe_probs)
    assert abs(correlation - 1.0) < 0.1  # Should be close to 1


def test_plot_gate_metrics():
    """Test gate metrics plotting function exists"""
    from visualize import plot_gate_metrics
    assert callable(plot_gate_metrics)


def test_plot_training_curves():
    """Test training curves plotting function exists"""
    from visualize import plot_training_curves
    assert callable(plot_training_curves)


def test_plot_expert_utilization():
    """Test expert utilization plotting function exists"""
    from visualize import plot_expert_utilization
    assert callable(plot_expert_utilization)


def test_generate_all_figures():
    """Test generate_all_figures function exists"""
    from visualize import generate_all_figures
    assert callable(generate_all_figures)


def test_main_functions_exist():
    """Test main.py functions exist"""
    from main import run_baseline_experiment, run_proposed_experiment, run_comparison
    assert callable(run_baseline_experiment)
    assert callable(run_proposed_experiment)
    assert callable(run_comparison)


def test_generate_validation_report():
    """Test validation report generation"""
    from main import generate_validation_report

    results = {
        'baseline_acc': 0.75,
        'proposed_acc': 0.77,
        'gain': 0.02,
        'gate_satisfied': True,
        'metrics_history': {'loss': [1.0, 0.8, 0.6]}
    }

    # Should not raise error
    generate_validation_report(results, '/tmp/test_validation.md')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
