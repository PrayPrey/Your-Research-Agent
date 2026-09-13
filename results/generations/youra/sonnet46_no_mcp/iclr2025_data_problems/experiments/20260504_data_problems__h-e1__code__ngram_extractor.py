from __future__ import annotations
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import Config

logger = logging.getLogger(__name__)


class NgramExtractor:
    def __init__(self, config: "Config"):
        self.config = config

    def extract(self, text: str) -> list[str]:
        """Sliding-window 13-gram extraction over whitespace-tokenized text.
        Returns [] if len(tokens) < min_token_length."""
        tokens = text.split()
        n = self.config.ngram_n
        if len(tokens) < self.config.min_token_length:
            return []
        return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]

    def extract_batch(self, texts: list[str]) -> list[list[str]]:
        """Batch extraction; logs count of skipped items (< min_token_length tokens)."""
        results = []
        skipped = 0
        for text in texts:
            ngrams = self.extract(text)
            if not ngrams:
                skipped += 1
            results.append(ngrams)
        if skipped:
            logger.info(f"NgramExtractor: skipped {skipped}/{len(texts)} items (< {self.config.min_token_length} tokens)")
        return results
