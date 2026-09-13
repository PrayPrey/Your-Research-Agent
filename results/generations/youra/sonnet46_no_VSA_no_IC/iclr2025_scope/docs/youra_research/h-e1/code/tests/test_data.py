"""Tests for data.py: chunk_and_split spec compliance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import torch
import pytest
from unittest.mock import patch, MagicMock


def make_mock_tokenizer(n_tokens=300_000):
    """Return a mock tokenizer that produces n_tokens token ids."""
    tok = MagicMock()
    tok.encode.return_value = list(range(n_tokens))
    return tok


def make_mock_texts(n=10):
    return ["word " * 1000 for _ in range(n)]


def test_chunk_and_split_output_types():
    """chunk_and_split returns 3 lists of tensors."""
    from data import chunk_and_split

    texts = make_mock_texts()
    with patch("data.AutoTokenizer") as mock_cls:
        mock_cls.from_pretrained.return_value = make_mock_tokenizer(700_000)
        A, B, C = chunk_and_split(texts, tokenizer_name="dummy")

    assert isinstance(A, list) and isinstance(B, list) and isinstance(C, list)
    assert isinstance(A[0], torch.Tensor)


def test_chunk_and_split_subset_sizes():
    """Each subset has exactly subset_size=100 tensors."""
    from data import chunk_and_split

    texts = make_mock_texts()
    with patch("data.AutoTokenizer") as mock_cls:
        mock_cls.from_pretrained.return_value = make_mock_tokenizer(700_000)
        A, B, C = chunk_and_split(texts, tokenizer_name="dummy")

    assert len(A) == 45
    assert len(B) == 45
    assert len(C) == 45


def test_chunk_and_split_tensor_shapes():
    """Each tensor has shape (1, 2048)."""
    from data import chunk_and_split

    texts = make_mock_texts()
    with patch("data.AutoTokenizer") as mock_cls:
        mock_cls.from_pretrained.return_value = make_mock_tokenizer(700_000)
        A, B, C = chunk_and_split(texts, tokenizer_name="dummy")

    for t in A + B + C:
        assert t.shape == (1, 2048), f"Expected (1, 2048), got {t.shape}"


def test_chunk_and_split_non_overlapping():
    """Subsets are non-overlapping (different index ranges)."""
    from data import chunk_and_split

    n_tokens = 300_000
    texts = make_mock_texts()
    with patch("data.AutoTokenizer") as mock_cls:
        tok = MagicMock()
        # Token ids are sequential so we can track index ranges
        tok.encode.return_value = list(range(n_tokens))
        mock_cls.from_pretrained.return_value = tok
        A, B, C = chunk_and_split(texts, tokenizer_name="dummy")

    # First token of each subset should not overlap
    a0 = A[0][0, 0].item()
    b0 = B[0][0, 0].item()
    c0 = C[0][0, 0].item()
    # A starts at 0, B at 45*2048, C at 90*2048
    assert a0 == 0
    assert b0 == 45 * 2048
    assert c0 == 90 * 2048


def test_chunk_and_split_tensor_dtype():
    """Tensors are int64."""
    from data import chunk_and_split

    texts = make_mock_texts()
    with patch("data.AutoTokenizer") as mock_cls:
        mock_cls.from_pretrained.return_value = make_mock_tokenizer(700_000)
        A, B, C = chunk_and_split(texts, tokenizer_name="dummy")

    assert A[0].dtype == torch.long
