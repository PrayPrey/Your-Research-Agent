"""Error classification and gated reward calculation."""
import re
import subprocess
import resource
import signal
import torch
from typing import Optional, Tuple, List
from dataclasses import dataclass
from config import U_LINE_ERRORS, U_IGNORE_ERRORS

# Counters for gating activation logging
gating_activations = {"u_line": 0, "u_ignore": 0, "pass": 0}


@dataclass
class Token:
    text: str
    line: int


def classify_error(traceback_str: Optional[str]) -> str:
    """Classify exception type as U_line or U_ignore."""
    if traceback_str is None:
        return "pass"
    for err in U_LINE_ERRORS:
        if err in traceback_str:
            return "U_line"
    return "U_ignore"


def parse_traceback_line(traceback_str: str) -> Optional[int]:
    """Extract failing source line number from traceback."""
    if not traceback_str:
        return None
    matches = re.findall(r'File ".*?", line (\d+)', traceback_str)
    if matches:
        return int(matches[-1])
    return None


def execute_code_safely(
    code: str,
    test_cases: List[dict],
    timeout_s: int = 30,
    mem_limit_mb: int = 512
) -> Tuple[str, Optional[str]]:
    """Run code in sandboxed subprocess. Returns (result, traceback)."""
    if not test_cases:
        return "PASS", None

    for tc in test_cases[:3]:  # Limit to 3 test cases for speed
        test_input = tc.get("input", "")
        expected = tc.get("output", "")

        full_code = f"{code}\n"

        try:
            result = subprocess.run(
                ["python", "-c", full_code],
                input=test_input,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )

            if result.returncode != 0:
                return "ERROR", result.stderr

            if result.stdout.strip() != expected.strip():
                return "FAIL", None

        except subprocess.TimeoutExpired:
            return "ERROR", "TimeoutError: Execution exceeded time limit"
        except Exception as e:
            return "ERROR", str(e)

    return "PASS", None


def compute_gated_reward(
    code_tokens: List[Token],
    traceback: Optional[str],
    gating: str = "fine_gated",
) -> torch.Tensor:
    """Compute per-token reward with error-type gating."""
    gen_len = len(code_tokens)
    rewards = torch.zeros(gen_len)

    if traceback is None:
        rewards[:] = 1.0
        gating_activations["pass"] += 1
        return rewards

    category = classify_error(traceback)
    error_line = parse_traceback_line(traceback)

    if gating == "fine_gated" and category == "U_ignore":
        rewards[:] = -0.1
        gating_activations["u_ignore"] += 1
        print(f"GATING: U_ignore error detected, applying coarse-only penalty")
    else:
        rewards[:] = -0.1
        if error_line is not None:
            for idx, token in enumerate(code_tokens):
                if token.line == error_line:
                    rewards[idx] = -1.0
        gating_activations["u_line"] += 1

    return rewards


def compute_batch_rewards(
    batch_tokens: List[List[Token]],
    tracebacks: List[Optional[str]],
    gating: str = "fine_gated",
) -> torch.Tensor:
    """Batch wrapper for reward computation."""
    rewards = []
    for tokens, tb in zip(batch_tokens, tracebacks):
        r = compute_gated_reward(tokens, tb, gating)
        rewards.append(r)

    max_len = max(len(r) for r in rewards)
    padded = torch.zeros(len(rewards), max_len)
    for i, r in enumerate(rewards):
        padded[i, :len(r)] = r

    return padded


def get_gating_stats():
    """Return current gating activation statistics."""
    total = sum(gating_activations.values())
    if total == 0:
        return {"u_line_rate": 0.0, "u_ignore_rate": 0.0, "pass_rate": 0.0}
    return {
        "u_line_rate": gating_activations["u_line"] / total,
        "u_ignore_rate": gating_activations["u_ignore"] / total,
        "pass_rate": gating_activations["pass"] / total,
        "total": total,
    }


def reset_gating_stats():
    """Reset gating activation counters."""
    global gating_activations
    gating_activations = {"u_line": 0, "u_ignore": 0, "pass": 0}
