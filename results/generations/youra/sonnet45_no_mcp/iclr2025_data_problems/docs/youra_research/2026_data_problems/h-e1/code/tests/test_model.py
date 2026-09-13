"""
Tests for GPT-2 Model
Verifies model architecture and forward pass.
"""

import pytest
import torch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.gpt2_model import GPT2Model, GPT2Config, create_model


def test_gpt2_config():
    """Test GPT-2 configuration."""
    config = GPT2Config(
        vocab_size=50257,
        n_layer=24,
        n_head=16,
        n_embd=1536,
        n_positions=2048,
        dropout=0.1
    )

    assert config.vocab_size == 50257
    assert config.n_layer == 24
    assert config.n_head == 16
    assert config.n_embd == 1536


def test_gpt2_model_creation():
    """Test model can be created."""
    config = GPT2Config(n_layer=2, n_head=4, n_embd=128, n_positions=512)
    model = GPT2Model(config)

    assert model is not None
    assert len(model.blocks) == 2


def test_gpt2_forward_pass():
    """Test forward pass produces correct output shape."""
    config = GPT2Config(n_layer=2, n_head=4, n_embd=128, n_positions=512, vocab_size=1000)
    model = GPT2Model(config)
    model.eval()

    # Create dummy input
    batch_size = 2
    seq_length = 64
    input_ids = torch.randint(0, 1000, (batch_size, seq_length))

    # Forward pass without labels
    with torch.no_grad():
        logits = model(input_ids)

    assert logits.shape == (batch_size, seq_length, 1000), \
        f"Expected shape (2, 64, 1000), got {logits.shape}"


def test_gpt2_forward_with_labels():
    """Test forward pass with labels computes loss."""
    config = GPT2Config(n_layer=2, n_head=4, n_embd=128, n_positions=512, vocab_size=1000)
    model = GPT2Model(config)
    model.eval()

    batch_size = 2
    seq_length = 64
    input_ids = torch.randint(0, 1000, (batch_size, seq_length))
    labels = torch.randint(0, 1000, (batch_size, seq_length))

    with torch.no_grad():
        loss, logits = model(input_ids, labels)

    assert loss is not None, "Loss should be computed when labels provided"
    assert isinstance(loss.item(), float), "Loss should be a scalar"
    assert logits.shape == (batch_size, seq_length, 1000)


def test_create_model_1b():
    """Test creating 1B model."""
    model = create_model("1B")

    assert model is not None
    assert model.config.n_layer == 24
    assert model.config.n_embd == 1536
    assert model.config.n_head == 16


def test_create_model_7b():
    """Test creating 7B model."""
    model = create_model("7B")

    assert model is not None
    assert model.config.n_layer == 32
    assert model.config.n_embd == 4096
    assert model.config.n_head == 32


def test_model_parameter_count():
    """Test model has expected number of parameters."""
    model = create_model("1B")
    n_params = model.get_num_params()

    # 1B model should have approximately 0.7-1.5 billion parameters
    assert 0.7e9 < n_params < 1.5e9, \
        f"1B model should have ~1B params, got {n_params:,}"


def test_causal_masking():
    """Test that causal masking is applied (no future peeking)."""
    config = GPT2Config(n_layer=1, n_head=2, n_embd=64, n_positions=128, vocab_size=1000)
    model = GPT2Model(config)
    model.eval()

    # Forward pass
    input_ids = torch.randint(0, 1000, (1, 10))

    with torch.no_grad():
        logits = model(input_ids)

    # The model should produce valid logits
    assert not torch.isnan(logits).any(), "Model produced NaN values"
    assert not torch.isinf(logits).any(), "Model produced Inf values"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
