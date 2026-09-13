"""
Integration tests for H-E1 implementation
Tests all components work together
"""

import pytest
import torch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_config_import():
    """Test configuration imports"""
    from config.config import CONFIG, VIZ_CONFIG, SMOKE_TEST_CONFIG
    assert 'seed' in CONFIG
    assert 'data_dir' in CONFIG
    assert 'num_eigenthings' in CONFIG
    assert 'fig_alignment' in VIZ_CONFIG


def test_model_creation():
    """Test ResNet-50 model creation"""
    from models.model import get_resnet50
    model = get_resnet50(num_classes=2, pretrained=False)
    assert model is not None
    assert hasattr(model, 'fc')
    assert model.fc.out_features == 2


def test_group_dro_loss():
    """Test GroupDRO loss computation"""
    from models.model import GroupDROLoss

    criterion = GroupDROLoss(num_groups=4)

    # Dummy data
    logits = torch.randn(8, 2)
    labels = torch.randint(0, 2, (8,))
    groups = torch.randint(0, 4, (8,))

    loss = criterion(logits, labels, groups)
    assert loss.item() > 0


def test_hessian_functions_exist():
    """Test Hessian analysis functions exist"""
    from analysis import hessian_analysis

    assert hasattr(hessian_analysis, 'compute_hessian_spectrum')
    assert hasattr(hessian_analysis, 'fit_marchenko_pastur')
    assert hasattr(hessian_analysis, 'compute_minority_gradient')
    assert hasattr(hessian_analysis, 'compute_alignment')


def test_evaluation_functions():
    """Test evaluation functions"""
    from eval.evaluate import compute_worst_group_accuracy, evaluate_alignment

    group_accs = [80.0, 60.0, 70.0, 85.0]
    worst = compute_worst_group_accuracy(group_accs)
    assert worst == 60.0

    result = evaluate_alignment(0.8, 0.3)
    assert result['difference'] == pytest.approx(0.5, rel=1e-5)


def test_visualization_functions_exist():
    """Test visualization functions exist"""
    from eval import visualize

    assert hasattr(visualize, 'plot_alignment_comparison')
    assert hasattr(visualize, 'plot_hessian_spectrum')
    assert hasattr(visualize, 'plot_training_curves')
    assert hasattr(visualize, 'plot_group_accuracy_heatmap')
    assert hasattr(visualize, 'generate_all_figures')


def test_setup_utilities():
    """Test setup utilities"""
    from utils.setup import set_seed

    set_seed(42)
    # After setting seed, random operations should be deterministic
    import random
    val1 = random.random()

    set_seed(42)
    val2 = random.random()

    assert val1 == val2


def test_marchenko_pastur_fitting():
    """Test MP fitting with synthetic data"""
    import numpy as np
    from analysis.hessian_analysis import fit_marchenko_pastur

    # Create synthetic eigenvalues
    eigenvalues = np.random.randn(100)
    eigenvalues = np.sort(eigenvalues)[::-1]  # Descending

    bulk_edge, sigma_sq, gamma = fit_marchenko_pastur(eigenvalues)

    assert bulk_edge > 0
    assert sigma_sq > 0
    assert 0 < gamma < 1


def test_alignment_computation():
    """Test alignment computation"""
    import numpy as np
    from analysis.hessian_analysis import compute_alignment

    # Create dummy data
    g_minority = torch.randn(1000)
    eigenvectors = np.random.randn(1000, 100)
    eigenvalues = np.sort(np.random.randn(100))[::-1]
    bulk_edge = eigenvalues[50]  # Middle value

    alignment = compute_alignment(g_minority, eigenvectors, eigenvalues, bulk_edge)

    assert 0 <= alignment <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
