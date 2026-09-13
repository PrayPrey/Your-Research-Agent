"""Tests for dpo_pairs.py — spec compliance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from data.leandojo_tracing import ProofStateTriple
from training.dpo_pairs import (
    DPOPair,
    build_pairs_condition_A,
    build_pairs_condition_B,
    build_pairs_condition_P,
    validate_state_alignment,
    build_all_conditions,
)


def _make_triples():
    """Create minimal test triples."""
    triples = []
    for i in range(5):
        triples.append(ProofStateTriple(
            state_id=f"state_{i}",
            state=f"⊢ goal_{i}",
            tactic="ring" if i % 2 == 0 else "simp",
            compiler_error=f"type mismatch error {i}" if i % 2 != 0 else None,
            error_category="type_error" if i % 2 != 0 else None,
            problem_name=f"prob_{i % 3}",
        ))
    return triples


def test_build_pairs_condition_A():
    triples = _make_triples()
    pairs = build_pairs_condition_A(triples)
    assert isinstance(pairs, list)
    for p in pairs:
        assert p.condition == "A"
        assert p.state_id_chosen == p.state_id_rejected  # state alignment


def test_build_pairs_condition_B():
    triples = _make_triples()
    pairs = build_pairs_condition_B(triples)
    assert isinstance(pairs, list)
    for p in pairs:
        assert p.condition == "B"
        assert p.error_msg == ""  # no error info for condition B
        assert p.state_id_chosen == p.state_id_rejected


def test_build_pairs_condition_P():
    triples = _make_triples()
    pairs = build_pairs_condition_P(triples)
    assert isinstance(pairs, list)
    for p in pairs:
        assert p.condition == "P"
        assert p.state_id_chosen == p.state_id_rejected


def test_validate_state_alignment_passes():
    triples = _make_triples()
    pairs = build_pairs_condition_A(triples)
    validate_state_alignment(pairs)  # Should not raise


def test_validate_state_alignment_fails():
    pair = DPOPair(
        state_id_chosen="s1",
        state_id_rejected="s2",  # mismatch!
        state="⊢ goal",
        chosen_tactic="ring",
        rejected_tactic="simp",
        error_msg="error",
        error_category="type_error",
        condition="A",
    )
    with pytest.raises(ValueError, match="State alignment violation"):
        validate_state_alignment([pair])


def test_build_all_conditions():
    triples = _make_triples()
    all_conds = build_all_conditions(triples)
    assert set(all_conds.keys()) == {"A", "B", "P"}
    for cond, pairs in all_conds.items():
        assert isinstance(pairs, list)
        for p in pairs:
            assert p.state_id_chosen == p.state_id_rejected
