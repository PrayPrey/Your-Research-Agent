"""
Tests for binomial hypothesis test.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis.hypothesis_test import binomial_test


def test_binomial_test_pass():
    """Test binomial test when it should PASS gate (p >= 0.40)."""
    # 225 violations out of 500 = 0.45 (> 0.40)
    p_value, decision = binomial_test(n_successes=225, n_trials=500, p_null=0.40)

    assert decision is True, "Should PASS gate when p=0.45 > 0.40"
    assert p_value < 0.05, f"p-value should be < 0.05 for PASS, got {p_value}"


def test_binomial_test_fail():
    """Test binomial test when it should FAIL gate (p < 0.40)."""
    # 150 violations out of 500 = 0.30 (< 0.40)
    p_value, decision = binomial_test(n_successes=150, n_trials=500, p_null=0.40)

    assert decision is False, "Should FAIL gate when p=0.30 < 0.40"
    assert p_value > 0.05, f"p-value should be > 0.05 for FAIL, got {p_value}"


def test_binomial_test_threshold():
    """Test binomial test exactly at threshold."""
    # 200 violations out of 500 = 0.40 (at threshold)
    p_value, decision = binomial_test(n_successes=200, n_trials=500, p_null=0.40)

    # At exact threshold, p-value should be high (not significant)
    assert p_value > 0.10, f"At threshold, p-value should be > 0.10, got {p_value}"


def test_binomial_test_high_rate():
    """Test with very high violation rate."""
    # 400 violations out of 500 = 0.80
    p_value, decision = binomial_test(n_successes=400, n_trials=500, p_null=0.40)

    assert decision is True, "Should PASS with very high rate"
    assert p_value < 0.001, f"p-value should be very small, got {p_value}"


def test_binomial_test_low_rate():
    """Test with very low violation rate."""
    # 50 violations out of 500 = 0.10
    p_value, decision = binomial_test(n_successes=50, n_trials=500, p_null=0.40)

    assert decision is False, "Should FAIL with very low rate"
    assert p_value > 0.99, f"p-value should be very high, got {p_value}"


def test_binomial_test_different_alpha():
    """Test with different significance level."""
    # 210 violations out of 500 = 0.42 (marginally above threshold)
    p_value, decision_005 = binomial_test(n_successes=210, n_trials=500, p_null=0.40, alpha=0.05)
    p_value, decision_010 = binomial_test(n_successes=210, n_trials=500, p_null=0.40, alpha=0.10)

    # More lenient alpha should be more likely to pass
    if not decision_005:
        assert not decision_010 or p_value < 0.10, "If fails at 0.05, may pass at 0.10"


def test_binomial_test_different_threshold():
    """Test with different null hypothesis threshold."""
    n_successes = 225  # 0.45 rate

    # Should pass for p_null=0.40
    p_value_40, decision_40 = binomial_test(n_successes, 500, p_null=0.40)
    # Should fail for p_null=0.50
    p_value_50, decision_50 = binomial_test(n_successes, 500, p_null=0.50)

    assert decision_40 is True, "Should pass against lower threshold"
    assert decision_50 is False, "Should fail against higher threshold"


def test_binomial_test_edge_cases():
    """Test edge cases."""
    # All violations
    p_value, decision = binomial_test(500, 500, p_null=0.40)
    assert decision is True, "All violations should PASS"

    # No violations
    p_value, decision = binomial_test(0, 500, p_null=0.40)
    assert decision is False, "No violations should FAIL"


def test_binomial_test_return_types():
    """Test that function returns correct types."""
    p_value, decision = binomial_test(225, 500)

    assert isinstance(p_value, float), "p_value should be float"
    assert isinstance(decision, bool), "decision should be bool"
    assert 0 <= p_value <= 1, "p_value should be between 0 and 1"
