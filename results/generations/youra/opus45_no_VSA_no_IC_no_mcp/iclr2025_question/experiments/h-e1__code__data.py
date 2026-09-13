"""Data loading for TruthfulQA."""

from datasets import load_dataset
from config import CONFIG


def load_truthfulqa() -> list[dict]:
    """Load TruthfulQA dataset.

    Returns list of {question_id, question, best_answer, incorrect_answers}
    """
    dataset = load_dataset(
        CONFIG["DATASET_ID"],
        CONFIG["DATASET_CONFIG"],
        split=CONFIG["DATASET_SPLIT"],
        cache_dir=CONFIG["CACHE_DIR"]
    )

    data = []
    for i, row in enumerate(dataset):
        data.append({
            "question_id": i,
            "question": row["question"],
            "best_answer": row["best_answer"],
            "incorrect_answers": row["incorrect_answers"],
        })
    return data
