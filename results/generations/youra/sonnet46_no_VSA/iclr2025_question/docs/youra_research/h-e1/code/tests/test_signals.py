"""Spec compliance tests for compute_signals.py and stats_analysis.py."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest
from unittest.mock import MagicMock, patch


def test_cluster_assignment_entropy_single_cluster():
    from compute_signals import cluster_assignment_entropy
    ids = [0, 0, 0, 0, 0]
    entropy = cluster_assignment_entropy(ids)
    # Single cluster → near 0 (epsilon prevents exact 0)
    assert entropy < 0.01


def test_cluster_assignment_entropy_max_diversity():
    from compute_signals import cluster_assignment_entropy
    # All different → max entropy for n=5
    ids = [0, 1, 2, 3, 4]
    entropy = cluster_assignment_entropy(ids)
    # max entropy for 5 uniform = log(5) ≈ 1.609
    assert entropy > 1.5


def test_get_semantic_ids_all_equivalent():
    from compute_signals import get_semantic_ids
    nli_mock = MagicMock()
    # Entailment in both directions → all equivalent → one cluster
    nli_mock.predict.return_value = np.array([[0.0, 0.0, 1.0]])  # [3-class: contra/neutral/entail]
    responses = ["Paris", "Paris", "Paris"]
    ids = get_semantic_ids(responses, nli_mock)
    assert len(set(ids)) == 1  # All same cluster


def test_get_semantic_ids_all_different():
    from compute_signals import get_semantic_ids
    nli_mock = MagicMock()
    # Contradiction → all different clusters
    nli_mock.predict.return_value = np.array([[1.0, 0.0, 0.0]])  # contradiction
    responses = ["Paris", "London", "Berlin"]
    ids = get_semantic_ids(responses, nli_mock)
    assert len(set(ids)) == len(responses)


def test_compute_min_logprob_shape_and_assertion():
    from compute_signals import compute_min_logprob
    # Valid input: all negative log-probs
    token_logprobs = [[-0.5, -1.2, -0.8], [-2.1, -0.3], [-0.7, -1.5, -0.9, -2.2]]
    result = compute_min_logprob(token_logprobs)
    assert result.shape == (3,)
    assert np.all(result < 0)
    expected = [-1.2, -2.1, -2.2]
    np.testing.assert_allclose(result, expected)


def test_compute_min_logprob_fails_on_positive():
    from compute_signals import compute_min_logprob
    # min of each list must be negative; if a list's min is >= 0 → assertion fails
    # e.g. [0.5, 1.0] → min=0.5 >= 0 → AssertionError
    with pytest.raises(AssertionError):
        compute_min_logprob([[0.5, 1.0], [-0.3, -1.0]])


def test_verify_signals_passes():
    from compute_signals import verify_signals
    se = np.random.default_rng(42).uniform(0, 2, size=2500)
    min_lp = np.random.default_rng(42).uniform(-5, -0.1, size=2500)
    # Should not raise
    verify_signals(se, min_lp)


def test_verify_signals_fails_degenerate_se():
    from compute_signals import verify_signals
    se = np.zeros(2500)  # degenerate
    min_lp = np.full(2500, -1.0)
    with pytest.raises(AssertionError):
        verify_signals(se, min_lp)


def test_run_pearson_returns_tuple():
    from stats_analysis import run_pearson
    rng = np.random.default_rng(0)
    se = rng.normal(0, 1, 100)
    lp = rng.normal(0, 1, 100)
    r, p = run_pearson(se, lp)
    assert isinstance(r, float)
    assert isinstance(p, float)
    assert -1 <= r <= 1
    assert 0 <= p <= 1


def test_evaluate_gate_pass():
    from stats_analysis import evaluate_gate
    result = evaluate_gate(pearson_r=0.3, partial_r2=0.05, lrt_p=0.001)
    assert result["gate_pass"] is True
    assert result["decision"] == "PASS"


def test_evaluate_gate_explore():
    from stats_analysis import evaluate_gate
    result = evaluate_gate(pearson_r=0.75, partial_r2=0.05, lrt_p=0.001)
    assert result["gate_pass"] is False
    assert result["decision"] == "EXPLORE_N10"


def test_evaluate_gate_abandon():
    from stats_analysis import evaluate_gate
    result = evaluate_gate(pearson_r=0.9, partial_r2=0.05, lrt_p=0.001)
    assert result["gate_pass"] is False
    assert result["decision"] == "ABANDON"


def test_run_conditional_lr():
    from stats_analysis import run_conditional_lr
    rng = np.random.default_rng(42)
    n = 200
    se = rng.uniform(0, 2, n)
    lp = rng.uniform(-5, -0.1, n)
    lengths = rng.integers(1, 20, n).astype(float)
    correctness = (rng.uniform(0, 1, n) > 0.5).astype(int)
    result = run_conditional_lr(se, lp, lengths, correctness)
    assert "partial_r2_se" in result
    assert "lrt_p" in result
    assert "coefs_full" in result
    assert len(result["coefs_full"]) == 4  # min_lp, SE, L, interaction
