from __future__ import annotations
import numpy as np
from config import ExperimentConfig


class NgramDetector:
    """Detector Family 1: EleutherAI 13-gram exact match."""

    def __init__(self, cfg: ExperimentConfig):
        self.n = cfg.ngram_n  # 13

    def predict(
        self,
        texts: list[str],
        ngram_index,
        threshold: int = 1,
    ) -> np.ndarray:
        """Binary contamination predictions. Returns shape (N,) int64."""
        return np.array(
            [int(ngram_index.max_overlap(t, self.n) >= threshold) for t in texts],
            dtype=np.int64,
        )

    def score(
        self,
        texts: list[str],
        ngram_index,
    ) -> np.ndarray:
        """Raw n-gram overlap counts. Returns shape (N,) int64."""
        return np.array(
            [ngram_index.max_overlap(t, self.n) for t in texts],
            dtype=np.int64,
        )
