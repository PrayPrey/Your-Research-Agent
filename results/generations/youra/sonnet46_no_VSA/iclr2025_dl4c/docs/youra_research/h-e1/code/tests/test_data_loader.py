"""Tests for data_loader.py — spec compliance."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from h_e1.data_loader import extract_text, EQUAL_MIX_PER_SOURCE


def test_extract_text_humaneval():
    ex = {"prompt": "def add(a, b):", "canonical_solution": "    return a + b"}
    result = extract_text(ex, "humaneval_train")
    assert "def add" in result
    assert "return" in result


def test_extract_text_mbpp():
    ex = {"text": "Write a function", "code": "def foo(): pass"}
    result = extract_text(ex, "mbpp_train")
    assert "foo" in result


def test_extract_text_leetcode():
    ex = {"question_title": "Two Sum", "python_solution": "def twoSum(): pass"}
    result = extract_text(ex, "leetcode")
    assert "Two Sum" in result


def test_equal_mix_per_source_value():
    assert EQUAL_MIX_PER_SOURCE == 164


def test_extract_text_returns_string():
    ex = {"prompt": "test", "canonical_solution": "pass"}
    result = extract_text(ex, "humaneval_plus")
    assert isinstance(result, str)
    assert len(result) > 0
