"""A-1: Data Loading - Load TruthfulQA MC2 split, format options with letters"""
import string
from datasets import load_dataset


def load_truthfulqa_mc2() -> list[dict]:
    """Load TruthfulQA mc2 validation split from HF datasets."""
    ds = load_dataset("truthful_qa", "multiple_choice", split="validation")
    items = []
    for row in ds:
        items.append({
            "question": row["question"],
            "mc2_targets": row["mc2_targets"]
        })
    return items


def format_options(mc2_targets: dict) -> tuple[str, list[str]]:
    """Format mc2_targets choices as 'A) text\\nB) text...'. Returns (formatted_str, ['A','B',...])."""
    choices = mc2_targets["choices"]
    letters = list(string.ascii_uppercase[:len(choices)])
    formatted = "\n".join(f"{letter}) {choice}" for letter, choice in zip(letters, choices))
    return formatted, letters


if __name__ == "__main__":
    items = load_truthfulqa_mc2()
    print(f"Loaded {len(items)} items")
    if items:
        opts, letters = format_options(items[0]["mc2_targets"])
        print(f"Sample options:\n{opts}")
        print(f"Letters: {letters}")
