"""Tests for uq_methods.py — E4 + subtasks spec compliance."""
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from generate import GenerationResult
from uq_methods import (
    compute_all_uq,
    compute_kle,
    compute_semantic_entropy,
    compute_token_probability,
    verify_se_mechanism,
)


def _make_result(n_samples=5, greedy_ll=-2.0):
    return GenerationResult(
        question_id="test_001",
        prompt="What is the capital of France?",
        greedy_text="Paris",
        greedy_log_likelihood=greedy_ll,
        sampled_texts=["Paris", "paris", "London", "Berlin", "Lyon"],
        sampled_log_likelihoods=[-1.5, -1.6, -3.0, -3.5, -2.8],
    )


def _make_nli_mock(entail_same=True):
    """Mock NLI model that returns high entailment for identical texts."""
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()
    mock_tokenizer.return_value = {"input_ids": MagicMock()}

    def fake_forward(**kwargs):
        # Return entailment logits: [contradiction, neutral, entailment]
        out = MagicMock()
        out.logits = MagicMock()
        # High entailment score
        import torch
        out.logits.__getitem__ = lambda self, idx: torch.tensor([0.1, 0.1, 5.0])
        return out

    mock_model.__call__ = fake_forward
    mock_model.parameters = MagicMock(return_value=iter([MagicMock(device=MagicMock())]))
    return mock_model, mock_tokenizer


# L-E4-1: compute_token_probability
def test_compute_token_probability_returns_float():
    result = _make_result(greedy_ll=-2.5)
    score = compute_token_probability(result)
    assert isinstance(score, float)


def test_compute_token_probability_higher_uncertainty_lower_ll():
    r1 = _make_result(greedy_ll=-1.0)
    r2 = _make_result(greedy_ll=-5.0)
    assert compute_token_probability(r2) > compute_token_probability(r1)


def test_compute_token_probability_negates_ll():
    result = _make_result(greedy_ll=-3.0)
    assert compute_token_probability(result) == 3.0


# L-E4-2: compute_semantic_entropy
@patch("uq_methods._get_entailment_prob")
def test_compute_semantic_entropy_returns_tuple(mock_entail):
    mock_entail.return_value = 0.9  # all entail each other -> 1 cluster
    result = _make_result(n_samples=3)
    result.sampled_texts = ["Paris", "Paris", "Paris"]
    se, K = compute_semantic_entropy(result, MagicMock(), MagicMock())
    assert isinstance(se, float)
    assert isinstance(K, int)
    assert K >= 1


@patch("uq_methods._get_entailment_prob")
def test_compute_semantic_entropy_one_cluster_low_entropy(mock_entail):
    mock_entail.return_value = 0.9
    result = _make_result()
    result.sampled_texts = ["Paris"] * 5
    se, K = compute_semantic_entropy(result, MagicMock(), MagicMock())
    assert K == 1
    assert se < 0.1  # near-zero entropy for single cluster


@patch("uq_methods._get_entailment_prob")
def test_compute_semantic_entropy_k_lt_n(mock_entail):
    # Two groups: Paris and London
    def side_effect(a, b, *args, **kwargs):
        if "paris" in a.lower() and "paris" in b.lower():
            return 0.9
        if "london" in a.lower() and "london" in b.lower():
            return 0.9
        return 0.1
    mock_entail.side_effect = side_effect
    result = _make_result()
    result.sampled_texts = ["Paris", "Paris", "Paris", "London", "London"]
    se, K = compute_semantic_entropy(result, MagicMock(), MagicMock())
    assert K == 2
    assert K < len(result.sampled_texts)


# L-E4-3: compute_kle
@patch("uq_methods._get_entailment_prob")
def test_compute_kle_returns_float_or_none(mock_entail):
    mock_entail.return_value = 0.5
    result = _make_result()
    kle = compute_kle(result, MagicMock(), MagicMock())
    assert kle is None or isinstance(kle, float)


@patch("uq_methods._get_entailment_prob")
def test_compute_kle_non_negative(mock_entail):
    mock_entail.return_value = 0.5
    result = _make_result()
    kle = compute_kle(result, MagicMock(), MagicMock())
    if kle is not None:
        assert kle >= 0


# L-E4-4: compute_all_uq
@patch("uq_methods.compute_selfcheck_nli", return_value=0.3)
@patch("uq_methods.compute_selfcheck_bertscore", return_value=0.2)
@patch("uq_methods.compute_kle", return_value=1.0)
@patch("uq_methods._get_entailment_prob")
def test_compute_all_uq_returns_dict(mock_entail, mock_kle, mock_bs, mock_nli):
    mock_entail.return_value = 0.5
    results = [_make_result() for _ in range(3)]
    uq_scores, cluster_counts = compute_all_uq(results, MagicMock(), MagicMock())
    assert isinstance(uq_scores, dict)
    assert "token_prob" in uq_scores
    assert "semantic_entropy" in uq_scores
    assert "kle" in uq_scores
    assert isinstance(cluster_counts, list)
    assert len(cluster_counts) == 3


@patch("uq_methods.compute_selfcheck_nli", return_value=0.3)
@patch("uq_methods.compute_selfcheck_bertscore", return_value=0.2)
@patch("uq_methods.compute_kle", return_value=1.0)
@patch("uq_methods._get_entailment_prob")
def test_compute_all_uq_shapes(mock_entail, mock_kle, mock_bs, mock_nli):
    mock_entail.return_value = 0.5
    Q = 5
    results = [_make_result() for _ in range(Q)]
    uq_scores, cluster_counts = compute_all_uq(results, MagicMock(), MagicMock())
    for method, arr in uq_scores.items():
        assert arr.shape == (Q,), f"{method} shape mismatch: {arr.shape}"
    assert len(cluster_counts) == Q


# verify_se_mechanism
def test_verify_se_mechanism_activated():
    cluster_counts = [2, 3, 2, 4, 3]
    ok, stats = verify_se_mechanism(cluster_counts, n_samples=10)
    assert ok is True
    assert stats["mean_k"] < 10


def test_verify_se_mechanism_degenerate():
    cluster_counts = [10, 10, 10]
    ok, stats = verify_se_mechanism(cluster_counts, n_samples=10)
    assert ok is False
