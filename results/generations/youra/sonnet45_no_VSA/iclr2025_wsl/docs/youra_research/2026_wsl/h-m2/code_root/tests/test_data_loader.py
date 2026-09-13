"""Tests for WeightSpaceDataLoader."""

import sys
from pathlib import Path
import pytest
import torch

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from data_loader import WeightSpaceDataLoader
from config import CONFIG


def test_data_loader_initialization():
    """Test that data loader initializes correctly."""
    loader = WeightSpaceDataLoader(CONFIG)
    assert loader.config == CONFIG
    assert loader.zoo_loader is not None
    assert loader.cache_dir.exists()


def test_state_dicts_to_mlp_vectors():
    """Test conversion of state dicts to MLP vectors."""
    loader = WeightSpaceDataLoader(CONFIG)

    # Create dummy state dicts
    state_dicts = [
        {
            'layer1.weight': torch.randn(10, 5),
            'layer1.bias': torch.randn(10),
            'layer2.weight': torch.randn(3, 10),
        },
        {
            'layer1.weight': torch.randn(10, 5),
            'layer1.bias': torch.randn(10),
            'layer2.weight': torch.randn(3, 10),
        }
    ]

    vectors = loader.state_dicts_to_mlp_vectors(state_dicts)

    # Check shape
    assert vectors.shape[0] == 2  # batch size
    expected_size = 10*5 + 10 + 3*10  # total params
    assert vectors.shape[1] == expected_size


def test_get_dataloaders():
    """Test dataloader creation."""
    loader = WeightSpaceDataLoader(CONFIG)
    dataloaders = loader.get_dataloaders()

    # Check structure
    assert 'mlp' in dataloaders
    assert 'nfn' in dataloaders
    assert 'train' in dataloaders['mlp']
    assert 'val' in dataloaders['mlp']
    assert 'test' in dataloaders['mlp']

    # Check batch iteration
    train_loader = dataloaders['mlp']['train']
    batch = next(iter(train_loader))
    assert len(batch) == 2  # data and labels
    assert batch[0].shape[0] <= CONFIG['batch_size']
