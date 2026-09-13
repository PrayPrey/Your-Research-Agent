"""N-gram extraction utilities."""

import hashlib
from config import NGRAM_SIZE


def tokenize(text: str) -> list[str]:
    """Lowercase, whitespace split."""
    return text.lower().split()


def extract_ngrams(tokens: list[str], n: int = NGRAM_SIZE) -> set[str]:
    """Sliding window n-grams."""
    if len(tokens) < n:
        return set()
    return {" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}


def ngram_hash(ngram: str) -> int:
    """64-bit blake2b hash."""
    return int.from_bytes(hashlib.blake2b(ngram.encode(), digest_size=8).digest(), "big")


def extract_ngram_hashes(text: str, n: int = NGRAM_SIZE) -> set[int]:
    """Tokenize, extract n-grams, hash each."""
    tokens = tokenize(text)
    ngrams = extract_ngrams(tokens, n)
    return {ngram_hash(g) for g in ngrams}
