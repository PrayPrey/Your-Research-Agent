"""Tests for task-004/008/009/010/011: UQ signal computations."""
import sys
import math
import json
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import pytest

from uq_signals import (
    _build_nli_pairs,
    _run_nli_batch,
    cluster_by_nli,
    compute_semantic_entropy,
    compute_token_entropy_mean,
    compute_all_token_entropy,
)
from config import get_config


# ─── L-A3-4: Batched NLI Pairs ───────────────────────────────────────────────

def test_pair_count():
    """N=5 → 20 ordered pairs."""
    samples = [f"s{i}" for i in range(5)]
    pairs = _build_nli_pairs(samples)
    assert len(pairs) == 20


def test_pair_count_n3():
    """N=3 → 6 ordered pairs."""
    pairs = _build_nli_pairs(["a", "b", "c"])
    assert len(pairs) == 6


def test_pairs_are_dicts():
    pairs = _build_nli_pairs(["a", "b"])
    assert all("text" in p and "text_pair" in p for p in pairs)


# ─── L-A3-1: NLI Clustering ──────────────────────────────────────────────────

def _make_mock_nli_pipeline(always_entail=False, never_entail=True):
    """Mock NLI pipeline that always returns ENTAILMENT or NEUTRAL."""
    label = "ENTAILMENT" if always_entail else "NEUTRAL"

    def pipeline(pairs, **kwargs):
        if isinstance(pairs, list) and isinstance(pairs[0], dict):
            return [{"label": label, "score": 0.99}] * len(pairs)
        return [{"label": label, "score": 0.99}]
    return pipeline


def test_clustering_identical_samples():
    """All same samples → 1 cluster."""
    samples = ["The sky is blue."] * 5
    pipe = _make_mock_nli_pipeline(always_entail=True)
    cluster_ids = cluster_by_nli(samples, pipe)
    assert len(set(cluster_ids.values())) == 1


def test_clustering_all_distinct():
    """All different samples → each in own cluster."""
    samples = [f"Different answer {i}" for i in range(5)]
    pipe = _make_mock_nli_pipeline(always_entail=False)
    cluster_ids = cluster_by_nli(samples, pipe)
    assert len(set(cluster_ids.values())) == 5


def test_entropy_zero_one_cluster():
    """Single cluster → entropy=0."""
    samples = ["same"] * 5
    pipe = _make_mock_nli_pipeline(always_entail=True)
    H = compute_semantic_entropy(samples, pipe)
    assert H < 0.01, f"Entropy should be ~0, got {H}"


def test_semantic_entropy_range():
    """Entropy should be ≥ 0."""
    samples = [f"s{i}" for i in range(5)]
    pipe = _make_mock_nli_pipeline(always_entail=False)
    H = compute_semantic_entropy(samples, pipe)
    assert H >= 0.0


def test_nli_clustering_all_different():
    """Max entropy with N clusters."""
    samples = [f"unrelated text {i}" for i in range(5)]
    pipe = _make_mock_nli_pipeline(always_entail=False)
    cluster_ids = cluster_by_nli(samples, pipe)
    H = compute_semantic_entropy(samples, pipe)
    assert H > 0.0


# ─── L-A3-2: Token Entropy Mean ──────────────────────────────────────────────

def test_token_entropy_scalar():
    """Output is scalar float."""
    logits = torch.randn(10, 32000)
    result = compute_token_entropy_mean(logits)
    assert isinstance(result, float)
    assert result >= 0.0


def test_entropy_uniform():
    """Uniform distribution → entropy = log(vocab_size)."""
    vocab_size = 4
    seq_len = 3
    logits = torch.zeros(seq_len, vocab_size)  # uniform after softmax
    result = compute_token_entropy_mean(logits)
    expected = math.log(vocab_size)
    assert abs(result - expected) < 0.01, f"Expected {expected}, got {result}"


def test_entropy_peaked():
    """Peaked distribution (one-hot logits) → entropy ≈ 0."""
    seq_len = 5
    vocab_size = 32000
    logits = torch.full((seq_len, vocab_size), -1e9)
    logits[:, 0] = 1e9  # Put all mass on token 0
    result = compute_token_entropy_mean(logits)
    assert result < 0.01, f"Expected ~0, got {result}"


def test_fp16_input():
    """fp16 input handled without overflow."""
    logits = torch.randn(5, 32000, dtype=torch.float16)
    result = compute_token_entropy_mean(logits)
    assert isinstance(result, float)
    assert not math.isnan(result)


def test_compute_all_token_entropy():
    """Load .pt files and compute entropy."""
    with tempfile.TemporaryDirectory() as d:
        cfg = get_config()
        cfg.outputs_dir = d
        logits_dir = Path(d) / "greedy_logits"
        logits_dir.mkdir()
        uq_dir = Path(d) / "uq_scores"
        uq_dir.mkdir()

        logits = torch.randn(8, 32000)
        torch.save(logits.half(), logits_dir / "example_0.pt")
        torch.save(logits.half(), logits_dir / "example_1.pt")

        result = compute_all_token_entropy(d, cfg)
        assert 0 in result and 1 in result
        assert all(isinstance(v, float) for v in result.values())
