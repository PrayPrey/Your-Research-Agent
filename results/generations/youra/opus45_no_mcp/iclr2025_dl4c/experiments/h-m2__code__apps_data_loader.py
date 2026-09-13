#!/usr/bin/env python3
"""Load APPS dataset and generate failing samples with real tracebacks."""
import os
import sys
import re
import json
import random
import traceback as tb_module
from typing import List, Dict, Optional, Tuple
from io import StringIO
import signal
from contextlib import contextmanager

from config import U_LINE_ERRORS, U_IGNORE_ERRORS, SEED


class ExecutionTimeout(Exception):
    pass


@contextmanager
def timeout_handler(seconds: int = 5):
    """Context manager for execution timeout."""
    def handler(signum, frame):
        raise ExecutionTimeout("Execution timed out")

    old_handler = signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def extract_traceback_line(exc_info) -> Optional[int]:
    """Extract line number from exception traceback."""
    if exc_info[2] is None:
        return None
    tb_lines = tb_module.extract_tb(exc_info[2])
    if not tb_lines:
        return None
    for frame in reversed(tb_lines):
        if frame.filename == "<string>":
            return frame.lineno
    return tb_lines[-1].lineno if tb_lines else None


def format_traceback_str(exc_info) -> str:
    """Format exception info as traceback string."""
    return "".join(tb_module.format_exception(*exc_info))


def categorize_error(error_type: str) -> str:
    """Categorize error as U_line or U_ignore."""
    if error_type in U_LINE_ERRORS:
        return "U_line"
    if error_type in U_IGNORE_ERRORS:
        return "U_ignore"
    return "unknown"


def safe_exec(code: str, test_input: str = "", timeout: int = 5) -> Tuple[bool, Optional[Dict]]:
    """
    Execute code safely with timeout and capture failure info.
    Returns (success, failure_info).
    """
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        sys.stdin = StringIO(test_input)
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        with timeout_handler(timeout):
            exec(compile(code, "<string>", "exec"), {"__builtins__": __builtins__})

        return True, None

    except ExecutionTimeout:
        return False, {
            "error_type": "TimeoutError",
            "error_category": "U_ignore",
            "traceback": "TimeoutError: Execution exceeded time limit",
            "error_line": None
        }
    except SyntaxError as e:
        return False, {
            "error_type": "SyntaxError",
            "error_category": "U_line",
            "traceback": f'File "<string>", line {e.lineno}\nSyntaxError: {e.msg}',
            "error_line": e.lineno
        }
    except Exception as e:
        exc_info = sys.exc_info()
        error_type = type(e).__name__
        error_line = extract_traceback_line(exc_info)
        traceback_str = format_traceback_str(exc_info)

        return False, {
            "error_type": error_type,
            "error_category": categorize_error(error_type),
            "traceback": traceback_str,
            "error_line": error_line
        }
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def load_apps_dataset(split: str = "train", max_problems: int = 2000):
    """Load APPS dataset from HuggingFace."""
    from datasets import load_dataset

    print(f"Loading APPS dataset (split={split}, max={max_problems})...", flush=True)
    dataset = load_dataset("codeparrot/apps", split=split)

    if max_problems and len(dataset) > max_problems:
        indices = list(range(len(dataset)))
        random.seed(SEED)
        random.shuffle(indices)
        indices = indices[:max_problems]
        dataset = dataset.select(indices)

    return dataset


def generate_code_with_codet5(problem_text: str, tokenizer, model, max_length: int = 256) -> str:
    """Generate code solution using CodeT5-small."""
    import torch

    prompt = f"Generate Python code: {problem_text[:500]}"
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)

    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=1,
            do_sample=True,
            temperature=0.7,
            pad_token_id=tokenizer.pad_token_id
        )

    code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return code


def get_test_inputs(problem: Dict) -> List[str]:
    """Extract test inputs from APPS problem."""
    inputs = []
    input_output_str = problem.get("input_output", "")
    if not input_output_str:
        return [""]

    try:
        io_data = json.loads(input_output_str)
        inputs = io_data.get("inputs", [])
        if isinstance(inputs, list):
            return [str(inp) for inp in inputs[:3]]
    except (json.JSONDecodeError, TypeError):
        pass

    return [""]


def generate_u_ignore_samples(n_samples: int = 100, seed: int = SEED) -> List[Dict]:
    """
    Generate samples that trigger U_ignore errors (RecursionError, TimeoutError, etc.).
    These are rare in model-generated code, so we create targeted patterns.
    The code is realistic (could appear in student submissions) but triggers specific errors.
    """
    random.seed(seed)

    patterns = [
        # RecursionError - infinite recursion
        ("def factorial(n):\n    return n * factorial(n - 1)\n\nprint(factorial(5))",
         "RecursionError"),
        ("def fib(n):\n    return fib(n-1) + fib(n-2)\n\nprint(fib(100))",
         "RecursionError"),
        # RuntimeError - explicit raise
        ("def check_value(x):\n    if x < 0:\n        raise RuntimeError('negative')\n    return x\n\ncheck_value(-1)",
         "RuntimeError"),
        # AssertionError
        ("def validate(x):\n    assert x > 0, 'must be positive'\n    return x\n\nvalidate(-5)",
         "AssertionError"),
        ("data = [1, 2, 3]\nassert len(data) == 5",
         "AssertionError"),
    ]

    samples = []
    for i in range(n_samples):
        pattern_idx = i % len(patterns)
        code, expected_error = patterns[pattern_idx]

        # Add variation
        code_var = code + f"\n# problem {i + 10000}"

        success, failure_info = safe_exec(code_var, "", timeout=2)

        if not success and failure_info and failure_info["error_category"] == "U_ignore":
            samples.append({
                "code": code_var,
                "traceback": failure_info["traceback"],
                "error_line": failure_info["error_line"],
                "actual_bug_line": None,
                "problem_id": i + 10000,
                "error_type": "U_ignore",
                "error_type_specific": failure_info["error_type"]
            })

    return samples


def collect_failing_samples_from_apps(
    n_target: int = 500,
    max_problems: int = 2000,
    split: str = "train",
    seed: int = SEED,
    min_u_ignore: int = 100
) -> List[Dict]:
    """
    Load APPS, generate code with CodeT5-small, execute, collect failures.
    Supplements with targeted U_ignore patterns since they're rare in generated code.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    random.seed(seed)

    # Load model
    print("Loading CodeT5-small model...", flush=True)
    model_name = "Salesforce/codet5-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    if torch.cuda.is_available():
        model = model.cuda()
        print("Using GPU for code generation")

    model.eval()

    # Load dataset
    dataset = load_apps_dataset(split=split, max_problems=max_problems)

    samples = []
    u_line_count = 0
    u_ignore_count = 0

    print(f"Collecting {n_target} failing samples from APPS...", flush=True)

    for idx, problem in enumerate(dataset):
        if len(samples) >= n_target:
            break

        problem_text = problem.get("question", "")
        if not problem_text:
            continue

        code = generate_code_with_codet5(problem_text, tokenizer, model)
        if not code or len(code.strip()) < 10:
            continue

        test_inputs = get_test_inputs(problem)

        for test_input in test_inputs:
            success, failure_info = safe_exec(code, test_input, timeout=3)

            if not success and failure_info:
                category = failure_info["error_category"]

                if category == "unknown":
                    continue

                sample = {
                    "code": code,
                    "traceback": failure_info["traceback"],
                    "error_line": failure_info["error_line"],
                    "actual_bug_line": None,
                    "problem_id": problem.get("problem_id", idx),
                    "error_type": category,
                    "error_type_specific": failure_info["error_type"]
                }
                samples.append(sample)

                if category == "U_line":
                    u_line_count += 1
                else:
                    u_ignore_count += 1

                if (len(samples) % 100) == 0:
                    print(f"  APPS: {len(samples)} samples (U_line={u_line_count}, U_ignore={u_ignore_count})", flush=True)

                break

    print(f"APPS collection done: {len(samples)} samples (U_line={u_line_count}, U_ignore={u_ignore_count})", flush=True)

    # Supplement with U_ignore samples if needed
    if u_ignore_count < min_u_ignore:
        needed = min_u_ignore - u_ignore_count
        print(f"Supplementing with {needed} targeted U_ignore samples...", flush=True)
        u_ignore_samples = generate_u_ignore_samples(needed * 2, seed)[:needed]
        samples.extend(u_ignore_samples)
        u_ignore_count += len(u_ignore_samples)

    print(f"Final: {len(samples)} samples (U_line={u_line_count}, U_ignore={u_ignore_count})", flush=True)
    return samples


if __name__ == "__main__":
    samples = collect_failing_samples_from_apps(n_target=100, max_problems=500)
    print(f"Collected {len(samples)} samples")
    for s in samples[:3]:
        print(f"  {s['error_type']}: {s['error_type_specific']}")
