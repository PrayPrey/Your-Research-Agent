"""Reformulation detection and slope computation."""

from typing import List
import numpy as np
from scipy.stats import linregress
from sentence_transformers import SentenceTransformer
import Levenshtein


class ReformulationAnalyzer:
    """Detect query reformulation patterns and compute slope."""

    def __init__(self, sbert_model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with SBERT model."""
        print(f"Loading SBERT model: {sbert_model_name}...")
        self.sbert = SentenceTransformer(sbert_model_name)

    def detect_reformulation(
        self,
        query_t: str,
        query_t1: str,
        semantic_threshold: float = 0.7,
        syntactic_threshold: float = 0.3
    ) -> bool:
        """
        Detect reformulation between consecutive queries.

        Reformulation = high semantic similarity + high syntactic change

        Args:
            query_t: Query at turn t
            query_t1: Query at turn t+1
            semantic_threshold: Min cosine similarity for semantic match
            syntactic_threshold: Min normalized edit distance for syntactic change

        Returns:
            True if reformulation detected
        """
        # Semantic similarity
        emb_t = self.sbert.encode(query_t, convert_to_tensor=False)
        emb_t1 = self.sbert.encode(query_t1, convert_to_tensor=False)
        semantic_sim = np.dot(emb_t, emb_t1) / (np.linalg.norm(emb_t) * np.linalg.norm(emb_t1))

        # Syntactic distance
        edit_dist = Levenshtein.distance(query_t, query_t1)
        max_len = max(len(query_t), len(query_t1))
        norm_edit = edit_dist / max_len if max_len > 0 else 0.0

        # Reformulation: high semantic + high syntactic change
        is_reformulation = semantic_sim > semantic_threshold and norm_edit > syntactic_threshold

        return is_reformulation

    def compute_reformulation_slope(
        self,
        queries: List[str],
        semantic_threshold: float = 0.7,
        syntactic_threshold: float = 0.3
    ) -> float:
        """
        Compute reformulation rate decline slope across turns.

        Args:
            queries: List of queries in conversation
            semantic_threshold: Semantic similarity threshold
            syntactic_threshold: Syntactic distance threshold

        Returns:
            Slope coefficient (negative = learning)
        """
        if len(queries) < 2:
            return 0.0

        # Detect reformulation for each consecutive pair
        reformulation_indicators = []
        for i in range(len(queries) - 1):
            is_reform = self.detect_reformulation(
                queries[i],
                queries[i + 1],
                semantic_threshold,
                syntactic_threshold
            )
            reformulation_indicators.append(float(is_reform))

        if len(reformulation_indicators) < 2:
            return 0.0

        # Linear regression: reformulation_rate ~ turn_index
        turns = np.arange(len(reformulation_indicators))
        slope, intercept, r_value, p_value, std_err = linregress(turns, reformulation_indicators)

        return slope
