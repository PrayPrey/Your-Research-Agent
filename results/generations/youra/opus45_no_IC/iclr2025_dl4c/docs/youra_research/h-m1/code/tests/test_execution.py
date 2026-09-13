"""Tests for execution.py module."""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution import check_compiles, compute_reward, collect_execution_trace


def test_check_compiles_valid():
    """Test valid Python code compiles."""
    code = "def foo():\n    return 1"
    assert check_compiles(code) is True


def test_check_compiles_invalid():
    """Test invalid Python code fails compilation."""
    code = "def foo(\n    return 1"
    assert check_compiles(code) is False


def test_compute_reward_compile_pass():
    """Test compile feedback with valid code."""
    code = "def foo(): return 1"
    reward = compute_reward(code, [], "compile")
    assert reward == 1.0


def test_compute_reward_compile_fail():
    """Test compile feedback with invalid code."""
    code = "def foo(:"
    reward = compute_reward(code, [], "compile")
    assert reward == -1.0


def test_compute_reward_test_pass():
    """Test test feedback with passing code."""
    code = "def foo(): return 1"
    tests = ["assert foo() == 1"]
    reward = compute_reward(code, tests, "test")
    assert reward == 1.0


def test_compute_reward_test_fail():
    """Test test feedback with failing assertion."""
    code = "def foo(): return 2"
    tests = ["assert foo() == 1"]
    reward = compute_reward(code, tests, "test")
    assert reward == -0.3


def test_collect_execution_trace():
    """Test execution trace collection."""
    code = """def foo():
    x = 1
    return x"""
    tests = ["foo()"]
    executed = collect_execution_trace(code, tests)
    assert len(executed) > 0
    assert isinstance(executed, set)
