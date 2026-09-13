"""
Test suite for baseline.py and proposed.py - Basic API tests
"""
import pytest
import torch
from config import ModelConfig


def test_baseline_model_exists():
    """Test BaselineModel class exists"""
    from models.baseline import BaselineModel
    assert hasattr(BaselineModel, '__init__')
    assert hasattr(BaselineModel, 'forward')


def test_baseline_model_init():
    """Test BaselineModel can be initialized"""
    from models.baseline import BaselineModel
    config = ModelConfig()
    model = BaselineModel(config)
    assert model is not None


def test_proposed_model_exists():
    """Test ProposedModel class exists"""
    from models.proposed import ProposedModel
    assert hasattr(ProposedModel, '__init__')
    assert hasattr(ProposedModel, 'forward')


def test_proposed_model_init():
    """Test ProposedModel can be initialized"""
    from models.proposed import ProposedModel
    config = ModelConfig()
    model = ProposedModel(config)
    assert model is not None
