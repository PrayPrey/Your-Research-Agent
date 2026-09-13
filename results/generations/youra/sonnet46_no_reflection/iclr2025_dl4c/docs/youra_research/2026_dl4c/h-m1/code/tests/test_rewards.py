import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rewards import (
    run_evalplus_tests,
    execution_reward_binary,
    execution_reward_error_type,
    REWARD_MAP,
)


def test_reward_map_values():
    assert REWARD_MAP[None] == 1.0
    assert REWARD_MAP["logic"] == 0.2
    assert REWARD_MAP["runtime"] == -0.2
    assert REWARD_MAP["syntax"] == -0.5


def test_syntax_error_detected():
    result = run_evalplus_tests(None, "def f(: pass")
    assert result["passed"] is False
    assert result["error_type"] == "syntax"


def test_valid_syntax_no_task_id():
    result = run_evalplus_tests(None, "def f():\n    return 1\n")
    # Without task_id, only syntax checked — should not raise
    assert "passed" in result
    assert "error_type" in result


def test_execution_reward_binary_no_task_id():
    completions = ["def f():\n    return 1\n", "def f(: pass"]
    rewards = execution_reward_binary(completions, ["p1", "p2"], task_ids=[None, None])
    assert rewards[0] == 1.0
    assert rewards[1] == 0.0


def test_execution_reward_error_type_syntax():
    completions = ["def f(: pass"]
    rewards = execution_reward_error_type(completions, ["p"], task_ids=[None])
    assert rewards[0] == REWARD_MAP["syntax"]


def test_execution_reward_error_type_valid():
    completions = ["def f():\n    return 1\n"]
    rewards = execution_reward_error_type(completions, ["p"], task_ids=[None])
    # No task_id, valid syntax -> reward for None (passed)
    assert rewards[0] == REWARD_MAP[None]


def test_execution_reward_binary_task_ids_from_kwargs():
    completions = ["def f(: pass"]
    rewards = execution_reward_binary(completions, ["p"], task_ids=None, task_ids_kwarg=[None])
    # Falls back to None task_ids list
    assert len(rewards) == 1


def test_run_evalplus_tests_returns_dict():
    result = run_evalplus_tests(None, "x = 1")
    assert isinstance(result, dict)
    assert "passed" in result
    assert "error_type" in result
