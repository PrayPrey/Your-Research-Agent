# data.py - TruthfulQA MC1 loading + 5-fold splits
from datasets import load_dataset
from sklearn.model_selection import StratifiedKFold
import numpy as np
from config import CONFIG


def load_truthfulqa_mc1():
    """Load TruthfulQA multiple_choice dataset, return list of dicts."""
    ds = load_dataset(CONFIG["dataset"], CONFIG["dataset_config"], split="validation")
    samples = []
    for row in ds:
        samples.append({
            "question": row["question"],
            "choices": row["mc1_targets"]["choices"],
            "labels": row["mc1_targets"]["labels"],
        })
    return samples


def build_prompts(samples):
    """Flatten to (prompt_text, is_correct) pairs, one per choice."""
    prompts = []
    labels = []
    for s in samples:
        q = s["question"]
        for choice, label in zip(s["choices"], s["labels"]):
            prompt = f"Question: {q}\nAnswer: {choice}"
            prompts.append(prompt)
            labels.append(label)
    return prompts, np.array(labels)


def stratified_folds(labels, n_folds=None, seed=None):
    """Return StratifiedKFold split indices generator."""
    n_folds = n_folds or CONFIG["n_folds"]
    seed = seed or CONFIG["seed"]
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    return skf.split(np.zeros(len(labels)), labels)
