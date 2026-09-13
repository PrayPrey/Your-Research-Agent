"""Tests for MLP Weight Encoder."""

import sys
from pathlib import Path
import pytest
import torch

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from models.mlp_encoder import MLPWeightEncoder


def test_mlp_encoder_initialization():
    """Test MLP encoder initialization."""
    encoder = MLPWeightEncoder(
        input_dim=2864,
        hidden_dims=[512, 256],
        output_dim=64
    )
    assert encoder is not None
    assert isinstance(encoder, torch.nn.Module)


def test_mlp_encoder_forward():
    """Test MLP encoder forward pass."""
    batch_size = 16
    input_dim = 2864
    output_dim = 64

    encoder = MLPWeightEncoder(
        input_dim=input_dim,
        hidden_dims=[512, 256],
        output_dim=output_dim
    )

    # Create dummy input
    x = torch.randn(batch_size, input_dim)

    # Forward pass
    embeddings = encoder(x)

    # Check output shape
    assert embeddings.shape == (batch_size, output_dim)


def test_mlp_encoder_different_widths():
    """Test MLP encoder with different output widths."""
    widths = [8, 16, 32, 64, 128]
    batch_size = 8
    input_dim = 2864

    for width in widths:
        encoder = MLPWeightEncoder(
            input_dim=input_dim,
            hidden_dims=[512, 256],
            output_dim=width
        )

        x = torch.randn(batch_size, input_dim)
        embeddings = encoder(x)

        assert embeddings.shape == (batch_size, width)
