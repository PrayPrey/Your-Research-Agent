from __future__ import annotations
import numpy as np
from config import ExperimentConfig


class EmbeddingDetector:
    """Detector Family 2: SBERT cosine similarity threshold."""

    def __init__(self, cfg: ExperimentConfig):
        self.default_threshold: float = 0.95

    def predict(
        self,
        texts: list[str],
        sbert_index,
        threshold: float = 0.95,
    ) -> np.ndarray:
        """Binary labels from max cosine to corpus. Returns shape (N,) int64."""
        distances, _ = sbert_index.search(texts, k=1)
        max_cosines = distances[:, 0]
        return (max_cosines >= threshold).astype(np.int64)

    def score(
        self,
        texts: list[str],
        sbert_index,
    ) -> np.ndarray:
        """Max cosine similarity per item. Returns shape (N,) float32."""
        distances, _ = sbert_index.search(texts, k=1)
        return distances[:, 0].astype(np.float32)
