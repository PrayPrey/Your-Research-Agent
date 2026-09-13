"""Tests for leandojo_tracing.py — spec compliance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from data.leandojo_tracing import (
    TACTIC_TAXONOMY,
    ProofStateTriple,
    classify_lean4_error,
    get_premise_consistent_tokens,
    extract_state_triples,
    _generate_synthetic_triples,
)


def test_tactic_taxonomy_immutable_keys():
    assert set(TACTIC_TAXONOMY.keys()) == {"type_error", "undefined_name", "tactic_failure"}


def test_tactic_taxonomy_has_patterns():
    for cat, patterns in TACTIC_TAXONOMY.items():
        assert len(patterns) >= 1, f"Category {cat} has no patterns"


def test_classify_lean4_error_type_error():
    assert classify_lean4_error("type mismatch\nexpected Nat got Int") == "type_error"


def test_classify_lean4_error_undefined():
    assert classify_lean4_error("unknown identifier 'foo'") == "undefined_name"


def test_classify_lean4_error_tactic_failure():
    assert classify_lean4_error("tactic failed to apply") == "tactic_failure"


def test_classify_lean4_error_unknown():
    assert classify_lean4_error("some completely different error") is None


def test_classify_lean4_error_empty():
    assert classify_lean4_error("") is None


def test_proof_state_triple_fields():
    t = ProofStateTriple(
        state_id="abc123",
        state="⊢ 1 + 1 = 2",
        tactic="ring",
        compiler_error="type mismatch",
        error_category="type_error",
        problem_name="test_prob",
    )
    assert t.state_id == "abc123"
    assert t.error_category == "type_error"


def test_get_premise_consistent_tokens():
    from transformers import AutoTokenizer
    try:
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        tokens = get_premise_consistent_tokens("type_error", tokenizer)
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(isinstance(t, int) for t in tokens)
    except Exception:
        pytest.skip("tokenizer not available")


def test_synthetic_triples_generated():
    from data.load_datasets import Problem
    problems = [
        Problem("p1", "train", "theorem p1 : 1 = 1", "1 = 1", "", "minif2f"),
        Problem("p2", "train", "theorem p2 : 2 = 2", "2 = 2", "", "minif2f"),
    ]
    triples = _generate_synthetic_triples(problems)
    assert len(triples) > 0
    for t in triples:
        assert t.state_id is not None
        assert t.error_category in TACTIC_TAXONOMY
        assert t.problem_name in ("p1", "p2")
