"""Basic import smoke tests."""
import pytest


def test_data_imports():
    """Test data module imports."""
    from data import G4SATDataset, SATDataLoader, collate_sat_batch
    assert G4SATDataset is not None
    assert SATDataLoader is not None
    assert collate_sat_batch is not None


def test_model_imports():
    """Test model module imports."""
    from models import MLP, NeuroSAT
    assert MLP is not None
    assert NeuroSAT is not None


def test_train_imports():
    """Test train module imports."""
    from train import unsupervised_loss, train_epoch, validate_epoch, Trainer
    assert unsupervised_loss is not None
    assert train_epoch is not None
    assert validate_epoch is not None
    assert Trainer is not None


def test_metrics_imports():
    """Test metrics module imports."""
    from metrics import (
        compute_hamming_distance,
        compute_violation_entropy,
        compute_heterogeneity_metrics,
        HeterogeneityAnalyzer
    )
    assert compute_hamming_distance is not None
    assert compute_violation_entropy is not None
    assert compute_heterogeneity_metrics is not None
    assert HeterogeneityAnalyzer is not None


def test_visualization_imports():
    """Test visualization module imports."""
    from visualization import (
        plot_gate_comparison,
        plot_dn_distribution,
        plot_entropy_distribution,
        plot_dn_vs_entropy_scatter,
        plot_quartile_boxplot,
        generate_all_figures
    )
    assert plot_gate_comparison is not None
    assert plot_dn_distribution is not None
    assert plot_entropy_distribution is not None
    assert plot_dn_vs_entropy_scatter is not None
    assert plot_quartile_boxplot is not None
    assert generate_all_figures is not None
