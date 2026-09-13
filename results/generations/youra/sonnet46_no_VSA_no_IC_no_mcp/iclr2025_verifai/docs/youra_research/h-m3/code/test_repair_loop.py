"""Unit tests for h-m3 repair_loop."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from repair_loop import (_count_tokens, _build_prompt_a, _build_prompt_b, _make_key)


def test_count_tokens():
    assert _count_tokens("hello world") > 0

def test_build_prompt_b_includes_mypy():
    problem = {"prompt": "def foo(): pass"}
    prompt = _build_prompt_b(problem, "def foo(): pass", "exec failed", "error: type mismatch")
    assert "mypy" in prompt.lower() or "type checker" in prompt.lower()

def test_condition_b_longer_than_a():
    problem = {"prompt": "def foo(): pass"}
    pa = _build_prompt_a(problem, "def foo(): pass", "exec failed")
    pb = _build_prompt_b(problem, "def foo(): pass", "exec failed", "error: X")
    assert len(pb) > len(pa)

def test_checkpoint_key_unique():
    key = _make_key("humaneval+", 42, "A", "HumanEval/0")
    assert "humaneval+" in key and "42" in key and "__A__" in key

if __name__ == "__main__":
    test_count_tokens()
    test_build_prompt_b_includes_mypy()
    test_condition_b_longer_than_a()
    test_checkpoint_key_unique()
    print("All repair_loop tests passed.")
