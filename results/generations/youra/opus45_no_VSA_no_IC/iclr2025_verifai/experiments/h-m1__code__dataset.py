from dataclasses import dataclass
from datasets import load_dataset

@dataclass
class Problem:
    task_id: str
    source: str
    prompt: str
    canonical_solution: str
    test: str

def load_humaneval() -> list[Problem]:
    ds = load_dataset("openai/openai_humaneval", split="test")
    return [
        Problem(
            task_id=row["task_id"],
            source="humaneval",
            prompt=row["prompt"],
            canonical_solution=row["canonical_solution"],
            test=row["test"],
        )
        for row in ds
    ]

def load_mbpp_sanitized() -> list[Problem]:
    ds = load_dataset("google-research-datasets/mbpp", "sanitized", split="test")
    return [
        Problem(
            task_id=f"mbpp_{row['task_id']}",
            source="mbpp",
            prompt=row["prompt"],
            canonical_solution=row["code"],
            test="\n".join(row["test_list"]),
        )
        for row in ds
    ]

def load_all_problems() -> list[Problem]:
    humaneval = load_humaneval()
    mbpp = load_mbpp_sanitized()
    return humaneval + mbpp
