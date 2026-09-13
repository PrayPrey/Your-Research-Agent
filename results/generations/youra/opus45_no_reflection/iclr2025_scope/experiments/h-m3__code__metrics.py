"""H-M3 Metrics - QA F1 Score and F1 Retention Computation"""
import re
import string
from collections import Counter
from typing import Dict, List
from tqdm import tqdm

from generate import generate_response

def normalize_text(text: str) -> str:
    """Normalize text for F1 comparison (LongBench style)."""
    text = text.lower()
    text = re.sub(r"[" + string.punctuation + "]", " ", text)
    text = " ".join(text.split())
    return text

def qa_f1_score(prediction: str, ground_truth: str) -> float:
    """Token-overlap F1 score (LongBench eval.py style)."""
    pred_tokens = normalize_text(prediction).split()
    gt_tokens = normalize_text(ground_truth).split()

    if not pred_tokens or not gt_tokens:
        return 0.0

    common = Counter(pred_tokens) & Counter(gt_tokens)
    num_same = sum(common.values())

    if num_same == 0:
        return 0.0

    precision = num_same / len(pred_tokens)
    recall = num_same / len(gt_tokens)
    f1 = 2 * precision * recall / (precision + recall)
    return f1

def evaluate_condition(
    model,
    tokenizer,
    samples_by_length: Dict[int, List[dict]],
    length: int,
    max_samples: int = None,
) -> Dict[str, List[float]]:
    """Evaluate model on samples at given length bucket."""
    scores = {}
    samples = samples_by_length.get(length, [])
    if max_samples:
        samples = samples[:max_samples]

    for sample in tqdm(samples, desc=f"Eval@{length}", leave=False):
        task = sample["task"]
        if task not in scores:
            scores[task] = []

        pred = generate_response(model, tokenizer, sample["prompt"])
        answers = sample.get("answers", [])
        if not answers:
            answers = [sample.get("answer", "")]

        f1 = max(qa_f1_score(pred, gt) for gt in answers) if answers else 0.0
        scores[task].append(f1)

    return scores

def f1_retention(student_f1: float, teacher_f1: float) -> float:
    """Compute F1 retention percentage."""
    if teacher_f1 == 0:
        return 100.0 if student_f1 == 0 else 0.0
    return (student_f1 / teacher_f1) * 100

def aggregate_scores(scores_by_task: Dict[str, List[float]]) -> float:
    """Aggregate F1 scores across tasks."""
    all_scores = []
    for task_scores in scores_by_task.values():
        all_scores.extend(task_scores)
    return sum(all_scores) / len(all_scores) if all_scores else 0.0
