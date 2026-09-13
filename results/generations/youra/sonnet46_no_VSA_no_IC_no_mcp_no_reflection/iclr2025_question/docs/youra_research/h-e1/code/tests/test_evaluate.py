"""Tests for evaluate.py spec compliance."""
import json
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evaluate import compute_metrics, save_results


def make_results(n=100, seed=0):
    rng = np.random.RandomState(seed)
    labels = [i % 2 for i in range(n)]
    # Simulate scores that correlate with labels
    nli_scores = [0.7 - 0.2 * l + rng.normal(0, 0.05) for l in labels]
    embed_scores = [0.6 - 0.15 * l + rng.normal(0, 0.05) for l in labels]
    return [
        {"idx": i, "label": labels[i], "smc_nli": nli_scores[i], "smc_embed": embed_scores[i]}
        for i in range(n)
    ]


def test_compute_metrics_keys():
    results = make_results()
    m = compute_metrics(results)
    assert "smc_nli_auroc" in m
    assert "smc_embed_auroc" in m
    assert "smc_nli_std" in m


def test_compute_metrics_auroc_range():
    results = make_results()
    m = compute_metrics(results)
    assert 0.0 <= m["smc_nli_auroc"] <= 1.0
    assert 0.0 <= m["smc_embed_auroc"] <= 1.0


def test_compute_metrics_std_positive():
    results = make_results()
    m = compute_metrics(results)
    assert m["smc_nli_std"] > 0.0


def test_save_results_creates_file():
    results = make_results(10)
    m = compute_metrics(results)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "results.json")
        save_results(results, m, path=path)
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert "metrics" in data
        assert "results" in data
