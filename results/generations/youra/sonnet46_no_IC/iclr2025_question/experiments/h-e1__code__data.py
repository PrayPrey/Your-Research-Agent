"""h-e1 data pipeline: load, prompt, label, stratified split (A-1)."""
import json
import re
import string
from pathlib import Path

from datasets import load_dataset
from sklearn.model_selection import train_test_split

from constants import SEED, TRIVIAQA_N, RESULTS_DIR


def load_triviaqa():
    return load_dataset("mandarjoshi/trivia_qa", "rc.nocontext",
                        split="validation").select(range(TRIVIAQA_N))


def load_truthfulqa():
    return load_dataset("truthfulqa/truthful_qa", "generation", split="validation")


def format_prompt(example: dict, dataset_name: str) -> str:
    # Uniform short-answer QA template across both datasets and all models
    # (h-e1 external prompt artifact absent — documented deviation, 03_architecture.md).
    return f"Q: {example['question']}\nA:"


def _normalize(text: str) -> str:
    """SQuAD/TriviaQA-style answer normalization: lower, strip punct/articles/space."""
    text = text.lower()
    text = "".join(ch for ch in text if ch not in string.punctuation)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def _first_line(generated: str) -> str:
    # Trim continuation past the answer line (models often append "Q: ..." next turn)
    return generated.strip().split("\n")[0]


def label_response(example: dict, generated: str, dataset_name: str) -> int:
    """1 = hallucination, 0 = correct."""
    answer = _normalize(_first_line(generated))
    if dataset_name == "triviaqa":
        aliases = set(example["answer"]["normalized_aliases"]) | {
            _normalize(a) for a in example["answer"]["aliases"]}
        return 0 if answer in aliases else 1
    if dataset_name == "truthfulqa":
        # substring match vs correct_answers/best_answer (documented deviation)
        refs = [example["best_answer"]] + list(example["correct_answers"])
        for ref in refs:
            ref_n = _normalize(ref)
            if ref_n and ref_n in answer:
                return 0
        return 1
    raise ValueError(f"unknown dataset: {dataset_name}")


def stratified_split(labels: list, seed: int = SEED):
    """(selection_idx, test_idx), 50/50 stratified on label.
    n=1000 -> 500/500; n=817 -> 408 selection / 409 test."""
    n = len(labels)
    idx = list(range(n))
    strat = labels if min(labels.count(0), labels.count(1)) >= 2 else None
    selection_idx, test_idx = train_test_split(
        idx, test_size=n - n // 2, stratify=strat, random_state=seed)
    return sorted(selection_idx), sorted(test_idx)


def write_test_split_locked(test_idx: list, dataset_name: str, model_key: str) -> None:
    """Written to results/, NEVER read by analysis.py (FR-1.4, locked for h-m1)."""
    path = Path(RESULTS_DIR) / f"test_split_locked_{model_key}_{dataset_name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"model": model_key, "dataset": dataset_name,
                                "test_idx": test_idx}, indent=2))
