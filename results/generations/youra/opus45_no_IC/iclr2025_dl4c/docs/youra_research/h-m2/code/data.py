"""Data loading for HumanEval and MBPP datasets."""

from typing import List, Dict, Any
from human_eval.data import read_problems
from datasets import load_dataset


def load_humaneval() -> List[Dict[str, Any]]:
    """Load HumanEval dataset (164 problems)."""
    raw = read_problems()
    problems = []
    for task_id, data in raw.items():
        problems.append({
            "task_id": task_id,
            "prompt": data["prompt"],
            "test": data["test"],
            "entry_point": data["entry_point"],
            "canonical_solution": data.get("canonical_solution", ""),
        })
    return problems


def load_mbpp() -> List[Dict[str, Any]]:
    """Load MBPP test split (500 problems, indices 11-510)."""
    dataset = load_dataset("mbpp", split="test")
    problems = []
    for item in dataset:
        problems.append({
            "task_id": f"mbpp/{item['task_id']}",
            "text": item["text"],
            "code": item["code"],
            "test_list": item["test_list"],
            "test_setup_code": item.get("test_setup_code", ""),
        })
    return problems


def format_prompt(problem: Dict[str, Any], dataset: str = "humaneval") -> str:
    """Format problem as instruction prompt for CodeLlama-Instruct."""
    if dataset == "humaneval" or "HumanEval" in problem.get("task_id", ""):
        prompt = problem["prompt"]
        instruction = f"""Complete the following Python function based on the docstring.

{prompt}"""
    else:
        text = problem.get("text", "")
        instruction = f"""Write a Python function to solve the following problem.

{text}

def solution():"""

    return f"[INST] {instruction} [/INST]"


def get_test_cases(problem: Dict[str, Any], dataset: str = "humaneval") -> List[str]:
    """Extract test cases from problem."""
    if dataset == "humaneval" or "HumanEval" in problem.get("task_id", ""):
        return [problem["test"]]
    else:
        return problem.get("test_list", [])
