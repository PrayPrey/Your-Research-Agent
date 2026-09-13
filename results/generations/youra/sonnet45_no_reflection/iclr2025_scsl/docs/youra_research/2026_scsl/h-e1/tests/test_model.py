"""Tests for model module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

import torch
from transformers import GPT2Config
from model import BaselineGPT2, StableRankRegularizer, RegularizedGPT2


def test_baseline_gpt2_initialization():
    """Test BaselineGPT2 can be initialized."""
    config = GPT2Config(n_embd=128, n_layer=2, n_head=2)
    model = BaselineGPT2(config)
    assert model.config == config
    assert model.model is not None


def test_baseline_gpt2_forward():
    """Test BaselineGPT2 forward pass."""
    config = GPT2Config(vocab_size=1000, n_embd=128, n_layer=2, n_head=2)
    model = BaselineGPT2(config)
    input_ids = torch.randint(0, 1000, (2, 10))
    labels = torch.randint(0, 1000, (2, 10))

    outputs = model(input_ids, labels)
    assert 'loss' in outputs
    assert 'logits' in outputs
    assert outputs['logits'].shape == (2, 10, 1000)


def test_stable_rank_regularizer_initialization():
    """Test StableRankRegularizer can be initialized."""
    regularizer = StableRankRegularizer(n_power_iterations=5, n_hutchinson_probes=10)
    assert regularizer.n_power_iter == 5
    assert regularizer.n_probes == 10
    assert regularizer.eps == 1e-12


def test_regularized_gpt2_initialization():
    """Test RegularizedGPT2 can be initialized."""
    config = GPT2Config(n_embd=128, n_layer=2, n_head=2)
    model = RegularizedGPT2(config, lambda_reg=0.01)
    assert model.lambda_reg == 0.01
    assert model.regularizer is not None


def test_regularized_gpt2_forward():
    """Test RegularizedGPT2 forward pass."""
    config = GPT2Config(vocab_size=1000, n_embd=128, n_layer=2, n_head=2)
    model = RegularizedGPT2(config, lambda_reg=0.01)
    input_ids = torch.randint(0, 1000, (2, 10))
    labels = torch.randint(0, 1000, (2, 10))

    outputs = model(input_ids, labels)
    assert 'loss' in outputs
    assert 'logits' in outputs
    assert 'reg_loss' in outputs
    assert outputs['logits'].shape == (2, 10, 1000)


def test_adaptive_lambda_update():
    """Test adaptive lambda tuning."""
    config = GPT2Config(n_embd=128, n_layer=2, n_head=2)
    model = RegularizedGPT2(config, lambda_reg=0.01)

    initial_lambda = model.lambda_reg
    model.adaptive_lambda_update(current_ppl=120.0, baseline_ppl=100.0)
    assert model.lambda_reg != initial_lambda
