"""Tests for score_richness module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import pytest
from score_richness import score_postcondition, verify_mechanism_activated


def test_tier1_simple():
    clauses = ["assert x > 0"]
    tier, score, has_q, has_r, nc = score_postcondition(clauses)
    assert tier == 1
    assert not has_q
    assert not has_r


def test_tier2_structural():
    # Multiple comparison ops → has_relational
    clauses = ["assert 0 < x < 10"]
    tier, score, has_q, has_r, nc = score_postcondition(clauses)
    assert tier == 2
    assert has_r
    assert not has_q


def test_tier3_quantifier():
    clauses = ["assert all(x > 0 for x in lst)"]
    tier, score, has_q, has_r, nc = score_postcondition(clauses)
    assert tier == 3
    assert has_q


def test_tier4_compound():
    clauses = ["assert all(x > 0 for x in lst) and 0 < n < 100"]
    tier, score, has_q, has_r, nc = score_postcondition(clauses)
    assert tier == 4
    assert has_q
    assert has_r


def test_score_formula():
    clauses = ["assert all(x > 0 for x in lst)"]
    tier, score, has_q, has_r, nc = score_postcondition(clauses)
    expected = nc + 3 * has_q + 2 * has_r
    assert abs(score - expected) < 1e-9


def test_malformed_clause_skipped():
    # Malformed clause should not crash
    clauses = ["assert $$invalid$$", "assert x > 0"]
    tier, score, has_q, has_r, nc = score_postcondition(clauses)
    assert tier == 1  # Only second clause processed


def test_empty_clauses():
    tier, score, has_q, has_r, nc = score_postcondition([])
    assert tier == 1
    assert nc == 0


def test_verify_mechanism_activated_pass():
    richness_df = pd.DataFrame({
        "task_id": [f"t{i}" for i in range(4)],
        "tier": [1, 2, 3, 4],
        "score": [1.0, 3.0, 4.0, 7.0],
        "has_quantifier": [False, False, True, True],
        "has_relational": [False, True, False, True],
        "node_count": [1, 3, 4, 7],
    })
    gap_dict = {"t0": 0.1, "t1": 0.2, "t2": 0.3, "t3": 0.4}
    results = {"rho": 0.5, "p_exact": 0.01, "gate_passed": True}
    passed, indicators = verify_mechanism_activated(richness_df, gap_dict, results)
    assert indicators["richness_computed"]
    assert indicators["all_tiers_present"]
    assert indicators["gap_loaded"]
    assert indicators["spearman_computed"]
