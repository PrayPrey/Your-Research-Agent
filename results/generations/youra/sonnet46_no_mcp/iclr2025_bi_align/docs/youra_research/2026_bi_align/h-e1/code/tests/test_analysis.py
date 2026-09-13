"""Tests for analysis.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import pytest
from analysis import (
    CoeffResult,
    apply_bonferroni,
    bootstrap_coefficient_ci,
    placebo_permutation_test,
)
from features import build_feature_matrix
from q_early import QEarlyModel


def make_round_dfs(n_per_round=300):
    rng = np.random.default_rng(42)
    round_dfs = {}
    for r in range(1, 4):
        chosen = [f"word " * int(rng.integers(20, 60)) + "perhaps maybe" for _ in range(n_per_round)]
        rejected = [f"word " * int(rng.integers(5, 20)) for _ in range(n_per_round)]
        round_dfs[r] = pd.DataFrame({"chosen": chosen, "rejected": rejected})
    return round_dfs


def make_q_model(round_dfs):
    X1, _ = build_feature_matrix(round_dfs[1])
    # Mix labels so LR has 2 classes
    rng = np.random.default_rng(0)
    y1 = rng.integers(0, 2, size=len(X1))
    model = QEarlyModel()
    model.fit(X1, y1)
    X2, _ = build_feature_matrix(round_dfs[2])
    y2 = rng.integers(0, 2, size=len(X2))
    model.calibrate(X2, y2)
    return model


def test_apply_bonferroni():
    p = {"beta_L": 0.01, "beta_H": 0.05, "beta_S": 0.5}
    corrected = apply_bonferroni(p, k=3)
    assert corrected["beta_L"] == pytest.approx(0.03)
    assert corrected["beta_H"] == pytest.approx(0.15)
    assert corrected["beta_S"] == 1.0  # capped at 1.0


def test_apply_bonferroni_cap():
    p = {"beta_L": 0.4, "beta_H": 0.5, "beta_S": 0.6}
    corrected = apply_bonferroni(p, k=3)
    for v in corrected.values():
        assert v <= 1.0


def test_bootstrap_coefficient_ci_shape():
    round_dfs = make_round_dfs(200)
    q_model = make_q_model(round_dfs)
    results = bootstrap_coefficient_ci(round_dfs, q_model, build_feature_matrix, n_iter=100)
    assert len(results) == 3
    for r in results:
        assert isinstance(r, CoeffResult)
        assert len(r.ci_L) == 2
        assert "beta_L" in r.p_values


def test_bootstrap_n_iter_too_small():
    round_dfs = make_round_dfs(200)
    q_model = make_q_model(round_dfs)
    with pytest.raises(ValueError, match="n_iter too small"):
        bootstrap_coefficient_ci(round_dfs, q_model, build_feature_matrix, n_iter=10)


def test_placebo_permutation_test():
    round_dfs = make_round_dfs(200)
    q_model = make_q_model(round_dfs)
    perm_p = placebo_permutation_test(round_dfs, q_model, build_feature_matrix, n_iter=20)
    assert "beta_L" in perm_p
    for v in perm_p.values():
        assert 0.0 <= v <= 1.0


def test_coeff_result_fields():
    r = CoeffResult(1, 0.1, 0.2, 0.3, (0.05, 0.15), (0.1, 0.3), (0.2, 0.4),
                    {"beta_L": 0.01, "beta_H": 0.03, "beta_S": 0.1})
    assert r.round_id == 1
    assert r.beta_L == pytest.approx(0.1)
