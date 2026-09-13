"""Basic tests for H-M3 noise analysis."""
import sys
import os

h_m3_code = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, h_m3_code)

from sample_builder import NoiseSample, collect_synthetic_samples

sys.path.insert(0, h_m3_code)
import importlib.util
spec = importlib.util.spec_from_file_location("stats_tests_m3", os.path.join(h_m3_code, "stats_tests.py"))
stats_tests_m3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stats_tests_m3)
compare_concentration = stats_tests_m3.compare_concentration
summarize_noise_ratio = stats_tests_m3.summarize_noise_ratio
import numpy as np


def test_synthetic_samples():
    samples = collect_synthetic_samples(n_per_category=10, seed=42)
    assert len(samples) == 20
    u_line = [s for s in samples if s.error_type == "U_line"]
    u_ignore = [s for s in samples if s.error_type == "U_ignore"]
    assert len(u_line) == 10
    assert len(u_ignore) == 10
    print("test_synthetic_samples: PASS")


def test_compare_concentration():
    u_line = [10.0, 12.0, 11.0, 9.0, 13.0]
    u_ignore = [2.0, 3.0, 2.5, 1.5, 3.5]
    result = compare_concentration(u_line, u_ignore)
    assert result['u_line_mean'] > result['u_ignore_mean']
    assert result['t_p'] < 0.05
    assert result['cohens_d'] > 0.5
    print("test_compare_concentration: PASS")


def test_summarize_noise_ratio():
    noise_ratios = [1.5, 2.0, 0.8, 1.2, 3.0, 0.5, 1.8]
    summary = summarize_noise_ratio(noise_ratios)
    assert 'mean' in summary
    assert 'pct_above_1' in summary
    assert summary['pct_above_1'] > 50
    print("test_summarize_noise_ratio: PASS")


if __name__ == "__main__":
    test_synthetic_samples()
    test_compare_concentration()
    test_summarize_noise_ratio()
    print("\nAll tests passed!")
