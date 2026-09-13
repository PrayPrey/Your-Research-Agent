"""
Vendored F1 scorer from THUDM/LongBench.
Source: https://github.com/THUDM/LongBench/blob/main/eval.py
"""
import re
import string
from collections import Counter


def normalize_answer(s: str) -> str:
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def get_tokens(s: str) -> list:
    if not s:
        return []
    return normalize_answer(s).split()


def compute_f1(prediction: str, ground_truth: str) -> float:
    prediction_tokens = get_tokens(prediction)
    ground_truth_tokens = get_tokens(ground_truth)
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(prediction_tokens)
    recall = num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def scorer(prediction: str, ground_truths, dataset: str = None) -> float:
    """
    Compute max F1 over all ground truth answers.
    ground_truths: str or list of str
    """
    if isinstance(ground_truths, str):
        ground_truths = [ground_truths]
    if not ground_truths:
        return 0.0
    return max(compute_f1(prediction, gt) for gt in ground_truths)
