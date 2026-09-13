"""reward.py — E-2: Fraction-of-tests reward function for H-E1"""
import json
import os
import subprocess
import tempfile


def fraction_reward_fn(
    completions: list,
    prompts: list,
    metadata: list,
    **kwargs,
) -> list:
    """
    Reward = passed_tests / total_tests for each completion.
    Returns floats in [0.0, 1.0].
    """
    rewards = []
    for code, meta in zip(completions, metadata):
        if isinstance(meta, dict):
            raw = meta.get("test_cases", "[]")
        else:
            raw = "[]"
        try:
            test_cases = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            test_cases = []

        if not test_cases:
            rewards.append(0.0)
            continue

        passed = 0
        for item in test_cases:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                stdin, expected = item
            else:
                continue
            try:
                actual = _execute_code(code, str(stdin), timeout=3.0)
                if actual.strip() == str(expected).strip():
                    passed += 1
            except Exception:
                pass

        rewards.append(passed / len(test_cases))
    return rewards


def _execute_code(code: str, stdin: str, timeout: float = 3.0) -> str:
    """Execute code in subprocess with stdin. Returns stdout."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        proc = subprocess.run(
            ["python", fname],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.stdout
    finally:
        try:
            os.unlink(fname)
        except OSError:
            pass
