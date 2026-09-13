import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from distributional_moments import compute_moments, compute_both_segments, SegmentMoments
from directional_tests import run_directional_tests, DirectionalTestResults
from verifier import verify_directional_specificity, GateResult
from results_output import build_results_dict


def test_compute_moments_known():
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    m = compute_moments(arr)
    assert m.n == 10
    assert abs(m.mean - 5.5) < 1e-6
    assert m.skewness == 0.0  # symmetric
    assert m.p10 < m.p25 < m.p75
    print("test_compute_moments_known: PASS")


def test_compute_both_segments():
    pc = np.arange(20)
    rcov = np.random.default_rng(0).uniform(0, 1, 20)
    pre_m, post_m, pre_a, post_a = compute_both_segments(pc, rcov, 10)
    assert pre_m.n == 10
    assert post_m.n == 10
    assert len(pre_a) + len(post_a) == 20
    print("test_compute_both_segments: PASS")


def test_gate_pass():
    pre = np.random.default_rng(1).uniform(0.5, 1.5, 30)
    post = np.random.default_rng(2).uniform(0.1, 0.4, 80)

    pre_m = compute_moments(pre)
    post_m = compute_moments(post)
    results = run_directional_tests(pre, post, pre_m, post_m, n_resamples=999)
    gate = verify_directional_specificity(results)
    assert gate.gate_passed, f"Expected gate to pass, got {gate.metrics_passed}/4"
    print(f"test_gate_pass: PASS ({gate.metrics_passed}/4 metrics)")


def test_gate_explore():
    rng = np.random.default_rng(42)
    segment = rng.normal(0.5, 0.1, 30)
    pre_m = compute_moments(segment)
    post_m = compute_moments(segment)
    results = run_directional_tests(segment, segment, pre_m, post_m, n_resamples=999)
    gate = verify_directional_specificity(results)
    print(f"test_gate_explore: metrics_passed={gate.metrics_passed} (expected low)")


def test_results_json_schema():
    pre = np.random.default_rng(10).uniform(0.5, 1.0, 20)
    post = np.random.default_rng(11).uniform(0.1, 0.5, 80)
    pre_m = compute_moments(pre)
    post_m = compute_moments(post)
    res = run_directional_tests(pre, post, pre_m, post_m, n_resamples=99)
    gate = verify_directional_specificity(res)
    d = build_results_dict(pre_m, post_m, res, gate, [])
    required = [
        'n_pre', 'n_post', 'skew_pre', 'skew_post', 'kurt_pre', 'kurt_post',
        'p10_pre', 'p10_post', 'perm_p_skew_diff', 'mw_pvalue',
        'metric1_pass', 'metric2_pass', 'metric3_pass', 'metric4_pass',
        'metrics_passed', 'gate_passed', 'gate_type',
    ]
    for key in required:
        assert key in d, f"Missing key: {key}"
    print("test_results_json_schema: PASS")


if __name__ == "__main__":
    test_compute_moments_known()
    test_compute_both_segments()
    test_gate_pass()
    test_gate_explore()
    test_results_json_schema()
    print("\nAll tests passed.")
