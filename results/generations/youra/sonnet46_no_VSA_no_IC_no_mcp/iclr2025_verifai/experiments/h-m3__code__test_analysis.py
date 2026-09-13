"""Unit tests for h-m3 analysis."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from analysis import welch_test, confound_analysis


def test_welch_detects_difference():
    import random
    random.seed(0)
    pass_a = [random.gauss(0.5, 0.1) for _ in range(100)]
    pass_b = [random.gauss(0.65, 0.1) for _ in range(100)]
    result = welch_test(pass_a, pass_b)
    assert result["p_value"] < 0.05
    assert result["absolute_improvement"] > 0.05

def test_welch_no_difference():
    pass_a = [0.5] * 100
    pass_b = [0.5] * 100
    result = welch_test(pass_a, pass_b)
    assert result["gate_passed"] == False

def test_confound_analysis_empty():
    result = confound_analysis([], "mbpp+")
    assert isinstance(result["per_round_delta"], dict)

if __name__ == "__main__":
    test_welch_detects_difference()
    test_welch_no_difference()
    test_confound_analysis_empty()
    print("All analysis tests passed.")
