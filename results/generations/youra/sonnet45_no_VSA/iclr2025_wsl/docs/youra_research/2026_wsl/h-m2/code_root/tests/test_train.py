"""Tests for training infrastructure."""

import sys
from pathlib import Path
import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from train import WidthScalingTrainer
from models.mlp_encoder import MLPWeightEncoder
from config import CONFIG


def test_trainer_initialization():
    """Test trainer initialization."""
    trainer = WidthScalingTrainer(CONFIG)
    assert trainer.config == CONFIG
    assert trainer.checkpoint_dir.exists()


def test_check_loss_matching():
    """Test loss matching validation."""
    trainer = WidthScalingTrainer(CONFIG)

    # Test matching losses
    assert trainer.check_loss_matching(1.0, 1.005, tolerance=0.01) == True

    # Test non-matching losses
    assert trainer.check_loss_matching(1.0, 1.05, tolerance=0.01) == False


def test_train_single_model():
    """Test training a single model (small scale)."""
    trainer = WidthScalingTrainer(CONFIG)

    # Create small dummy dataset
    data = torch.randn(100, 2864)
    labels = torch.zeros(100)
    train_loader = DataLoader(TensorDataset(data, labels), batch_size=16)
    val_loader = DataLoader(TensorDataset(data[:20], labels[:20]), batch_size=16)

    # Create small model
    model = MLPWeightEncoder(
        input_dim=2864,
        hidden_dims=[128],
        output_dim=32
    )

    # Train for few epochs
    result = trainer.train_single_model(
        model,
        train_loader,
        val_loader,
        epochs=2,
        model_name="test_model"
    )

    # Check results
    assert 'train_loss' in result
    assert 'val_loss' in result
    assert 'epoch_losses' in result
    assert 'checkpoint_path' in result
    assert len(result['epoch_losses']) == 2
