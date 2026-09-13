import subprocess
from typing import Optional


def execute_code(code: str, test_input: str, expected_output: str, timeout: int = 5) -> bool:
    """Run code in subprocess, compare stdout to expected_output. Returns pass/fail."""
    try:
        result = subprocess.run(
            ["python", "-c", code],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip() == expected_output.strip()
    except (subprocess.TimeoutExpired, Exception):
        return False


def binary_reward(completion: str, test_cases: list) -> float:
    """Return 1.0 if all test cases pass, else 0.0."""
    if not test_cases:
        return 0.0
    for tc in test_cases:
        if not execute_code(completion, tc.get("input", ""), tc.get("output", "")):
            return 0.0
    return 1.0


def ratio_reward(completion: str, test_cases: list) -> float:
    """Return k/n where k = number of passing test cases, n = total."""
    if not test_cases:
        return 0.0
    passes = sum(
        execute_code(completion, tc.get("input", ""), tc.get("output", ""))
        for tc in test_cases
    )
    return passes / len(test_cases)


def make_reward_fn(mode: str):
    """
    mode: 'binary' | 'ratio'
    Returns trl-compatible reward function signature.
    """
    base_fn = ratio_reward if mode == "ratio" else binary_reward

    def reward_fn(completions=None, prompts=None, test_cases=None, **kwargs) -> list:
        if completions is None:
            return []
        results = []
        for i, completion in enumerate(completions):
            tc = (test_cases[i] if test_cases and i < len(test_cases) else []) or []
            # tc may be a string if serialized; parse if needed
            if isinstance(tc, str):
                import json
                try:
                    tc = json.loads(tc)
                except Exception:
                    tc = []
            try:
                r = base_fn(completion, tc)
            except Exception:
                r = 0.0
            results.append(r)
        return results

    reward_fn.__name__ = f"{mode}_reward_fn"
    return reward_fn
