"""Lexical diversity metrics."""

from typing import List


def compute_distinct_n(texts: List[str], n: int = 1) -> float:
    """
    Compute distinct-n metric (lexical diversity).

    Distinct-n = unique n-grams / total n-grams

    Args:
        texts: List of text strings
        n: N-gram size (default: 1 for distinct-1)

    Returns:
        Diversity score (0-1)
    """
    if not texts:
        return 0.0

    # Concatenate all texts
    combined_text = " ".join(texts)
    tokens = combined_text.split()

    if len(tokens) < n:
        return 0.0

    # Generate n-grams
    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngram = tuple(tokens[i:i + n])
        ngrams.append(ngram)

    if not ngrams:
        return 0.0

    unique_ngrams = set(ngrams)
    diversity = len(unique_ngrams) / len(ngrams)

    return diversity


def compute_diversity(texts: List[str]) -> float:
    """
    Compute diversity using distinct-1.

    Args:
        texts: List of text strings

    Returns:
        Diversity score
    """
    return compute_distinct_n(texts, n=1)
