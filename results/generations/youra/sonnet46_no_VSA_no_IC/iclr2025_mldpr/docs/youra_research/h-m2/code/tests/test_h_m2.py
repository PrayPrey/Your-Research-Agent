"""Minimal self-check for H-M2 analyzer logic."""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer import split_segments, run_brown_forsythe_pre_post, analyze


def test_split_segments():
    cov = np.arange(10, dtype=float)
    pre, post = split_segments(cov, 5)
    assert len(pre) == 5
    assert len(post) == 5
    assert list(pre) == [0, 1, 2, 3, 4]
    assert list(post) == [5, 6, 7, 8, 9]
    print("test_split_segments: PASS")


def test_split_segments_post_guard():
    cov = np.arange(10, dtype=float)
    try:
        split_segments(cov, 8)  # post only 2
        assert False, "Should raise"
    except ValueError:
        print("test_split_segments_post_guard: PASS")


def test_bf_compressed():
    """Synthetic: post has much lower variance than pre -> gate should PASS."""
    np.random.seed(42)
    pre = np.random.normal(0, 1.0, 50)   # high variance
    post = np.random.normal(0, 0.1, 50)  # low variance
    bf_stat, bf_p_two, bf_p_one, ratio = run_brown_forsythe_pre_post(pre, post)
    assert ratio < 1.0, f"Expected ratio < 1.0, got {ratio}"
    assert bf_p_two < 0.05, f"Expected p < 0.05, got {bf_p_two}"
    print(f"test_bf_compressed: PASS (ratio={ratio:.4f}, p={bf_p_two:.4f})")


def test_analyze_gate_pass():
    np.random.seed(42)
    N = 111
    paper_counts = np.arange(1, N + 1)
    pre = np.random.normal(0, 1.0, 40)
    post = np.random.normal(0, 0.2, N - 40)
    residual_cov = np.concatenate([pre, post])
    results = analyze(paper_counts, residual_cov, 40)
    assert results["n_pre"] == 40
    assert results["n_post"] == 71
    assert results["variance_ratio"] < 1.0
    print(f"test_analyze_gate_pass: PASS (gate={results['gate_passed']})")


if __name__ == "__main__":
    test_split_segments()
    test_split_segments_post_guard()
    test_bf_compressed()
    test_analyze_gate_pass()
    print("\nAll tests PASS")
