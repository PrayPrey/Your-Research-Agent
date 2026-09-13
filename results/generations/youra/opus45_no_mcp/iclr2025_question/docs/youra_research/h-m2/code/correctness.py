"""Correctness evaluation: exact match + majority voting"""
from collections import Counter


def evaluate_correctness(generated: str, aliases: list[str]) -> bool:
    """Check if generated text contains any answer alias."""
    g = generated.lower().strip()
    return any(a.lower().strip() in g for a in aliases)


def majority_answer(responses: list[str]) -> str:
    """Return most frequent normalized response."""
    normalized = [r.lower().strip() for r in responses]
    if not normalized:
        return ""
    return Counter(normalized).most_common(1)[0][0]
