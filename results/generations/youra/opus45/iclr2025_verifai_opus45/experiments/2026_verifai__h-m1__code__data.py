"""Data loading module for H-M1: Load H-E1 results and MBPP dataset."""

import json
import re
from typing import Optional
from datasets import load_dataset

from config import RepairConfig, ExperimentConfig


def load_runtime_error_cases(config: RepairConfig) -> list[dict]:
    """Load runtime error cases from H-E1 execution_results.json.

    Args:
        config: RepairConfig with h_e1_results_path

    Returns:
        List of dicts: {task_id, generated_code, category, stderr}
        Filtered to category == 'runtime_error' only.
    """
    with open(config.h_e1_results_path, "r") as f:
        all_results = json.load(f)

    runtime_cases = [
        r for r in all_results
        if r.get("category") == "runtime_error"
    ]

    print(f"Loaded {len(runtime_cases)} runtime error cases from H-E1")
    return runtime_cases


def load_mbpp_index(config: RepairConfig) -> dict[int, dict]:
    """Load MBPP test split and return dict keyed by task_id.

    Args:
        config: RepairConfig with mbpp_dataset_name, task_id_min/max

    Returns:
        Dict mapping task_id to {text, test_list, test_setup_code}
    """
    # Use simple mbpp loading (same as H-E1)
    dataset = load_dataset("mbpp", split="test")

    mbpp_index = {}
    for item in dataset:
        task_id = item["task_id"]
        if config.task_id_min <= task_id <= config.task_id_max:
            mbpp_index[task_id] = {
                "text": item["text"],
                "test_list": item["test_list"],
                "test_setup_code": item.get("test_setup_code", ""),
            }

    print(f"Loaded {len(mbpp_index)} MBPP tasks (IDs {config.task_id_min}-{config.task_id_max})")
    return mbpp_index


def parse_error_info(stderr: str) -> dict:
    """Parse stderr string into structured error_info dict.

    Args:
        stderr: Raw stderr output from execution

    Returns:
        Dict with {type, message, line, traceback}
    """
    if not stderr:
        return {
            "type": "Unknown",
            "message": "",
            "line": None,
            "traceback": "",
        }

    lines = stderr.strip().split("\n")
    error_type = "Unknown"
    error_message = ""
    error_line: Optional[int] = None

    # Find the last error line (e.g., "TypeError: unsupported operand...")
    for line in reversed(lines):
        if "Error:" in line or "Exception:" in line:
            parts = line.split(":", 1)
            error_type = parts[0].strip()
            error_message = parts[1].strip() if len(parts) > 1 else ""
            break

    # Extract line number from traceback
    # Pattern: 'File "<string>", line X'
    line_pattern = r'File ["\']<string>["\'], line (\d+)'
    matches = re.findall(line_pattern, stderr)
    if matches:
        error_line = int(matches[-1])  # Take last match (closest to error)

    return {
        "type": error_type,
        "message": error_message,
        "line": error_line,
        "traceback": stderr,
    }


# H-E1 compatibility functions below

def load_mbpp_test(config: ExperimentConfig) -> list[dict]:
    """Load MBPP test split (task IDs 11-510, 500 problems).

    Returns:
        List of dicts with keys: task_id, text, code, test_list
    """
    dataset = load_dataset("mbpp", split="test")

    # Filter to task IDs 11-510 (standard test split)
    problems = []
    for item in dataset:
        task_id = item["task_id"]
        if config.task_id_min <= task_id <= config.task_id_max:
            problems.append({
                "task_id": task_id,
                "text": item["text"],
                "code": item["code"],
                "test_list": item["test_list"],
            })

    # Sort by task_id for reproducibility
    problems.sort(key=lambda x: x["task_id"])

    assert len(problems) == 500, f"Expected 500 problems, got {len(problems)}"
    return problems


def format_prompt(problem: dict) -> str:
    """Format problem into MBPP standard prompt (H-E1 compatibility).

    Args:
        problem: Dict with 'text' and 'test_list' keys

    Returns:
        Formatted prompt string
    """
    tests_str = "\n".join(problem["test_list"])
    prompt = f"""You are an expert Python programmer, and here is your task: {problem["text"]}
Your code should pass these tests:

{tests_str}

[BEGIN]
"""
    return prompt
