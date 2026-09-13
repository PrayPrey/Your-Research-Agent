"""Tests for evaluate.py — E5 + subtasks spec compliance."""
import os
import sys
import tempfile

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evaluate import bootstrap_auroc_ci, compute_auroc, evaluate_all, run_gate_check


# L-E5-1: bootstrap_auroc_ci
def test_bootstrap_auroc_ci_returns_tuple():
    scores = np.array([0.1, 0.5, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4, 0.6, 0.15])
    labels = np.array([0, 1, 1, 0, 1, 0, 1, 0, 1, 0])
    mean_a, ci_l, ci_h = bootstrap_auroc_ci(scores, labels, n_resamples=100)
    assert isinstance(mean_a, float)
    assert isinstance(ci_l, float)
    assert isinstance(ci_h, float)


def test_bootstrap_auroc_ci_ordering():
    scores = np.array([0.1, 0.5, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4, 0.6, 0.15])
    labels = np.array([0, 1, 1, 0, 1, 0, 1, 0, 1, 0])
    mean_a, ci_l, ci_h = bootstrap_auroc_ci(scores, labels, n_resamples=200)
    assert ci_l <= mean_a <= ci_h


def test_bootstrap_auroc_ci_perfect_predictor():
    # Perfect predictor: uncertainty always high for incorrect
    labels = np.array([1, 1, 1, 0, 0, 0])
    scores = np.array([0.1, 0.1, 0.1, 0.9, 0.9, 0.9])  # low uncertainty -> correct
    mean_a, ci_l, ci_h = bootstrap_auroc_ci(scores, labels, n_resamples=200)
    assert mean_a > 0.8


def test_bootstrap_auroc_ci_range():
    scores = np.random.rand(100)
    labels = (np.random.rand(100) > 0.5).astype(int)
    mean_a, ci_l, ci_h = bootstrap_auroc_ci(scores, labels, n_resamples=100)
    assert 0.0 <= ci_l <= 1.0
    assert 0.0 <= ci_h <= 1.0


# L-E5-2: run_gate_check
def _make_uq_scores_all(se_better=True):
    """Create mock uq_scores_all with SE better than TP if se_better=True."""
    np.random.seed(42)
    Q = 200
    labels = (np.random.rand(Q) > 0.5).astype(int)

    if se_better:
        # SE scores: high for wrong, low for right
        se = np.where(labels == 1, np.random.uniform(0, 0.4, Q), np.random.uniform(0.6, 1.0, Q))
        tp = np.where(labels == 1, np.random.uniform(0.2, 0.6, Q), np.random.uniform(0.4, 0.8, Q))
    else:
        se = np.random.rand(Q)
        tp = np.random.rand(Q)

    return (
        {
            "small": {"trivia_qa": {"semantic_entropy": se, "token_prob": tp},
                      "natural_questions": {"semantic_entropy": se, "token_prob": tp}},
            "large": {"trivia_qa": {"semantic_entropy": se, "token_prob": tp},
                      "natural_questions": {"semantic_entropy": se, "token_prob": tp}},
        },
        {"trivia_qa": labels, "natural_questions": labels},
    )


def test_run_gate_check_returns_tuple():
    uq_scores_all, labels_all = _make_uq_scores_all(se_better=True)
    gate_pass, conditions = run_gate_check({}, uq_scores_all, labels_all, n_resamples=100)
    assert isinstance(gate_pass, bool)
    assert isinstance(conditions, dict)


def test_run_gate_check_conditions_keys():
    uq_scores_all, labels_all = _make_uq_scores_all(se_better=True)
    _, conditions = run_gate_check({}, uq_scores_all, labels_all, n_resamples=50)
    expected_keys = {"8b_trivia", "70b_trivia", "8b_nq", "70b_nq"}
    assert set(conditions.keys()) == expected_keys


def test_compute_auroc_perfect():
    labels = np.array([1, 1, 0, 0])
    scores = np.array([0.1, 0.2, 0.9, 0.8])  # low uncertainty = correct
    auroc = compute_auroc(scores, labels)
    assert auroc == 1.0


def test_compute_auroc_range():
    labels = np.array([1, 0, 1, 0, 1, 0])
    scores = np.random.rand(6)
    auroc = compute_auroc(scores, labels)
    assert 0.0 <= auroc <= 1.0
