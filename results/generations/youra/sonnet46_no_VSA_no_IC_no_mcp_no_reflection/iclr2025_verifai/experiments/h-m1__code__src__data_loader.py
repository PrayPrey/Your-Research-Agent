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

    # MBPP sanitized test split
    try:
        import re as _re
        from datasets import load_dataset
        mbpp = load_dataset("google-research-datasets/mbpp", "sanitized")["test"]
        for i, item in enumerate(mbpp, 1):
            pid = f"MB_{i:04d}"
            test_list = item.get("test_list", [])
            test_code = "\n".join(test_list)
            # Extract expected function name from first test assertion
            entry_point = ""
            if test_list:
                m = _re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', test_list[0])
                if m and m.group(1) not in ("assert", "isinstance", "len", "print"):
                    entry_point = m.group(1)
            nat_prompt = item.get("prompt", "") or item.get("text", "")
            # Include function signature hint so model uses correct name
            if entry_point:
                prompt = f"{nat_prompt}\n\nWrite a Python function named `{entry_point}` that solves the above."
            else:
                prompt = nat_prompt
            problems.append(Problem(
                problem_id=pid,
                prompt=prompt,
                test_code=test_code,
                entry_point=entry_point,
                source="mbpp",
            ))
        print(f"✓ Loaded {i} MBPP problems")
    except Exception as e:
        print(f"⚠ MBPP load failed: {e}")

    print(f"✓ Total: {len(problems)} problems")
    return problems
