"""MBPP dataset loading and prompt formatting for H-E1."""

from datasets import load_dataset
from config import ExperimentConfig


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
    """Format problem into MBPP standard prompt.

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
