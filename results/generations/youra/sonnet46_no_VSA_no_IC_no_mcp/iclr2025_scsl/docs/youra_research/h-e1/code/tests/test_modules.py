"""Spec compliance tests for h-e1 modules."""
import sys
import os
import numpy as np
import torch
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── config ──────────────────────────────────────────────────────────────────

def test_config_imports():
    import config
    assert config.SEEDS == [0, 1, 2, 3, 4]
    assert config.PARADIGMS == ['erm', 'moco', 'dino', 'barlowtwins']
    assert config.FEATURE_DIM == 2048
    assert config.BONFERRONI_N == 6
    assert config.GATE_ALPHA == 0.05
    assert config.GATE_MIN_DIFF == 0.02


# ── stats_utils ──────────────────────────────────────────────────────────────

def test_pairwise_tests_returns_6():
    from stats_utils import pairwise_tests
    ratios = {
        'erm': [1.1, 1.2, 1.0, 1.15, 1.05],
        'moco': [0.95, 0.98, 0.97, 0.96, 0.99],
        'dino': [0.90, 0.88, 0.92, 0.91, 0.89],
        'barlowtwins': [1.05, 1.08, 1.03, 1.06, 1.04],
    }
    results = pairwise_tests(ratios)
    assert len(results) == 6
    for r in results:
        assert 'pair' in r
        assert 'p_bonf' in r
        assert 'cohens_d' in r
        assert 'mean_diff' in r
        assert r['p_bonf'] <= 1.0


def test_check_gate_pass():
    from stats_utils import check_gate
    # fabricate a clearly passing pair
    pair_results = [
        {'pair': 'erm_vs_dino', 't': 5.0, 'p_raw': 0.001, 'p_bonf': 0.006, 'cohens_d': 2.0, 'mean_diff': 0.15},
        {'pair': 'erm_vs_moco', 't': 0.5, 'p_raw': 0.6, 'p_bonf': 1.0, 'cohens_d': 0.1, 'mean_diff': 0.005},
    ]
    gate_ok, passing = check_gate(pair_results)
    assert gate_ok is True
    assert len(passing) == 1
    assert passing[0]['pair'] == 'erm_vs_dino'


def test_check_gate_fail():
    from stats_utils import check_gate
    pair_results = [
        {'pair': 'erm_vs_moco', 't': 0.5, 'p_raw': 0.6, 'p_bonf': 1.0, 'cohens_d': 0.1, 'mean_diff': 0.005},
    ]
    gate_ok, passing = check_gate(pair_results)
    assert gate_ok is False
    assert len(passing) == 0


def test_run_anova():
    from stats_utils import run_anova
    ratios = {
        'erm': [1.1, 1.2, 1.0, 1.15, 1.05],
        'moco': [0.95, 0.98, 0.97, 0.96, 0.99],
        'dino': [0.90, 0.88, 0.92, 0.91, 0.89],
        'barlowtwins': [1.05, 1.08, 1.03, 1.06, 1.04],
    }
    f_stat, p_val = run_anova(ratios)
    assert isinstance(f_stat, float)
    assert 0.0 <= p_val <= 1.0


# ── probe_utils ──────────────────────────────────────────────────────────────

def test_train_eval_probe():
    from probe_utils import train_probe, eval_probe
    rng = np.random.default_rng(42)
    X_tr = rng.standard_normal((100, 32)).astype(np.float32)
    y_tr = (X_tr[:, 0] > 0).astype(int)
    X_te = rng.standard_normal((50, 32)).astype(np.float32)
    y_te = (X_te[:, 0] > 0).astype(int)
    clf = train_probe(X_tr, y_tr)
    acc = eval_probe(clf, X_te, y_te)
    assert 0.5 <= acc <= 1.0


# ── data_utils ───────────────────────────────────────────────────────────────

def test_get_balanced_probe_indices():
    from data_utils import get_balanced_probe_indices
    # synthetic metadata: col0=background(0/1), col1=bird(0/1)
    n = 200
    rng = np.random.default_rng(0)
    meta_np = rng.integers(0, 2, size=(n, 2))
    meta_t = torch.tensor(meta_np, dtype=torch.long)
    idx = get_balanced_probe_indices(meta_t, seed=0)
    assert len(idx) % 4 == 0
    assert len(idx) <= n
    assert len(np.unique(idx)) == len(idx)  # no duplicates


# ── model_utils (unit test — no GPU/Hub needed) ───────────────────────────────

def test_extract_features_shape():
    from model_utils import extract_features
    import torch.nn as nn
    # mock model returning 2048-dim output
    class FakeModel(nn.Module):
        def forward(self, x):
            return torch.ones(x.shape[0], 2048)
    model = FakeModel()

    # fake DataLoader items: (x, y, metadata)
    fake_batch = (
        torch.randn(8, 3, 224, 224),
        torch.randint(0, 2, (8,)),
        torch.zeros(8, 3, dtype=torch.long),
    )

    class FakeLoader:
        def __iter__(self):
            yield fake_batch

    feats, task_lbls, spur_lbls = extract_features(model, FakeLoader(), 'cpu')
    assert feats.shape == (8, 2048)
    assert task_lbls.shape == (8,)
    assert spur_lbls.shape == (8,)


# ── export / stats integration ────────────────────────────────────────────────

def test_export_results(tmp_path):
    from stats_utils import export_results, pairwise_tests, run_anova
    import json
    ratios = {
        'erm': [1.1, 1.0, 1.05, 1.15, 1.2],
        'moco': [0.9, 0.95, 0.92, 0.91, 0.93],
        'dino': [0.85, 0.88, 0.87, 0.86, 0.84],
        'barlowtwins': [1.05, 1.06, 1.04, 1.07, 1.03],
    }
    anova_result = run_anova(ratios)
    pair_results = pairwise_tests(ratios)
    gate_ok = True
    passing_pairs = [pair_results[0]]
    out_path = str(tmp_path / 'stats.json')
    export_results(ratios, anova_result, pair_results, gate_ok, passing_pairs, out_path)
    with open(out_path) as f:
        data = json.load(f)
    assert 'anova' in data
    assert 'pairwise' in data
    assert len(data['pairwise']) == 6
    assert 'gate' in data
