"""Data loading for TruthfulQA mc1 dataset."""
from datasets import load_dataset
from typing import TypedDict


class TruthfulQAItem(TypedDict):
    question: str
    choices: list
    correct_idx: int


def load_truthfulqa_mc1() -> list:
    """Load TruthfulQA mc1 subset (817 items)."""
    dataset = load_dataset("truthful_qa", "multiple_choice", split="validation")
    items = []
    for row in dataset:
        mc1 = row["mc1_targets"]
        choices = mc1["choices"]
        labels = mc1["labels"]
        correct_idx = labels.index(1) if 1 in labels else 0
        items.append({
            "question": row["question"],
            "choices": choices,
            "correct_idx": correct_idx
        })
    return items


def format_choices(choices: list) -> str:
    """Format choices as lettered list."""
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "\n".join(f"{letters[i]}) {c}" for i, c in enumerate(choices))
