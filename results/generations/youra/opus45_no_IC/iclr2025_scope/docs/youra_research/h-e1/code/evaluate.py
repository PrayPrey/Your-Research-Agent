"""LongBench evaluation metrics."""

import re
import string
from collections import Counter
from config import TASK_METRIC


def normalize_answer(s: str) -> str:
    """Normalize answer for comparison."""
    s = s.lower()
    s = "".join(ch for ch in s if ch not in string.punctuation)
    s = " ".join(s.split())
    return s


def qa_f1_score(prediction: str, reference) -> float:
    """F1 score for QA tasks."""
    if isinstance(reference, list):
        return max(qa_f1_score(prediction, r) for r in reference)

    pred_tokens = normalize_answer(prediction).split()
    ref_tokens = normalize_answer(str(reference)).split()

    if not pred_tokens or not ref_tokens:
        return float(pred_tokens == ref_tokens)

    common = Counter(pred_tokens) & Counter(ref_tokens)
    num_same = sum(common.values())

    if num_same == 0:
        return 0.0

    precision = num_same / len(pred_tokens)
    recall = num_same / len(ref_tokens)
    return 2 * precision * recall / (precision + recall)


def rouge_score(prediction: str, reference) -> float:
    """ROUGE-L score for summarization."""
    if isinstance(reference, list):
        return max(rouge_score(prediction, r) for r in reference)

    pred_tokens = normalize_answer(prediction).split()
    ref_tokens = normalize_answer(str(reference)).split()

    if not pred_tokens or not ref_tokens:
        return float(pred_tokens == ref_tokens)

    m, n = len(ref_tokens), len(pred_tokens)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_tokens[i-1] == pred_tokens[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    lcs = dp[m][n]
    if lcs == 0:
        return 0.0

    precision = lcs / n
    recall = lcs / m
    return 2 * precision * recall / (precision + recall)


def classification_score(prediction: str, reference) -> float:
    """Exact match for classification."""
    if isinstance(reference, list):
        return max(classification_score(prediction, r) for r in reference)

    pred_norm = normalize_answer(prediction)
    ref_norm = normalize_answer(str(reference))
    return float(pred_norm == ref_norm or ref_norm in pred_norm or pred_norm in ref_norm)


def retrieval_score(prediction: str, reference) -> float:
    """Retrieval accuracy."""
    if isinstance(reference, list):
        return max(retrieval_score(prediction, r) for r in reference)

    pred_norm = normalize_answer(prediction)
    ref_norm = normalize_answer(str(reference))
    return float(ref_norm in pred_norm or pred_norm == ref_norm)


def code_sim_score(prediction: str, reference) -> float:
    """Code similarity (edit similarity)."""
    if isinstance(reference, list):
        return max(code_sim_score(prediction, r) for r in reference)

    pred = prediction.strip()
    ref = str(reference).strip()

    if not pred or not ref:
        return float(pred == ref)

    m, n = len(ref), len(pred)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref[i-1] == pred[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])

    edit_dist = dp[m][n]
    return 1.0 - edit_dist / max(m, n)


METRIC_FNS = {
    "qa_f1_score": qa_f1_score,
    "rouge_score": rouge_score,
    "classification_score": classification_score,
    "retrieval_score": retrieval_score,
    "code_sim_score": code_sim_score,
}


def score_task(task_name: str, predictions: list[str], references: list) -> float:
    """Score predictions for a task."""
    metric_name = TASK_METRIC.get(task_name, "qa_f1_score")
    metric_fn = METRIC_FNS[metric_name]

    scores = []
    for pred, ref in zip(predictions, references):
        scores.append(metric_fn(pred, ref))

    return sum(scores) / len(scores) if scores else 0.0
