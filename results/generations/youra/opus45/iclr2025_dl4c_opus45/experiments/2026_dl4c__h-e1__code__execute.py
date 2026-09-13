"""Execution and error capture using EvalPlus sandbox."""

import json
import os
import signal
import traceback
from typing import Dict, List, Optional

from tqdm import tqdm


class TimeoutError(Exception):
    """Custom timeout exception."""
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")


def execute_sample(
    task_id: str,
    completion: str,
    problem: dict,
    entry_point: str,
    timeout: int = 5,
) -> Optional[str]:
    """Execute completion against test suite.

    Args:
        task_id: The problem ID
        completion: Generated code completion
        problem: Problem dict with test code
        entry_point: Function entry point name
        timeout: Execution timeout in seconds

    Returns:
        None on PASS, error_trace str on failure.
    """
    # Build full code: completion + test
    # The completion should define the function with name entry_point
    full_code = completion + "\n\n" + problem.get("test", "")

    # Execute with timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        # Create isolated namespace
        exec_globals = {}
        exec(full_code, exec_globals)
        signal.alarm(0)  # Cancel alarm
        return None  # PASS

    except TimeoutError:
        signal.alarm(0)
        return "TimeoutError: Execution timed out"

    except Exception as e:
        signal.alarm(0)
        return f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"


def execute_all_samples(
    samples: List[dict],
    problems: Dict[str, dict],
    timeout: int = 5,
) -> List[dict]:
    """Execute all samples. Adds error_trace and status fields.

    Args:
        samples: List of sample dicts with completion
        problems: Dict mapping task_id to problem dict
        timeout: Execution timeout per sample

    Returns:
        List of dicts: [{task_id, model, sample_idx, completion, error_trace, status}]
        status: "pass" | "fail"
    """
    results = []

    for sample in tqdm(samples, desc="Executing samples"):
        task_id = sample["task_id"]
        problem = problems.get(task_id, {})
        entry_point = sample.get("entry_point", problem.get("entry_point", ""))

        error_trace = execute_sample(
            task_id=task_id,
            completion=sample["completion"],
            problem=problem,
            entry_point=entry_point,
            timeout=timeout
        )

        results.append({
            "task_id": task_id,
            "model": sample["model"],
            "sample_idx": sample["sample_idx"],
            "completion": sample["completion"],
            "error_trace": error_trace,
            "status": "pass" if error_trace is None else "fail"
        })

    pass_count = sum(1 for r in results if r["status"] == "pass")
    fail_count = len(results) - pass_count
    print(f"Execution complete: {pass_count} pass, {fail_count} fail ({100*pass_count/len(results):.1f}% pass rate)")

    return results


def save_execution_results(results: List[dict], path: str) -> None:
    """Save to outputs/execution_results.json."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} execution results to {path}")


def load_execution_results(path: str) -> List[dict]:
    """Load execution results from JSON file."""
    with open(path, "r") as f:
        return json.load(f)
