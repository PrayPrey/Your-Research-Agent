"""Tests for overlap analysis module."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from overlap import jaccard_index, compute_jaccard_overlap, gate_check


def test_jaccard_index():
    assert jaccard_index(set(), set()) == 0.0
    assert jaccard_index({1, 2}, {1, 2}) == 1.0
    assert jaccard_index({1}, {2}) == 0.0
    assert jaccard_index({1, 2}, {2, 3}) == 1/3
    print("  ✓ jaccard_index")


def test_compute_jaccard_overlap():
    sets = {
        "grammar": {1, 2, 3},
        "static": {4, 5, 6},
        "smt": {7, 8, 9},
    }
    overlaps = compute_jaccard_overlap(sets)
    assert overlaps["grammar_vs_static"] == 0.0
    assert overlaps["grammar_vs_smt"] == 0.0
    assert overlaps["static_vs_smt"] == 0.0
    assert overlaps["mean"] == 0.0
    print("  ✓ compute_jaccard_overlap (disjoint)")

    sets2 = {
        "grammar": {1, 2, 3},
        "static": {1, 2, 3},
        "smt": {1, 2, 3},
    }
    overlaps2 = compute_jaccard_overlap(sets2)
    assert overlaps2["grammar_vs_static"] == 1.0
    print("  ✓ compute_jaccard_overlap (identical)")


def test_gate_check():
    overlaps_pass = {"grammar_vs_static": 0.1, "grammar_vs_smt": 0.2, "static_vs_smt": 0.15, "mean": 0.15}
    assert gate_check(overlaps_pass, 0.30) == True
    print("  ✓ gate_check (pass)")

    overlaps_fail = {"grammar_vs_static": 0.35, "grammar_vs_smt": 0.2, "static_vs_smt": 0.15, "mean": 0.23}
    assert gate_check(overlaps_fail, 0.30) == False
    print("  ✓ gate_check (fail)")


if __name__ == "__main__":
    print("Running overlap tests...")
    test_jaccard_index()
    test_compute_jaccard_overlap()
    test_gate_check()
    print("\nAll tests passed!")
