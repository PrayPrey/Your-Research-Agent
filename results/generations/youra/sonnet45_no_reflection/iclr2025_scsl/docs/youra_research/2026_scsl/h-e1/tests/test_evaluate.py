"""Tests for evaluation module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

import torch
from transformers import GPT2Config
from model import BaselineGPT2
from evaluate import MetricsEvaluator


def test_metrics_evaluator_initialization():
    """Test MetricsEvaluator can be initialized."""
    config = GPT2Config(n_embd=128, n_layer=2, n_head=2)
    model = BaselineGPT2(config)

    evaluator = MetricsEvaluator(model, val_loader=None, device="cpu")
    assert evaluator.model == model
    assert evaluator.device.type == "cpu"


def test_layer_variance_computation():
    """Test layer variance computation."""
    config = GPT2Config(n_embd=128, n_layer=2, n_head=2)
    model = BaselineGPT2(config)
    evaluator = MetricsEvaluator(model, val_loader=None, device="cpu")

    stable_ranks = {'layer_0': 10.0, 'layer_1': 12.0, 'layer_2': 11.0}
    variance = evaluator.compute_layer_variance(stable_ranks)
    assert variance >= 0.0
    assert isinstance(variance, float)


def test_layer_variance_empty():
    """Test layer variance with empty input."""
    config = GPT2Config(n_embd=128, n_layer=2, n_head=2)
    model = BaselineGPT2(config)
    evaluator = MetricsEvaluator(model, val_loader=None, device="cpu")

    variance = evaluator.compute_layer_variance({})
    assert variance == 0.0
