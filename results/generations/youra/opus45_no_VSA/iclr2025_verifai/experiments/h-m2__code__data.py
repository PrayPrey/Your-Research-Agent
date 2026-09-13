"""Data loading for HumanEval + MBPP datasets."""
from dataclasses import dataclass
from typing import List
import random


@dataclass
class Problem:
    problem_id: str
    source: str  # "humaneval" | "mbpp"
    prompt: str
    tests: str
    entry_point: str


def load_problems(seed: int = 42) -> List[Problem]:
    """Load HumanEval + MBPP problems, shuffle with fixed seed."""
    from datasets import load_dataset

    problems = []

    # HumanEval
    humaneval = load_dataset("openai/openai_humaneval", split="test")
    for item in humaneval:
        problems.append(Problem(
            problem_id=item["task_id"],
            source="humaneval",
            prompt=item["prompt"],
            tests=item["test"],
            entry_point=item["entry_point"],
        ))

    # MBPP
    mbpp = load_dataset("mbpp", split="test")
    for item in mbpp:
        test_str = "\n".join(item["test_list"])
        problems.append(Problem(
            problem_id=f"mbpp_{item['task_id']}",
            source="mbpp",
            prompt=item["text"] + "\n" + item["code"],
            tests=test_str,
            entry_point="",  # MBPP uses inline test assertions
        ))

    random.seed(seed)
    random.shuffle(problems)
    return problems
