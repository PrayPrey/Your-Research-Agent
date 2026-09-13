"""Unit tests for analysis.py."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from analysis import welch_test, confound_analysis


def test_welch_detects_difference():
    pass_a = [0.5] * 100
    pass_b = [0.6] * 100
    result = welch_test(pass_a, pass_b)
    assert result["p_value"] < 0.05
    assert result["absolute_improvement"] > 0.09


def test_welch_no_difference():
    pass_a = [0.5] * 100
    pass_b = [0.5] * 100
    result = welch_test(pass_a, pass_b)
    assert result["gate_passed"] == False


def test_confound_analysis_returns_per_round():
    result = confound_analysis([], "mbpp+")
    assert isinstance(result["per_round_delta"], dict)


if __name__ == "__main__":
    test_welch_detects_difference()
    test_welch_no_difference()
    test_confound_analysis_returns_per_round()
    print("All analysis tests passed.")
