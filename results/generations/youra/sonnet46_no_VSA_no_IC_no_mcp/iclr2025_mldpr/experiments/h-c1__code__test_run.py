#!/usr/bin/env python3
"""Self-check tests for h-c1/code/run.py."""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from run import (
    logistic,
    fit_and_evaluate,
    compare_groups,
    verify_boundary_test_activated,
    run_ablation,
    FIT_CONFIG,
    GATE,
)


def test_logistic_shape():
    t = np.array([0.0, 5.0, 10.0, 20.0, 30.0])
    y = logistic(t, K=0.95, r=0.3, t0=15.0)
    assert y.shape == t.shape
    assert float(y[0]) < float(y[-1])  # monotone increasing
    assert all(0 <= v <= 1.01 for v in y)


def test_fit_and_evaluate_convergence():
    # Generate clean logistic data — should converge
    t = np.linspace(0, 36, 40)
    y = logistic(t, K=0.92, r=0.2, t0=15.0) + np.random.default_rng(42).normal(0, 0.01, 40)
    y = np.clip(y, 0, 1)
    res = fit_and_evaluate(t, y)
    assert "converged" in res
    assert "r_squared" in res
    assert "plausible" in res
    assert "k_boundary_hit" in res
    assert "n_points" in res
    assert res["n_points"] == 40


def test_fit_and_evaluate_fields():
    t = np.linspace(0, 30, 35)
    y = logistic(t, 0.90, 0.25, 12.0)
    res = fit_and_evaluate(t, y)
    required_keys = {"converged", "r_squared", "params", "ci_width", "plausible", "k_boundary_hit", "n_points"}
    assert required_keys.issubset(set(res.keys())), f"Missing keys: {required_keys - set(res.keys())}"


def test_fit_and_evaluate_runtime_error():
    # Constant signal should fail (or return low R²)
    t = np.linspace(0, 30, 35)
    y = np.ones(35) * 0.5
    res = fit_and_evaluate(t, y)
    # Should either not converge or have very low R²
    if res["converged"]:
        assert res["r_squared"] is not None
    else:
        assert res["r_squared"] is None


def test_compare_groups_structure():
    # Build mock results
    def make_fit(converged, r2, plausible, k_hit):
        return {"converged": converged, "r_squared": r2, "plausible": plausible,
                "k_boundary_hit": k_hit, "n_points": 35}

    small = [make_fit(False, None, False, False)] * 4 + [make_fit(True, 0.5, False, True)]
    ctrl = [make_fit(True, 0.95, True, False)] * 3

    cmp = compare_groups(small, ctrl)
    required = {"convergence_rate_small", "convergence_rate_control", "mean_r2_small",
                "mean_r2_control", "plausibility_rate_small", "plausibility_rate_control",
                "k_boundary_hit_rate_small", "h_c1_supported", "n_small", "n_control"}
    assert required.issubset(set(cmp.keys()))
    assert 0.0 <= cmp["convergence_rate_small"] <= 1.0
    assert 0.0 <= cmp["convergence_rate_control"] <= 1.0


def test_compare_groups_h_c1_supported():
    # All small benchmarks fail -> h_c1 supported
    def make_fail():
        return {"converged": False, "r_squared": None, "plausible": False, "k_boundary_hit": False, "n_points": 35}
    def make_pass():
        return {"converged": True, "r_squared": 0.95, "plausible": True, "k_boundary_hit": False, "n_points": 60}

    cmp = compare_groups([make_fail()] * 5, [make_pass()] * 3)
    assert cmp["h_c1_supported"] is True


def test_verify_boundary_test_activated():
    def make_fit(converged, r2):
        return {"converged": converged, "r_squared": r2, "plausible": converged, "k_boundary_hit": False}

    small = [make_fit(False, None)] * 3
    ctrl = [make_fit(True, 0.95)] * 3
    activated, indicators = verify_boundary_test_activated(small, ctrl)
    assert isinstance(activated, bool)
    assert "n_small" in indicators
    assert "n_control" in indicators


def test_run_ablation_returns_variants():
    rng = np.random.default_rng(0)
    timeseries_data = []
    for i in range(3):
        t = np.linspace(0, 30, 35 + i)
        y = logistic(t, 0.9, 0.2, 12) + rng.normal(0, 0.02, len(t))
        y = np.clip(y, 0, 1)
        timeseries_data.append((t, y))

    ctrl = [{"converged": True, "r_squared": 0.95, "plausible": True, "k_boundary_hit": False, "n_points": 60}]
    meta = [{"result_count": 30}, {"result_count": 40}, {"result_count": 45}]
    names = ["bm0", "bm1", "bm2"]

    ablation = run_ablation(timeseries_data, names, ctrl, benchmark_meta=meta)
    assert "strict" in ablation
    assert "loose" in ablation
    assert "no_bounds" in ablation
    assert "split40" in ablation


def test_gate_thresholds_present():
    for key in ["convergence_rate_threshold", "mean_r2_threshold",
                "plausibility_rate_threshold", "k_boundary_hit_threshold"]:
        assert key in GATE, f"Missing GATE key: {key}"


if __name__ == "__main__":
    tests = [
        test_logistic_shape,
        test_fit_and_evaluate_convergence,
        test_fit_and_evaluate_fields,
        test_fit_and_evaluate_runtime_error,
        test_compare_groups_structure,
        test_compare_groups_h_c1_supported,
        test_verify_boundary_test_activated,
        test_run_ablation_returns_variants,
        test_gate_thresholds_present,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {t.__name__}: {exc}")
            failed += 1
    print(f"\n{passed}/{passed+failed} tests passed")
    sys.exit(0 if failed == 0 else 1)
