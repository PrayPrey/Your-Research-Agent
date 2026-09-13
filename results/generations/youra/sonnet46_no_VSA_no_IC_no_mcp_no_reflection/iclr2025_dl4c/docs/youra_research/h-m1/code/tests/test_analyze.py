import sys
import os
import numpy as np
import csv
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analyze import bootstrap_ci, verify_h_m1_mechanism


def test_bootstrap_ci_excludes_zero():
    np.random.seed(42)
    ratio = list(np.random.normal(2.0, 0.1, 400))
    binary = list(np.random.normal(1.0, 0.1, 400))
    result = bootstrap_ci(ratio, binary, n_bootstrap=500)
    assert result.mean_diff > 0
    assert result.excludes_zero is True
    assert result.ci_lower < result.ci_upper


def test_bootstrap_ci_includes_zero():
    binary = list(np.ones(400))
    ratio = list(np.ones(400))
    result = bootstrap_ci(ratio, binary, n_bootstrap=500)
    assert abs(result.mean_diff) < 1e-10
    assert result.excludes_zero is False


def test_verify_mechanism_gate():
    # P1 satisfied: gap=0.05 > 0.03, ci_lower=0.01 > 0
    # P2 satisfied: ratio_apps <= binary_apps
    result = verify_h_m1_mechanism(
        ratio_humaneval_pass1=0.50,
        binary_humaneval_pass1=0.45,
        ratio_apps_allpass=0.10,
        binary_apps_allpass=0.12,
        bootstrap_ci_lower=0.01,
    )
    assert result.gate_satisfied is True
    assert result.p1_satisfied is True
    assert result.p2_policy_shift is True
    assert result.result == "GATE_SATISFIED"


def test_verify_mechanism_gate_fail():
    # P1 fails: gap < 0.03
    result = verify_h_m1_mechanism(
        ratio_humaneval_pass1=0.45,
        binary_humaneval_pass1=0.44,
        ratio_apps_allpass=0.10,
        binary_apps_allpass=0.12,
        bootstrap_ci_lower=0.01,
    )
    assert result.gate_satisfied is False
    assert result.result == "GATE_FAILED"


if __name__ == "__main__":
    test_bootstrap_ci_excludes_zero()
    test_bootstrap_ci_includes_zero()
    test_verify_mechanism_gate()
    test_verify_mechanism_gate_fail()
    print("analyze tests passed")
