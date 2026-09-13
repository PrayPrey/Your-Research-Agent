"""Tests for h-m1 models.py (tasks 006, 007)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from models import FlatMLPEncoder, FlatMLPWithHead, count_params, grid_search_architecture


def test_encoder_output_shape():
    enc = FlatMLPEncoder(input_dim=256, hidden_dims=[64], embed_dim=128)
    x = torch.randn(4, 256)
    out = enc(x)
    assert out.shape == (4, 128)


def test_with_head_output():
    enc = FlatMLPEncoder(input_dim=256, hidden_dims=[64], embed_dim=128)
    model = FlatMLPWithHead(enc)
    x = torch.randn(4, 256)
    emb, pred = model(x)
    assert emb.shape == (4, 128)
    assert pred.shape == (4, 1)


def test_count_params():
    enc = FlatMLPEncoder(input_dim=100, hidden_dims=[64], embed_dim=32)
    n = count_params(enc)
    assert n > 0


def test_grid_search_finds_valid():
    # input_dim=53002 approximates real MNIST-CNN weight vector
    enc, dims, n = grid_search_architecture(
        input_dim=53002,
        candidates=[[9],[10],[8,256],[8,512],[16,128],[16,256]],
        embed_dim=128,
        dropout=0.1,
        target_min=475_000,
        target_max=525_000,
    )
    assert 475_000 <= n <= 525_000
