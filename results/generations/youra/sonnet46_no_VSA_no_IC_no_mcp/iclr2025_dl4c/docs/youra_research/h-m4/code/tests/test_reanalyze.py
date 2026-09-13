"""Tests for reanalyze.py — JT test + monotonicity check."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from reanalyze import (
    bootstrap_pseudo_groups,
    build_jt_groups,
    jonckheere_terpstra,
    verify_monotonicity,
    describe_trend,
    BENCHMARK_ORDER,
)
from config import H_M4_Config


def test_bootstrap_pseudo_groups_shape():
    samples = bootstrap_pseudo_groups(delta_point=0.1, pass_rate_sft=0.3,
                                      n_problems=100, n_bootstrap=200, seed=1)
    assert len(samples) == 200
    assert all(isinstance(v, float) for v in samples)


def test_bootstrap_pseudo_groups_positive_delta():
    # With positive delta, mean of samples should be > 0
    samples = bootstrap_pseudo_groups(delta_point=0.2, pass_rate_sft=0.3,
                                      n_problems=200, n_bootstrap=1000, seed=42)
    import statistics
    assert statistics.mean(samples) > 0.05, "Expected positive mean for positive delta"


def test_verify_monotonicity_true():
    deltas = {"humaneval": 0.05, "mbpp": 0.08, "lcb_easy": 0.10, "lcb_medium": 0.14, "lcb_hard": 0.18}
    is_mono, ordered = verify_monotonicity(deltas)
    assert is_mono is True
    assert len(ordered) == 5


def test_verify_monotonicity_false():
    deltas = {"humaneval": 0.10, "mbpp": 0.05, "lcb_easy": 0.08, "lcb_medium": 0.12, "lcb_hard": 0.15}
    is_mono, _ = verify_monotonicity(deltas)
    assert is_mono is False


def test_jt_monotone_passes():
    # Construct clearly increasing groups
    import numpy as np
    rng = np.random.default_rng(0)
    groups = [rng.normal(i * 0.1, 0.01, 500).tolist() for i in range(5)]
    z, p = jonckheere_terpstra(groups)
    assert z > 0
    assert p < 0.05, f"Expected p<0.05 for clearly monotone groups, got {p}"


def test_jt_flat_does_not_pass():
    # Flat groups — no trend
    import numpy as np
    rng = np.random.default_rng(1)
    groups = [rng.normal(0.1, 0.05, 500).tolist() for _ in range(5)]
    z, p = jonckheere_terpstra(groups)
    assert p > 0.1, f"Expected p>0.1 for flat groups, got {p}"


def test_describe_trend():
    deltas = {"humaneval": -0.06, "mbpp": 0.16, "lcb_easy": 0.12, "lcb_medium": -0.02, "lcb_hard": 0.18}
    _, ordered = verify_monotonicity(deltas)
    trend = describe_trend(ordered, jt_z=0.5, jt_p=0.3)
    assert "violations" in trend
    assert isinstance(trend["violations"], list)
    assert trend["gate_passed"] is False  # p=0.3 >= 0.05


def test_build_jt_groups_returns_5():
    cfg = H_M4_Config()
    cfg.n_bootstrap = 100
    deltas = {"humaneval": 0.05, "mbpp": 0.08, "lcb_easy": 0.10, "lcb_medium": 0.14, "lcb_hard": 0.18}
    groups = build_jt_groups(deltas, cfg=cfg)
    assert len(groups) == 5
    assert all(len(g) == 100 for g in groups)


if __name__ == "__main__":
    test_bootstrap_pseudo_groups_shape()
    test_bootstrap_pseudo_groups_positive_delta()
    test_verify_monotonicity_true()
    test_verify_monotonicity_false()
    test_jt_monotone_passes()
    test_jt_flat_does_not_pass()
    test_describe_trend()
    test_build_jt_groups_returns_5()
    print("ALL TESTS PASSED")
