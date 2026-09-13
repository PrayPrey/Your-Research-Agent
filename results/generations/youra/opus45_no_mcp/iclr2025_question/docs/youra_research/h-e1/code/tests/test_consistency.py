"""Basic tests for consistency computation."""
import numpy as np
import sys
sys.path.insert(0, "..")
from consistency import SemanticConsistency


def test_consistency_identical():
    """Identical responses should have consistency ~1.0."""
    calc = SemanticConsistency()
    responses = ["Paris is the capital of France"] * 3
    c = calc.compute(responses)
    assert c > 0.99, f"Identical responses should have consistency ~1.0, got {c}"


def test_consistency_diverse():
    """Diverse responses should have lower consistency."""
    calc = SemanticConsistency()
    responses = [
        "Paris is the capital of France",
        "The weather is sunny today",
        "Python is a programming language"
    ]
    c = calc.compute(responses)
    assert 0 < c < 0.9, f"Diverse responses should have lower consistency, got {c}"


def test_consistency_single():
    """Single response returns nan."""
    calc = SemanticConsistency()
    c = calc.compute(["Only one response"])
    assert np.isnan(c)


if __name__ == "__main__":
    test_consistency_identical()
    test_consistency_diverse()
    test_consistency_single()
    print("All consistency tests passed")
