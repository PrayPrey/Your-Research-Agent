from datasets import load_dataset
import config

def load_truthfulqa() -> list[dict]:
    ds = load_dataset(config.DATASET_ID, config.DATASET_CONFIG, split=config.DATASET_SPLIT, cache_dir=config.CACHE_DIR)
    return [
        {
            "question_id": i,
            "question": row["question"],
            "best_answer": row["best_answer"],
            "incorrect_answers": row["incorrect_answers"],
        }
        for i, row in enumerate(ds)
    ]
