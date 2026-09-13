"""Data loading for HumanEval and MBPP datasets."""

from datasets import load_dataset
from typing import List, Dict


def load_problems(name: str) -> List[Dict]:
    """Load problems from HumanEval or MBPP dataset.

    Returns list of dicts with keys: id, prompt, test, entry_point
    """
    if name == "humaneval":
        ds = load_dataset("openai_humaneval", split="test")
        problems = []
        for item in ds:
            problems.append({
                "id": item["task_id"],
                "prompt": item["prompt"],
                "test": item["test"],
                "entry_point": item["entry_point"],
                "canonical_solution": item.get("canonical_solution", ""),
            })
        return problems

    elif name == "mbpp":
        ds = load_dataset("mbpp", split="test")
        problems = []
        for item in ds:
            test_code = "\n".join(item["test_list"])
            problems.append({
                "id": str(item["task_id"]),
                "prompt": item["text"],
                "test": test_code,
                "entry_point": extract_function_name(item["code"]),
                "canonical_solution": item.get("code", ""),
            })
        return problems

    else:
        raise ValueError(f"Unknown dataset: {name}")


def extract_function_name(code: str) -> str:
    """Extract function name from Python code."""
    for line in code.split("\n"):
        if line.strip().startswith("def "):
            name = line.split("def ")[1].split("(")[0].strip()
            return name
    return "solution"
