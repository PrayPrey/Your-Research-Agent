"""Tests for data.py module."""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import load_humaneval, load_mbpp, format_prompt, get_test_cases


def test_load_humaneval():
    """Test HumanEval loading returns 164 problems."""
    problems = load_humaneval()
    assert len(problems) == 164, f"Expected 164 problems, got {len(problems)}"
    assert "task_id" in problems[0]
    assert "prompt" in problems[0]
    assert "test" in problems[0]


def test_load_mbpp():
    """Test MBPP loading returns 500 problems."""
    problems = load_mbpp()
    assert len(problems) == 500, f"Expected 500 problems, got {len(problems)}"
    assert "task_id" in problems[0]
    assert "text" in problems[0]
    assert "test_list" in problems[0]


def test_format_prompt_humaneval():
    """Test prompt formatting for HumanEval."""
    problem = {
        "task_id": "HumanEval/0",
        "prompt": "def foo():\n    '''Example'''\n",
    }
    prompt = format_prompt(problem, "humaneval")
    assert "[INST]" in prompt
    assert "def foo()" in prompt


def test_format_prompt_mbpp():
    """Test prompt formatting for MBPP."""
    problem = {
        "task_id": "mbpp/1",
        "text": "Write a function to add two numbers.",
    }
    prompt = format_prompt(problem, "mbpp")
    assert "[INST]" in prompt
    assert "add two numbers" in prompt


def test_get_test_cases_humaneval():
    """Test test case extraction for HumanEval."""
    problem = {"task_id": "HumanEval/0", "test": "assert foo() == 1"}
    cases = get_test_cases(problem, "humaneval")
    assert len(cases) == 1
    assert "assert" in cases[0]


def test_get_test_cases_mbpp():
    """Test test case extraction for MBPP."""
    problem = {"task_id": "mbpp/1", "test_list": ["assert f(1) == 2", "assert f(2) == 4"]}
    cases = get_test_cases(problem, "mbpp")
    assert len(cases) == 2
