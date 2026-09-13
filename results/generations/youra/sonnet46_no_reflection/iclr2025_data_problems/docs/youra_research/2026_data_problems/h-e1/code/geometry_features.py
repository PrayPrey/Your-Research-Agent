from __future__ import annotations
import numpy as np
from config import ExperimentConfig


class GeometryStratifier:
    """Compute corpus-side geometry features and assign contamination strata."""

    def __init__(self, cfg: ExperimentConfig):
        self.percentile: float = cfg.stratum_percentile  # 75.0

    def compute_geometry_features(
        self,
        benchmark_texts: list[str],
        ngram_index,
        sbert_index,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Returns (ngram_counts shape (N,) int64, cosines shape (N,) float32)."""
        ngram_counts = np.array(
            [ngram_index.max_overlap(t) for t in benchmark_texts], dtype=np.int64
        )
        distances, _ = sbert_index.search(benchmark_texts, k=1)
        cosines = distances[:, 0].astype(np.float32)
        return ngram_counts, cosines

    def compute_thresholds(
        self,
        ngram_counts: np.ndarray,
        cosines: np.ndarray,
    ) -> tuple[float, float]:
        """Return (lexical_thresh, semantic_thresh) as 75th percentile values."""
        lexical_thresh = float(np.percentile(ngram_counts, self.percentile))
        semantic_thresh = float(np.percentile(cosines, self.percentile))
        return lexical_thresh, semantic_thresh

    def assign_strata(
        self,
        ngram_counts: np.ndarray,
        cosines: np.ndarray,
        lexical_thresh: float,
        semantic_thresh: float,
    ) -> np.ndarray:
        """Assign strata: lexical overrides semantic. Returns shape (N,) object array."""
        strata = np.full(len(ngram_counts), "indeterminate", dtype=object)
        strata[cosines >= semantic_thresh] = "semantic"
        strata[ngram_counts >= lexical_thresh] = "lexical"
        valid = {"lexical", "semantic", "indeterminate"}
        assert set(np.unique(strata)).issubset(valid), f"Invalid strata labels: {np.unique(strata)}"
        return strata
