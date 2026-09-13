from datasets import load_dataset

def load_humaneval_problems(dataset_id: str = "openai/openai_humaneval", max_problems: int = 5) -> list[dict]:
    # ponytail: PoC uses 5 problems, increase max_problems for full eval
    dataset = load_dataset(dataset_id, split="test")
    problems = []
    for i, item in enumerate(dataset):
        if i >= max_problems:
            break
        problems.append({
            "task_id": item["task_id"],
            "prompt": item["prompt"],
            "canonical_solution": item.get("canonical_solution", ""),
            "test": item.get("test", ""),
            "entry_point": item.get("entry_point", "")
        })
    return problems
