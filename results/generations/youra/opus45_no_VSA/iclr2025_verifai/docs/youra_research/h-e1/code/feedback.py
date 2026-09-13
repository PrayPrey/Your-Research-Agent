"""Feedback generation: static analysis and execution feedback with deterministic truncation."""
import subprocess
import tempfile
import os
from typing import List
from sandbox import ExecResult


def count_tokens(text: str) -> int:
    """Approximate token count (4 chars ~ 1 token)."""
    return len(text) // 4 + 1


def truncate_deterministic(items: List[str], token_budget: int) -> str:
    """Greedily join items (pre-sorted by priority) until budget hit."""
    out = []
    used = 0
    for item in items:
        cost = count_tokens(item)
        if used + cost > token_budget:
            break
        out.append(item)
        used += cost
    return "\n".join(out)


def get_static_feedback(code: str, token_budget: int = 500) -> str:
    """Run pylint+mypy on code, return truncated feedback."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        temp_path = f.name

    messages = []
    try:
        # Pylint
        result = subprocess.run(
            ["pylint", "--output-format=text", "--score=no", temp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        for line in result.stdout.split("\n"):
            if line.strip() and not line.startswith("*"):
                severity = 0 if ": E" in line else (1 if ": W" in line else 2)
                messages.append((severity, line.strip()))

        # Mypy
        result = subprocess.run(
            ["mypy", "--no-error-summary", temp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        for line in result.stdout.split("\n"):
            if line.strip():
                severity = 0 if "error:" in line else 1
                messages.append((severity, line.strip()))

    except Exception:
        pass
    finally:
        os.unlink(temp_path)

    # Sort by severity (errors first), stable sort preserves order
    messages.sort(key=lambda m: m[0])
    return truncate_deterministic([m[1] for m in messages], token_budget)


def get_execution_feedback(exec_result: ExecResult, token_budget: int = 500) -> str:
    """Format execution result into truncated feedback."""
    items = []

    if exec_result.traceback:
        items.append(f"ERROR: {exec_result.traceback}")

    if exec_result.stderr and exec_result.stderr != exec_result.traceback:
        items.append(f"STDERR: {exec_result.stderr}")

    if exec_result.stdout:
        items.append(f"OUTPUT: {exec_result.stdout}")

    if exec_result.passed:
        items.append("All tests passed.")
    else:
        items.insert(0, "Tests FAILED.")

    return truncate_deterministic(items, token_budget)


def build_feedback_prompt(static_fb: str, exec_fb: str, condition: str) -> str:
    """Build feedback prompt with A/B ordering."""
    if condition == "A":  # static -> execution
        return f"Static Analysis Feedback:\n{static_fb}\n\nExecution Feedback:\n{exec_fb}"
    else:  # B: execution -> static
        return f"Execution Feedback:\n{exec_fb}\n\nStatic Analysis Feedback:\n{static_fb}"
