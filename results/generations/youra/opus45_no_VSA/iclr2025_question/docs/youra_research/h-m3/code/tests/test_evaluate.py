# test_evaluate.py - Unit tests for rate computation and gate check
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from evaluate import compute_rates, check_gate


def test_compute_rates_basic():
    """Test rate computation with known values."""
    results = [
        {"has_flip": True, "is_hallucination": True},
        {"has_flip": True, "is_hallucination": True},
        {"has_flip": False, "is_hallucination": True},
        {"has_flip": False, "is_hallucination": False},
        {"has_flip": False, "is_hallucination": False},
    ]
    # 2/3 hallucinations have flip = 66.7%
    # 0/2 correct have flip = 0%

    rates = compute_rates(results)

    assert abs(rates["hallucination_flip_rate"] - 2/3) < 0.01
    assert rates["correct_flip_rate"] == 0.0
    assert rates["n_hallucinations"] == 3
    assert rates["n_correct"] == 2


def test_check_gate_full_pass():
    """Test gate passes when halluc>=30% and correct<10%."""
    rates = {
        "hallucination_flip_rate": 0.35,
        "correct_flip_rate": 0.05,
        "separation": 0.30,
    }

    result = check_gate(rates)

    assert result["pass"] == True
    assert result["poc_pass"] == True
    assert result["falsified"] == False


def test_check_gate_poc_only():
    """Test PoC passes but full fails when direction is right but thresholds not met."""
    rates = {
        "hallucination_flip_rate": 0.25,  # Below 30%
        "correct_flip_rate": 0.15,  # Above 10%
        "separation": 0.10,
    }

    result = check_gate(rates)

    assert result["pass"] == False
    assert result["poc_pass"] == True  # halluc > correct
    assert result["falsified"] == True  # correct >= 15%


def test_check_gate_falsified():
    """Test falsification when halluc < 20%."""
    rates = {
        "hallucination_flip_rate": 0.15,
        "correct_flip_rate": 0.05,
        "separation": 0.10,
    }

    result = check_gate(rates)

    assert result["falsified"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
