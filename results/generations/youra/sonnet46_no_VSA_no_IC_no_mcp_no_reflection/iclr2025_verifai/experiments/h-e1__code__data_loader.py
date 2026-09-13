from dataclasses import dataclass
from typing import List


@dataclass
class Problem:
    problem_id: str
    prompt: str
    test_code: str
    entry_point: str
    source: str  # "humaneval" | "mbpp"


def load_problems() -> List[Problem]:
    problems: List[Problem] = []

    # HumanEval (164 problems)
    try:
        from human_eval.data import read_problems
        he_problems = read_problems()
        for i, (task_id, p) in enumerate(he_problems.items(), 1):
            pid = f"HE_{i:04d}"
            problems.append(Problem(
                problem_id=pid,
                prompt=p["prompt"],
                test_code=p["test"],
                entry_point=p.get("entry_point", ""),
                source="humaneval",
            ))
        print(f"✓ Loaded {i} HumanEval problems")
    except ImportError:
        print("⚠ human-eval not installed, skipping HumanEval")

    # MBPP sanitized test split (374 problems)
    try:
        from datasets import load_dataset
        mbpp = load_dataset("google-research-datasets/mbpp", "sanitized")["test"]
        for i, item in enumerate(mbpp, 1):
            pid = f"MB_{i:04d}"
            test_code = "\n".join(item.get("test_list", []))
            problems.append(Problem(
                problem_id=pid,
                prompt=item.get("text", ""),
                test_code=test_code,
                entry_point="",
                source="mbpp",
            ))
        print(f"✓ Loaded {i} MBPP problems")
    except Exception as e:
        print(f"⚠ MBPP load failed: {e}")

    print(f"✓ Total: {len(problems)} problems")
    return problems
