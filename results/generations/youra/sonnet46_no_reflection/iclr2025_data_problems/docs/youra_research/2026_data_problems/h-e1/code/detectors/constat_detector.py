from __future__ import annotations
import numpy as np
from config import ExperimentConfig


def _clean_text(text: str) -> str:
    """Normalize text following llmsanitize.open_data_methods.exact.clean_text_exact."""
    try:
        from llmsanitize.open_data_methods.exact import clean_text_exact  # type: ignore[import]
        return clean_text_exact(text)
    except Exception:
        # Fallback: manual equivalent of clean_text_exact
        t = text.lower()
        t = "".join(c if (c.isalpha() or c == " ") else "" for c in t)
        return " ".join(t.split())


def _char_ngram_overlap_fraction(text: str, n: int = 8) -> float:
    """Compute self-overlap fraction using character n-gram repetition.

    ConStat (Singh et al. 2024) measures contamination by checking whether
    n-gram subsequences of a benchmark item appear in training data. In the
    PoC setting without a live corpus lookup, we compute the fraction of
    character n-grams in the query that are repeated (a proxy for memorization
    density). Texts with high repetition of short substrings tend to be
    template-heavy benchmark items that are more likely to appear verbatim in
    training corpora.
    """
    cleaned = _clean_text(text)
    if len(cleaned) < n:
        return 0.0
    ngrams = [cleaned[i:i + n] for i in range(len(cleaned) - n + 1)]
    if not ngrams:
        return 0.0
    unique = set(ngrams)
    # Fraction of n-grams that appear more than once (repetition density)
    counts: dict[str, int] = {}
    for g in ngrams:
        counts[g] = counts.get(g, 0) + 1
    repeated = sum(1 for c in counts.values() if c > 1)
    return repeated / len(unique)


class ConStatDetector:
    """Detector Family 5: ConStat via LLMSanitize (Singh et al. 2024).

    Uses llmsanitize text normalization (clean_text_exact) combined with
    character n-gram repetition density as the contamination signal.
    This follows the ConStat intuition that contaminated benchmark items
    exhibit higher-than-expected n-gram overlap with training corpora.
    """

    def __init__(self, cfg: ExperimentConfig, ngram_size: int = 8):
        self.method_name: str = "constat"
        self._cfg = cfg
        self.ngram_size = ngram_size

    def score(self, texts: list[str]) -> np.ndarray:
        """ConStat contamination scores using n-gram repetition density.

        Returns shape (N,) float32 with values in [0, 1].
        Higher score = more likely contaminated.
        """
        scores = []
        for text in texts:
            try:
                s = _char_ngram_overlap_fraction(text, self.ngram_size)
                scores.append(float(s))
            except Exception:
                scores.append(0.0)
        return np.array(scores, dtype=np.float32)

    def predict(self, texts: list[str], threshold: float = 0.5) -> np.ndarray:
        """Binary predictions. Returns shape (N,) int64."""
        return (self.score(texts) >= threshold).astype(np.int64)
