"""Data loading for TriviaQA, NQ-Open, and TruthfulQA."""
import json
import os
import string
import re
from typing import List, Dict, Optional

from datasets import load_dataset
from rouge_score import rouge_scorer as rouge_scorer_module


def _normalize_answer(s: str) -> str:
    """Lower, strip punctuation/articles/whitespace."""
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        return ''.join(ch for ch in text if ch not in set(string.punctuation))

    return white_space_fix(remove_articles(remove_punc(s.lower())))


def _exact_match(prediction: str, references: List[str]) -> bool:
    """Return True if normalized prediction matches any normalized reference."""
    pred_norm = _normalize_answer(prediction)
    return any(pred_norm == _normalize_answer(ref) for ref in references)


def load_trivia_qa(farquhar_data_dir: Optional[str] = None) -> List[Dict]:
    """
    Load TriviaQA validation samples.
    Uses HuggingFace 'trivia_qa' rc.nocontext split.
    Labels are pre-assigned as 1 (correct) since correctness is evaluated at inference time.

    Returns list of dicts with keys: question, label (None=eval at runtime), reference_answers
    """
    ds = load_dataset("trivia_qa", "rc.nocontext", split="validation")
    records = []
    for item in ds:
        question = item["question"]
        aliases = item["answer"].get("aliases", [])
        normalized_value = item["answer"].get("normalized_value", "")
        ref_answers = list(set(aliases + ([normalized_value] if normalized_value else [])))
        if not ref_answers:
            continue
        records.append({
            "question": question,
            "label": None,  # determined at inference time vs generated answer
            "reference_answers": ref_answers,
            "dataset": "trivia_qa",
        })
    return records


def load_nq(farquhar_data_dir: Optional[str] = None) -> List[Dict]:
    """
    Load NQ-Open validation samples.
    Uses HuggingFace 'nq_open' dataset.

    Returns list of dicts with keys: question, label (None=eval at runtime), reference_answers
    """
    ds = load_dataset("nq_open", split="validation")
    records = []
    for item in ds:
        question = item["question"]
        ref_answers = list(item["answer"]) if item["answer"] else []
        if not ref_answers:
            continue
        records.append({
            "question": question,
            "label": None,
            "reference_answers": ref_answers,
            "dataset": "nq",
        })
    return records


def load_truthful_qa() -> List[Dict]:
    """
    Load TruthfulQA generation subset from HuggingFace hub.
    Labels are None at load time; resolved via ROUGE-L at inference time.

    Returns list of dicts with keys: question, label, reference_answers, best_answer
    """
    ds = load_dataset("truthful_qa", "generation", split="validation")
    records = []
    for item in ds:
        question = item["question"]
        best_answer = item["best_answer"]
        correct_answers = list(item["correct_answers"])
        reference_answers = list(set([best_answer] + correct_answers))
        records.append({
            "question": question,
            "label": None,  # determined at inference time
            "reference_answers": reference_answers,
            "best_answer": best_answer,
            "dataset": "truthful_qa",
        })
    return records


def score_answer(generated: str, record: Dict, rouge_threshold: float = 0.3) -> int:
    """
    Score generated answer against reference answers.
    For TruthfulQA: ROUGE-L >= threshold -> correct (1)
    For TriviaQA/NQ: exact match -> correct (1)
    """
    if record.get("dataset") == "truthful_qa":
        scorer = rouge_scorer_module.RougeScorer(["rougeL"], use_stemmer=True)
        max_score = max(
            scorer.score(ref, generated)["rougeL"].fmeasure
            for ref in record["reference_answers"]
        )
        return int(max_score >= rouge_threshold)
    else:
        return int(_exact_match(generated, record["reference_answers"]))


def get_dataset(name: str, farquhar_data_dir: Optional[str] = None) -> List[Dict]:
    """Dispatcher: name in {'trivia_qa', 'nq', 'truthful_qa'}."""
    if name == "trivia_qa":
        return load_trivia_qa(farquhar_data_dir)
    elif name == "nq":
        return load_nq(farquhar_data_dir)
    elif name == "truthful_qa":
        return load_truthful_qa()
    else:
        raise ValueError(f"Unknown dataset: {name}. Must be one of: trivia_qa, nq, truthful_qa")
