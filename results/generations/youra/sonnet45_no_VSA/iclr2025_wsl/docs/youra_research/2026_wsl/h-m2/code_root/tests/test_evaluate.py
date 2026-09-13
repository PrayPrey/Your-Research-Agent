"""Tests for evaluation pipeline."""

import sys
from pathlib import Path
import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from evaluate import WidthScalingEvaluator
from models.mlp_encoder import MLPWeightEncoder
from config import CONFIG


def test_evaluator_initialization():
    """Test evaluator initialization."""
    evaluator = WidthScalingEvaluator(CONFIG)
    assert evaluator.config == CONFIG
    assert evaluator.results_dir.exists()


def test_check_monotonicity():
    """Test monotonicity checking."""
    evaluator = WidthScalingEvaluator(CONFIG)

    # Strictly increasing
    assert evaluator.check_monotonicity([1.0, 2.0, 3.0, 4.0, 5.0]) == True

    # Not increasing
    assert evaluator.check_monotonicity([1.0, 3.0, 2.0, 4.0, 5.0]) == True  # 1 violation allowed

    # Multiple violations
    assert evaluator.check_monotonicity([5.0, 4.0, 3.0, 2.0, 1.0]) == False


def test_compute_test_error():
    """Test test error computation."""
    evaluator = WidthScalingEvaluator(CONFIG)

    # Create small model and dataset
    model = MLPWeightEncoder(input_dim=2864, hidden_dims=[128], output_dim=32)
    data = torch.randn(50, 2864)
    labels = torch.zeros(50)
    test_loader = DataLoader(TensorDataset(data, labels), batch_size=16)

    # Compute test error
    error = evaluator.compute_test_error(model, test_loader)

    assert isinstance(error, float)
    assert error >= 0.0
