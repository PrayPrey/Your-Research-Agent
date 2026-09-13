"""HaluEval QA download and stratified sampling."""
import json
import os
import random
from pathlib import Path


def download_halueval(
    save_path: str = "data/halueval_qa_1000.json",
    raw_cache: str = "data/HaluEval_QA/qa_data.json",
    n_questions: int = 1000,
    seed: int = 42,
) -> list:
    """
    Load HaluEval QA, stratified sample 500 correct + 500 hallucinated.
    Skips download if save_path already exists.
    Returns list of {"question": str, "label": int} dicts.
    label: 0 = correct (right_answer), 1 = hallucinated (hallucinated_answer)
    """
    if os.path.exists(save_path):
        with open(save_path) as f:
            data = json.load(f)
        print(f"Loaded {len(data)} questions from {save_path}")
        return data

    # Load raw data
    if os.path.exists(raw_cache):
        with open(raw_cache) as f:
            raw = json.load(f)
    else:
        try:
            from datasets import load_dataset
            ds = load_dataset("pminervini/HaluEval", "qa", trust_remote_code=True)
            raw = list(ds["data"])
        except Exception as e:
            raise RuntimeError(f"Cannot load HaluEval: {e}")

    # Build flat list: each row yields two items (correct + hallucinated)
    correct_items = []
    hallucinated_items = []
    for row in raw:
        q = row["question"]
        correct_items.append({"question": q, "label": 0, "answer": row["right_answer"]})
        hallucinated_items.append({"question": q, "label": 1, "answer": row["hallucinated_answer"]})

    rng = random.Random(seed)
    rng.shuffle(correct_items)
    rng.shuffle(hallucinated_items)

    n_each = n_questions // 2
    sampled = correct_items[:n_each] + hallucinated_items[:n_each]
    rng.shuffle(sampled)

    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    with open(save_path, "w") as f:
        json.dump(sampled, f)

    print(f"Saved {len(sampled)} stratified questions to {save_path}")
    return sampled
