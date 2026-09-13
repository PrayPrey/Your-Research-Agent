"""Data loading for H-M2: TruthfulQA generation split."""
from datasets import load_dataset


def load_truthfulqa_generation() -> list[dict]:
    """Load TruthfulQA generation/validation split.

    Returns:
        List of dicts with 'question' key, 817 items total.
    """
    ds = load_dataset("truthful_qa", "generation", split="validation")
    return [{"question": q} for q in ds["question"]]
