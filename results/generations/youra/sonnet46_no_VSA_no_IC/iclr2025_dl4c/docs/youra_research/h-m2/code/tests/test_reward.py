import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from reward import _execute_code, make_execution_reward


def test_execute_code_pass():
    code = "def add(a, b): return a + b"
    tests = ["assert add(1, 2) == 3", "assert add(0, 0) == 0"]
    assert _execute_code(code, tests) is True


def test_execute_code_fail():
    code = "def add(a, b): return a - b"
    tests = ["assert add(1, 2) == 3"]
    assert _execute_code(code, tests) is False


def test_execute_code_syntax_error():
    code = "def broken(: return"
    tests = ["assert True"]
    assert _execute_code(code, tests) is False


def test_execute_code_timeout():
    code = "import time; time.sleep(100)"
    tests = ["assert True"]
    assert _execute_code(code, tests, timeout=0.2) is False


def test_reward_fn_interface():
    """reward_fn must accept completions, prompts, **kwargs and return list[float]."""
    reward_fn = make_execution_reward(timeout=5.0)
    completions = ["def add(a, b): return a + b", "def add(a, b): return 0"]
    prompts = ["p1", "p2"]
    test_list = [["assert add(1,2)==3"], ["assert add(1,2)==3"]]
    rewards = reward_fn(completions, prompts, test_list=test_list)
    assert rewards == [1.0, 0.0]


def test_reward_fn_empty_tests():
    """Empty test list: any code passes (no assertions to fail)."""
    reward_fn = make_execution_reward()
    rewards = reward_fn(["x = 1"], ["p"], test_list=[[]])
    assert rewards == [1.0]
