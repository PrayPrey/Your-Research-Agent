from datasets import load_dataset

import config

def load_humaneval() -> list[dict]:
    ds = load_dataset(config.DATASET_ID, split="test")
    return [
        {
            "task_id": row["task_id"],
            "prompt": row["prompt"],
            "canonical_solution": row["canonical_solution"],
            "test": row["test"],
            "entry_point": row["entry_point"],
        }
        for row in ds
    ]

def generate_solution(prompt: str, canonical_solution: str) -> str:
    # Use canonical solution (simulates LLM output) for pylint analysis
    return prompt + canonical_solution
