import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evaluate import bootstrap_ci, compute_semantic_edit_per_kl
from config import get_config


def test_bootstrap_ci_known_values():
    values = [1.0] * 100
    result = bootstrap_ci(values, n_samples=1000, ci=0.95, seed=42)
    assert result["mean"] == pytest.approx(1.0, abs=1e-6)
    assert result["lower"] == pytest.approx(1.0, abs=1e-6)
    assert result["upper"] == pytest.approx(1.0, abs=1e-6)
    assert result["n"] == 100


def test_bootstrap_ci_spread():
    values = list(range(100))
    result = bootstrap_ci(values, n_samples=5000, ci=0.95, seed=42)
    assert result["lower"] < result["mean"] < result["upper"]
    assert result["n"] == 100


def test_bootstrap_ci_single_value():
    result = bootstrap_ci([5.0], n_samples=100, ci=0.95, seed=42)
    assert result["mean"] == pytest.approx(5.0)


def test_compute_semantic_edit_per_kl_no_match():
    cfg = get_config()
    grpo_kl_log = [{"step": 100, "kl_divergence": 1.0}]
    dpo_kl_log = [{"step": 100, "kl_divergence": 5.0}]
    result = compute_semantic_edit_per_kl(
        grpo_solutions={}, dpo_solutions={}, reference_solutions={},
        grpo_kl_log=grpo_kl_log, dpo_kl_log=dpo_kl_log, cfg=cfg,
    )
    assert result["grpo_edit_per_kl"] == []
    assert result["dpo_edit_per_kl"] == []
    assert result["matched_pairs"] == []


def test_compute_semantic_edit_per_kl_with_data():
    cfg = get_config()
    grpo_solutions = {"t1": "if True:\n    x = 1\n"}
    dpo_solutions = {"t1": "for i in range(3):\n    pass\n"}
    ref_solutions = {"t1": "if True:\n    x = 1\n"}
    grpo_kl_log = [{"step": 100, "kl_divergence": 0.5}]
    dpo_kl_log = [{"step": 100, "kl_divergence": 0.52}]
    result = compute_semantic_edit_per_kl(
        grpo_solutions, dpo_solutions, ref_solutions,
        grpo_kl_log, dpo_kl_log, cfg,
    )
    assert len(result["matched_pairs"]) >= 1
    assert "mean_grpo_edit" in result
    assert "mean_dpo_edit" in result
