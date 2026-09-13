"""Binary unit-test execution reward for GRPO training."""

import subprocess
import sys
import json
import tempfile
import os
from typing import Any

# Import CONFIG for reward parameters
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG

REWARD_TIMEOUT: float = CONFIG["reward_timeout"]
REWARD_EPSILON: float = CONFIG["reward_epsilon"]
REWARD_PASS: float = 1.0
REWARD_FAIL: float = 0.0

_RUNNER_TEMPLATE = """
import sys, json, signal

def timeout_handler(signum, frame):
    raise TimeoutError("Test timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm({timeout})

try:
{code_indented}

    results = []
    test_cases = {test_cases}
    for tc in test_cases:
        inp = tc.get("input", "")
        expected = tc.get("output", "")
        try:
            import io
            old_stdin = sys.stdin
            sys.stdin = io.StringIO(inp)
            import io as _io
            out = _io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = out
            # Try to call solve or main if defined
            if 'solve' in dir():
                solve()
            elif 'main' in dir():
                main()
            sys.stdout = old_stdout
            sys.stdin = old_stdin
            actual = out.getvalue().strip()
            results.append(actual == expected.strip())
        except Exception as e:
            results.append(False)
    print(json.dumps(results))
except Exception as e:
    print(json.dumps([False]))
"""


def run_unit_tests(code: str, test_cases: list[dict], timeout: float = REWARD_TIMEOUT) -> bool:
    """Execute code against test_cases. Returns True if all tests pass."""
    if not test_cases:
        return False

    # Indent code for embedding in runner
    code_indented = "\n".join("    " + line for line in code.split("\n"))
    timeout_int = max(1, int(timeout))

    runner = _RUNNER_TEMPLATE.format(
        timeout=timeout_int,
        code_indented=code_indented,
        test_cases=json.dumps(test_cases[:3]),  # Limit to first 3 tests for speed
    )

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(runner)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout + 2,
        )
        os.unlink(tmp_path)

        if result.returncode != 0:
            return False

        output = result.stdout.strip()
        if not output:
            return False

        results = json.loads(output)
        return all(results) if results else False

    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return False


def _parse_test_cases(example: dict) -> list[dict]:
    """Extract test cases from tokenized example (normalized test_cases_json field)."""
    # New unified format: test_cases_json is a JSON string set by preprocessing.py
    tc_json = example.get("test_cases_json", "")
    if tc_json:
        try:
            test_cases = json.loads(tc_json)
            if isinstance(test_cases, list):
                return test_cases[:3]
        except (json.JSONDecodeError, TypeError):
            pass
    return []


def execution_reward_fn(completions: list[str], prompts: list[Any], **kwargs) -> list[float]:
    """TRL reward_funcs callable: (completions, prompts, **kwargs) -> list[float].

    completions: list of generated code strings (one per sample in batch)
    prompts: list of prompt dicts or strings
    kwargs: may contain 'examples' with original dataset examples
    """
    rewards = []
    examples = kwargs.get("examples", [{}] * len(completions))

    for completion, example in zip(completions, examples):
        if not isinstance(example, dict):
            example = {}
        test_cases = _parse_test_cases(example)
        if test_cases:
            passed = run_unit_tests(completion, test_cases)
            rewards.append(REWARD_PASS if passed else REWARD_FAIL)
        else:
            rewards.append(REWARD_FAIL)

    return rewards


def compute_reward_density(rewards_group: list[float]) -> float:
    """Returns 1.0 if std(rewards_group) > 0, else 0.0.

    A non-zero std means the group has mixed outcomes (some pass, some fail),
    which produces informative GRPO advantage estimates.
    """
    if not rewards_group or len(rewards_group) < 2:
        return 0.0
    mean = sum(rewards_group) / len(rewards_group)
    variance = sum((r - mean) ** 2 for r in rewards_group) / len(rewards_group)
    std = variance ** 0.5
    return 1.0 if std > REWARD_EPSILON else 0.0
