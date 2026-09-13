"""Data loading for HumanEval and MBPP datasets."""
from datasets import load_dataset

def load_humaneval() -> list[dict]:
    """Load HumanEval dataset with unified schema."""
    ds = load_dataset("openai_humaneval", split="test")
    problems = []
    for item in ds:
        problems.append({
            "id": item["task_id"],
            "prompt": item["prompt"],
            "code": item["canonical_solution"],
            "tests": item["test"],
            "entry_point": item["entry_point"],
        })
    return problems

def load_mbpp() -> list[dict]:
    """Load MBPP dataset with unified schema."""
    ds = load_dataset("mbpp", split="test")
    problems = []
    for item in ds:
        test_code = "\n".join(item["test_list"])
        problems.append({
            "id": f"mbpp_{item['task_id']}",
            "prompt": item["text"],
            "code": item["code"],
            "tests": test_code,
            "entry_point": None,
        })
    return problems

def load_all_problems() -> list[dict]:
    """Load both HumanEval and MBPP with unified schema."""
    return load_humaneval() + load_mbpp()

if __name__ == "__main__":
    problems = load_all_problems()
    print(f"Loaded {len(problems)} problems")
