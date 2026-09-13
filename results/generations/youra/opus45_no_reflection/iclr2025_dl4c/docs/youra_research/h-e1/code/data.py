"""HumanEval data loading for EVAF H-E1."""

from datasets import load_dataset
from config import CONFIG


def load_humaneval():
    """Load HumanEval dataset from HuggingFace."""
    dataset = load_dataset(CONFIG["dataset_name"], split=CONFIG["dataset_split"])
    return dataset


def extract_problem(item: dict) -> dict:
    """Extract problem components from HumanEval item."""
    return {
        "task_id": item["task_id"],
        "prompt": item["prompt"],
        "entry_point": item["entry_point"],
        "test": item["test"],
        "canonical_solution": item["canonical_solution"],
    }


def get_all_problems():
    """Load and extract all HumanEval problems."""
    dataset = load_humaneval()
    return [extract_problem(item) for item in dataset]
