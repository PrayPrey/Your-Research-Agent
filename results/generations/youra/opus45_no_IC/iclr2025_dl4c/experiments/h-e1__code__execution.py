"""Execution sandbox, reward computation, and trace collection."""

import sys
import ast
import signal
from typing import List, Set, Tuple
from contextlib import contextmanager


class TimeoutError(Exception):
    pass


@contextmanager
def time_limit(seconds: int = 5):
    """Context manager for timeout."""
    def signal_handler(signum, frame):
        raise TimeoutError("Execution timed out")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def check_compiles(code: str) -> bool:
    """Check if code compiles without syntax errors."""
    try:
        compile(code, "<string>", "exec")
        return True
    except SyntaxError:
        return False


def compute_reward(code: str, test_cases: List[str], feedback_type: str) -> float:
    """
    Compute reward based on feedback type.

    Args:
        code: Generated code string
        test_cases: List of test case strings
        feedback_type: "compile", "test", or "combined"

    Returns:
        reward: +1.0 pass, -0.3 fail, -0.6 runtime, -1.0 compile
    """
    if feedback_type == "compile":
        return 1.0 if check_compiles(code) else -1.0

    if not check_compiles(code):
        return -1.0

    test_code = "\n".join(test_cases) if isinstance(test_cases, list) else test_cases
    full_code = code + "\n" + test_code

    try:
        with time_limit(5):
            sandbox_globals = {"__builtins__": __builtins__}
            exec(full_code, sandbox_globals)
        return 1.0
    except AssertionError:
        return -0.3
    except TimeoutError:
        return -0.6
    except Exception:
        return -0.6


def collect_execution_trace(code: str, test_cases: List[str]) -> Set[int]:
    """
    Collect executed line numbers via sys.settrace.

    Args:
        code: Code to trace
        test_cases: Test cases to run

    Returns:
        Set of executed line numbers (1-indexed)
    """
    executed_lines: Set[int] = set()

    def trace_func(frame, event, arg):
        if event == "line":
            executed_lines.add(frame.f_lineno)
        return trace_func

    test_code = "\n".join(test_cases) if isinstance(test_cases, list) else test_cases
    full_code = code + "\n" + test_code

    if not check_compiles(full_code):
        return executed_lines

    sys.settrace(trace_func)
    try:
        with time_limit(5):
            sandbox_globals = {"__builtins__": __builtins__}
            exec(full_code, sandbox_globals)
    except Exception:
        pass
    finally:
        sys.settrace(None)

    return executed_lines


def map_tokens_to_lines(token_ids, code: str, tokenizer) -> List[int]:
    """
    Map token positions to source line numbers.

    Args:
        token_ids: Tensor of token IDs [seq_len]
        code: Source code string
        tokenizer: HuggingFace tokenizer

    Returns:
        List of line numbers (1-indexed), one per token
    """
    from bisect import bisect_right

    encoding = tokenizer(code, return_offsets_mapping=True, add_special_tokens=False)
    offsets = encoding.get("offset_mapping", [])

    if not offsets:
        return [1] * len(token_ids)

    line_starts = [0]
    for i, char in enumerate(code):
        if char == "\n":
            line_starts.append(i + 1)

    token_to_line = []
    for start, end in offsets:
        if start is None or end is None:
            token_to_line.append(1)
        else:
            line_num = bisect_right(line_starts, start)
            token_to_line.append(line_num)

    seq_len = len(token_ids) if hasattr(token_ids, "__len__") else token_ids.shape[0]
    while len(token_to_line) < seq_len:
        token_to_line.append(token_to_line[-1] if token_to_line else 1)

    return token_to_line[:seq_len]
