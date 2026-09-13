"""Tests for NFN Weight Encoder."""

import sys
from pathlib import Path
import pytest
import torch

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from models.nfn_encoder import NFNWeightEncoder


def test_nfn_encoder_initialization():
    """Test NFN encoder initialization."""
    encoder = NFNWeightEncoder(
        input_dim=2864,
        num_layers=4,
        hidden_dim=64,
        input_channels=1
    )
    assert encoder is not None
    assert isinstance(encoder, torch.nn.Module)


def test_nfn_encoder_forward():
    """Test NFN encoder forward pass."""
    batch_size = 16
    input_dim = 2864
    hidden_dim = 64

    encoder = NFNWeightEncoder(
        input_dim=input_dim,
        num_layers=4,
        hidden_dim=hidden_dim
    )

    # Create dummy input
    x = torch.randn(batch_size, input_dim)

    # Forward pass
    embeddings = encoder(x)

    # Check output shape
    assert embeddings.shape == (batch_size, hidden_dim)


def test_nfn_encoder_different_widths():
    """Test NFN encoder with different output widths."""
    widths = [8, 16, 32, 64, 128]
    batch_size = 8
    input_dim = 2864

    for width in widths:
        encoder = NFNWeightEncoder(
            input_dim=input_dim,
            num_layers=4,
            hidden_dim=width
        )

        x = torch.randn(batch_size, input_dim)
        embeddings = encoder(x)

        assert embeddings.shape == (batch_size, width)
