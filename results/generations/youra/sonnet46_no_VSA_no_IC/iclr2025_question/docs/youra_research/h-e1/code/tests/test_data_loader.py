"""Tests for data_loader module."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from data_loader import score_answer, get_dataset, _normalize_answer


def test_normalize_answer():
    assert _normalize_answer("The Cat") == "cat"
    assert _normalize_answer("a dog.") == "dog"


def test_score_answer_exact_match_correct():
    record = {"dataset": "trivia_qa", "reference_answers": ["Paris", "paris"]}
    assert score_answer("paris", record) == 1


def test_score_answer_exact_match_wrong():
    record = {"dataset": "nq", "reference_answers": ["Paris"]}
    assert score_answer("London", record) == 0


def test_score_answer_rouge_threshold():
    record = {
        "dataset": "truthful_qa",
        "reference_answers": ["The Earth is round"],
    }
    # Perfect match -> 1
    assert score_answer("The Earth is round", record) == 1
    # Unrelated -> 0
    assert score_answer("unrelated answer xyz", record) == 0


def test_get_dataset_raises_unknown():
    with pytest.raises(ValueError):
        get_dataset("unknown_dataset")


def test_load_truthful_qa_structure():
    """Smoke test: load first 5 samples and verify structure."""
    from data_loader import load_truthful_qa
    records = load_truthful_qa()
    assert len(records) > 0
    for r in records[:5]:
        assert "question" in r
        assert "reference_answers" in r
        assert isinstance(r["reference_answers"], list)
        assert len(r["reference_answers"]) > 0
        assert r["label"] is None  # labels resolved at inference time
