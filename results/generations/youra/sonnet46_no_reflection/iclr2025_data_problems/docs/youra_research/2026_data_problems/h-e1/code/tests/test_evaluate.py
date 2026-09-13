"""Tests for evaluate.py — spec compliance."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from config import ExperimentConfig
from evaluate import StratifiedEvaluator


def _make_cfg():
    cfg = ExperimentConfig()
    cfg.bootstrap_n = 100  # Fast for tests
    return cfg


def test_per_stratum_recall_correct():
    cfg = _make_cfg()
    ev = StratifiedEvaluator(cfg)
    y_true = np.array([1, 1, 0, 0, 1, 0], dtype=np.int64)
    y_pred = np.array([1, 0, 0, 0, 1, 0], dtype=np.int64)
    strata = np.array(["lexical", "lexical", "semantic", "semantic", "indeterminate", "indeterminate"], dtype=object)
    result = ev.per_stratum_recall(y_true, y_pred, strata)
    assert "lexical" in result
    assert "semantic" in result
    assert "indeterminate" in result
    assert abs(result["lexical"] - 0.5) < 1e-6


def test_minkpp_f1_variance():
    cfg = _make_cfg()
    ev = StratifiedEvaluator(cfg)
    result = ev.minkpp_f1_variance([0.8, 0.6, 0.5])
    assert abs(result - np.var([0.8, 0.6, 0.5])) < 1e-6


def test_bootstrap_ci_returns_two_floats():
    cfg = _make_cfg()
    ev = StratifiedEvaluator(cfg)
    from sklearn.metrics import recall_score
    y_true = np.array([1, 1, 0, 0, 1, 0], dtype=np.int64)
    y_pred = np.array([1, 0, 0, 0, 1, 0], dtype=np.int64)
    lower, upper = ev.bootstrap_ci(y_true, y_pred, recall_score, n_iterations=50)
    assert isinstance(lower, float)
    assert isinstance(upper, float)
    assert lower <= upper


def test_indeterminacy_rate_in_range():
    cfg = _make_cfg()
    ev = StratifiedEvaluator(cfg)
    mat = np.array([[0.8, 0.75], [0.5, 0.5], [0.9, 0.1]], dtype=np.float32)
    rate = ev.indeterminacy_rate(mat)
    assert 0.0 <= rate <= 1.0
