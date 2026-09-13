"""Tests for data_loader.py — E1 spec compliance."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_loader import compute_exact_match, format_few_shot_prompt, normalize_answer


def test_normalize_answer_lowercase():
    assert normalize_answer("Paris") == "paris"


def test_normalize_answer_articles():
    assert normalize_answer("the Eiffel Tower") == "eiffel tower"
    assert normalize_answer("a cat") == "cat"


def test_normalize_answer_punctuation():
    assert normalize_answer("hello, world!") == "hello world"


def test_compute_exact_match_correct():
    assert compute_exact_match("paris", ["Paris", "paris"]) == 1


def test_compute_exact_match_incorrect():
    assert compute_exact_match("london", ["Paris"]) == 0


def test_compute_exact_match_normalized():
    assert compute_exact_match("the united states", ["United States"]) == 1


def test_format_few_shot_prompt_contains_question():
    examples = [{"question": "Q1?", "answer": "A1"}]
    prompt = format_few_shot_prompt("What is X?", examples, n_shot=1)
    assert "What is X?" in prompt
    assert "Q1?" in prompt
    assert "A1" in prompt
    assert prompt.endswith("A:")


def test_format_few_shot_prompt_zero_shot():
    prompt = format_few_shot_prompt("What is X?", [], n_shot=0)
    assert "What is X?" in prompt
    assert prompt.endswith("A:")


def test_format_few_shot_prompt_n_shot_limit():
    examples = [{"question": f"Q{i}?", "answer": f"A{i}"} for i in range(10)]
    prompt = format_few_shot_prompt("Test?", examples, n_shot=3)
    # Should contain exactly 3 few-shot Q/A pairs plus the test question
    lines = [l for l in prompt.split("\n") if l.startswith("Q:")]
    assert len(lines) == 4  # 3 examples + 1 test question
