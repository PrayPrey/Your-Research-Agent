"""Tests for similarity.py — spec compliance."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
import numpy as np
import torch
from h_e1.similarity import (
    mean_pairwise_cosine, compute_similarity_matrix, evaluate_gate,
    verify_embeddings, SOURCES, BENCHMARKS, GATE_THRESHOLD,
)


def make_fake_embeddings(n=10, d=768):
    """L2-normalized random embeddings."""
    t = torch.randn(n, d)
    return torch.nn.functional.normalize(t, dim=-1)


def make_fake_corpora(n=10):
    corpora = {}
    for name in SOURCES + BENCHMARKS:
        corpora[name] = {
            "codebert": make_fake_embeddings(n, 768),
            "minilm": make_fake_embeddings(n, 384),
        }
    return corpora


def test_sources_list():
    assert len(SOURCES) == 4
    assert "humaneval_train" in SOURCES
    assert "equal_mix" in SOURCES


def test_benchmarks_list():
    assert len(BENCHMARKS) == 2
    assert "humaneval_plus" in BENCHMARKS
    assert "mbpp_plus" in BENCHMARKS


def test_mean_pairwise_cosine_range():
    src = make_fake_embeddings(5, 64)
    tgt = make_fake_embeddings(5, 64)
    sim = mean_pairwise_cosine(src, tgt)
    assert -1.0 <= sim <= 1.0


def test_mean_pairwise_cosine_identical():
    # All-ones unit vectors → self-pairwise mean = 1.0
    src = torch.ones(5, 64) / (64 ** 0.5)
    sim = mean_pairwise_cosine(src, src)
    assert sim > 0.99


def test_compute_similarity_matrix_shape():
    embeddings = make_fake_corpora(10)
    mats = compute_similarity_matrix(embeddings)
    assert "codebert" in mats
    assert "minilm" in mats
    assert mats["codebert"].shape == (4, 2)
    assert mats["minilm"].shape == (4, 2)


def test_compute_similarity_matrix_values_in_range():
    embeddings = make_fake_corpora(10)
    mats = compute_similarity_matrix(embeddings)
    for mat in mats.values():
        assert mat.min() >= -1.0
        assert mat.max() <= 1.0


def test_evaluate_gate_satisfied_when_below_threshold():
    # Low similarity → gate satisfied
    mat = np.full((4, 2), 0.5)
    mats = {"codebert": mat, "minilm": mat.copy()}
    result = evaluate_gate(mats)
    assert result["gate_satisfied"] is True
    assert result["min_sim"] == pytest.approx(0.5, abs=0.001)


def test_evaluate_gate_not_satisfied_when_all_above():
    mat = np.full((4, 2), 0.99)
    mats = {"codebert": mat, "minilm": mat.copy()}
    result = evaluate_gate(mats)
    assert result["gate_satisfied"] is False


def test_evaluate_gate_returns_16_values():
    embeddings = make_fake_corpora(10)
    mats = compute_similarity_matrix(embeddings)
    result = evaluate_gate(mats)
    assert len(result["all_values"]) == 16  # 4x2 x 2 encoders


def test_gate_threshold_value():
    assert GATE_THRESHOLD == 0.95


def test_verify_embeddings_passes_valid():
    embeddings = make_fake_corpora(10)
    mats = compute_similarity_matrix(embeddings)
    all_pass, checks = verify_embeddings(embeddings, mats)
    # Shape checks should all pass
    for k, v in checks.items():
        if "shape" in k:
            assert v is True, f"Shape check failed: {k}"
