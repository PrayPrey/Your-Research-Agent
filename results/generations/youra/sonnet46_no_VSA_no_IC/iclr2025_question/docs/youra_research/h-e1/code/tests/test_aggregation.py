"""Tests for aggregation module."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest
from aggregation import aggregate, compute_all_scores


def test_aggregate_min():
    lp = [-0.1, -0.5, -2.0]
    assert aggregate(lp, "min") == pytest.approx(-2.0)


def test_aggregate_mean():
    lp = [-0.1, -0.5, -2.0]
    assert aggregate(lp, "mean") == pytest.approx(np.mean(lp))


def test_aggregate_sum():
    lp = [-0.1, -0.5, -2.0]
    assert aggregate(lp, "sum") == pytest.approx(-2.6)


def test_aggregate_single_token():
    lp = [-0.3]
    assert aggregate(lp, "min") == pytest.approx(-0.3)
    assert aggregate(lp, "mean") == pytest.approx(-0.3)
    assert aggregate(lp, "sum") == pytest.approx(-0.3)


def test_aggregate_raises_unknown_method():
    with pytest.raises(ValueError):
        aggregate([-0.1], "max")


def test_aggregate_raises_empty():
    with pytest.raises(ValueError):
        aggregate([], "min")


def test_compute_all_scores_shape():
    records = [
        {"logprobs": [-0.1, -0.5], "label": 1},
        {"logprobs": [-2.0, -3.0], "label": 0},
    ]
    result = compute_all_scores(records)
    assert set(result.keys()) == {"min", "mean", "sum"}
    for method in result:
        scores, labels = result[method]
        assert scores.shape == (2,)
        assert labels.shape == (2,)
        # Scores are negated: all >= 0 for log-probs <= 0
        assert np.all(scores >= 0)


def test_compute_all_scores_negated():
    records = [{"logprobs": [-1.0], "label": 1}]
    result = compute_all_scores(records)
    # -(-1.0) = 1.0
    for method in result:
        scores, _ = result[method]
        assert scores[0] == pytest.approx(1.0)


def test_compute_all_scores_order():
    # More uncertain (more negative logprobs) -> higher negated score -> predicted hallucinated
    records = [
        {"logprobs": [-0.1], "label": 1},   # confident
        {"logprobs": [-5.0], "label": 0},   # uncertain
    ]
    result = compute_all_scores(records)
    for method in result:
        scores, labels = result[method]
        # Hallucinated sample should have higher score
        assert scores[1] > scores[0]
