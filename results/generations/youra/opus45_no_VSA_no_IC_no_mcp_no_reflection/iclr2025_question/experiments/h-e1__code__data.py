# data.py - TruthfulQA mc1 loading
from datasets import load_dataset
from config import DATASET_NAME, DATASET_CONFIG, CACHE_DIR


def load_truthfulqa_mc1(cache_dir: str = CACHE_DIR) -> list[dict]:
    """Load TruthfulQA mc1 (817 questions)."""
    ds = load_dataset(DATASET_NAME, DATASET_CONFIG, cache_dir=cache_dir, split="validation")
    records = []
    for row in ds:
        choices = row["mc1_targets"]["choices"]
        labels = row["mc1_targets"]["labels"]
        correct_idx = labels.index(1)
        records.append({
            "question": row["question"],
            "choices": choices,
            "correct_idx": correct_idx,
            "category": row.get("category", "unknown"),
        })
    return records


if __name__ == "__main__":
    data = load_truthfulqa_mc1()
    print(f"Loaded {len(data)} questions")
    print(f"Sample: {data[0]}")
