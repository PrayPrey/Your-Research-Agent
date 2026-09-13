"""Tests for evaluation module."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest
from evaluation import (
    compute_auroc, compute_auprc, bootstrap_auroc_diff,
    length_stratified_auroc, check_gate
)


def _make_records(logprob_lists, labels):
    return [{"logprobs": lp, "label": l} for lp, l in zip(logprob_lists, labels)]


def test_compute_auroc_perfect():
    labels = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.2, 0.8, 0.9])
    assert compute_auroc(labels, scores) == pytest.approx(1.0)


def test_compute_auroc_single_class():
    labels = np.array([1, 1, 1])
    scores = np.array([0.5, 0.6, 0.7])
    assert compute_auroc(labels, scores) == pytest.approx(0.5)


def test_compute_auprc_positive():
    labels = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.2, 0.8, 0.9])
    auprc = compute_auprc(labels, scores)
    assert 0.0 <= auprc <= 1.0


def test_bootstrap_auroc_diff_structure():
    np.random.seed(42)
    n = 200
    labels = np.array([0] * 100 + [1] * 100)
    scores_a = np.random.normal(0.7, 0.1, n)
    scores_b = np.random.normal(0.5, 0.1, n)
    ci_lo, ci_hi = bootstrap_auroc_diff(scores_a, scores_b, labels, n_resamples=100)
    assert ci_lo <= ci_hi
    assert isinstance(ci_lo, float)
    assert isinstance(ci_hi, float)


def test_length_stratified_auroc():
    records = _make_records(
        [[-0.1] * i for i in range(1, 21)],
        [0, 1] * 10
    )
    result = length_stratified_auroc(records, "min", threshold=5)
    assert "short" in result
    assert "long" in result
    assert "n_short" in result
    assert "n_long" in result
    assert result["n_short"] + result["n_long"] == 20


def test_check_gate_pass():
    auroc_table = {
        "llama2": {"trivia_qa": {"min": 0.70, "mean": 0.65, "sum": 0.60}},
    }
    ci_table = {
        "llama2": {"trivia_qa": {
            "min_vs_mean": (0.01, 0.09),  # ci_lower > 0, diff >= 0.02
            "min_vs_sum": (0.05, 0.15),
            "mean_vs_sum": (0.03, 0.10),
        }},
    }
    passed, justification = check_gate(ci_table, auroc_table)
    assert passed
    assert "PASS" in justification


def test_check_gate_fail():
    auroc_table = {
        "llama2": {"trivia_qa": {"min": 0.60, "mean": 0.60, "sum": 0.60}},
    }
    ci_table = {
        "llama2": {"trivia_qa": {
            "min_vs_mean": (-0.01, 0.01),
            "min_vs_sum": (-0.01, 0.01),
            "mean_vs_sum": (-0.01, 0.01),
        }},
    }
    passed, justification = check_gate(ci_table, auroc_table)
    assert not passed
    assert "FAIL" in justification
