"""Correctness labeling for H-M1."""

from typing import List
from data_loader import normalize_answer
from config import F1_THRESHOLD


def token_f1(pred: str, gold: str) -> float:
    """Token-overlap F1 after normalization."""
    pred_tokens = set(normalize_answer(pred).split())
    gold_tokens = set(normalize_answer(gold).split())

    if not pred_tokens or not gold_tokens:
        return 0.0

    common = pred_tokens & gold_tokens
    if not common:
        return 0.0

    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gold_tokens)

    f1 = 2 * precision * recall / (precision + recall)
    return f1


def is_correct(response: str, gold_aliases: List[str], f1_threshold: float = F1_THRESHOLD) -> bool:
    """Check if response is correct via exact match OR F1 > threshold."""
    response_norm = normalize_answer(response)

    for alias in gold_aliases:
        alias_norm = normalize_answer(alias)
        # Exact match
        if response_norm == alias_norm:
            return True
        # Substring match (answer contained in response)
        if alias_norm in response_norm:
            return True
        # F1 threshold
        if token_f1(response, alias) > f1_threshold:
            return True

    return False


def label_responses(responses: List[str], gold_aliases: List[str]) -> List[bool]:
    """Label each response as correct/incorrect."""
    return [is_correct(r, gold_aliases) for r in responses]


def has_any_correct(responses: List[str], gold_aliases: List[str]) -> bool:
    """Check if any response in the set is correct."""
    return any(is_correct(r, gold_aliases) for r in responses)
