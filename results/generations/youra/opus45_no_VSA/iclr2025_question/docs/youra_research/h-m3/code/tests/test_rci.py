# test_rci.py - Unit tests for RCI flip detector
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import pytest
from rci import RCIFlipDetector


def test_extract_layer_predictions_shape():
    """Test layer logits output shape is [9, B, V]."""
    vocab_size = 100
    hidden_dim = 64
    batch_size = 2
    seq_len = 10

    # Synthetic unembedding weight
    W = torch.randn(vocab_size, hidden_dim)
    detector = RCIFlipDetector(W, layer_range=(24, 32))

    # Synthetic hidden states: 33 layers
    hidden_states = tuple(
        torch.randn(batch_size, seq_len, hidden_dim) for _ in range(33)
    )

    layer_logits = detector.extract_layer_predictions(hidden_states)

    assert layer_logits.shape == (9, batch_size, vocab_size)


def test_detect_flip_pattern_no_flips():
    """Test flip detection when all layers predict same token."""
    vocab_size = 100
    batch_size = 1
    num_layers = 9

    # All layers have same top prediction
    layer_logits = torch.zeros(num_layers, batch_size, vocab_size)
    layer_logits[:, :, 0] = 1.0  # Token 0 always highest

    W = torch.randn(vocab_size, 64)
    detector = RCIFlipDetector(W)

    num_flips, flip_positions = detector.detect_flip_pattern(layer_logits)

    assert num_flips[0].item() == 0
    assert flip_positions.sum().item() == 0


def test_detect_flip_pattern_with_flips():
    """Test flip detection when top token changes between layers."""
    vocab_size = 100
    batch_size = 1
    num_layers = 9

    layer_logits = torch.zeros(num_layers, batch_size, vocab_size)
    # Layer 0-3: token 0, Layer 4-8: token 1 (1 flip at position 3->4)
    layer_logits[:4, :, 0] = 1.0
    layer_logits[4:, :, 1] = 1.0

    W = torch.randn(vocab_size, 64)
    detector = RCIFlipDetector(W)

    num_flips, flip_positions = detector.detect_flip_pattern(layer_logits)

    assert num_flips[0].item() == 1
    assert flip_positions[3, 0].item() == True  # Flip between layer 3 and 4


def test_compute_sample_output_format():
    """Test compute_sample returns expected dict structure."""
    vocab_size = 100
    hidden_dim = 64
    seq_len = 10

    W = torch.randn(vocab_size, hidden_dim)
    detector = RCIFlipDetector(W, layer_range=(24, 32))

    hidden_states = tuple(
        torch.randn(1, seq_len, hidden_dim) for _ in range(33)
    )

    result = detector.compute_sample(hidden_states)

    assert "num_flips" in result
    assert "has_flip" in result
    assert "flip_positions" in result
    assert isinstance(result["num_flips"], int)
    assert isinstance(result["has_flip"], bool)
    assert isinstance(result["flip_positions"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
