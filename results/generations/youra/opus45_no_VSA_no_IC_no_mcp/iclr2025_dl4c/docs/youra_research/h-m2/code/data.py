from datasets import load_dataset

def load_humaneval() -> list[dict]:
    ds = load_dataset("openai_humaneval", split="test")
    return [
        {
            "task_id": row["task_id"],
            "prompt": row["prompt"],
            "tests": row["test"],
            "entry_point": row["entry_point"],
            "source": "humaneval",
        }
        for row in ds
    ]

def load_mbpp() -> list[dict]:
    ds = load_dataset("mbpp", split="test")
    return [
        {
            "task_id": str(row["task_id"]),
            "prompt": row["text"],
            "tests": "\n".join(row["test_list"]),
            "entry_point": None,
            "source": "mbpp",
        }
        for row in ds
    ]

def load_all_problems() -> dict[str, list[dict]]:
    return {
        "humaneval": load_humaneval(),
        "mbpp": load_mbpp(),
    }
