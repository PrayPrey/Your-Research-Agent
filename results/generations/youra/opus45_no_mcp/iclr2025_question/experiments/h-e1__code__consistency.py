"""Semantic consistency computation using sentence embeddings."""
import numpy as np
from sentence_transformers import SentenceTransformer
from itertools import combinations


class SemanticConsistency:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def compute(self, responses: list[str]) -> float:
        """Compute mean pairwise cosine similarity across responses.

        Returns float in [-1, 1], or nan if < 2 responses.
        """
        if len(responses) < 2:
            return float('nan')

        embeddings = self.model.encode(responses)

        similarities = []
        for i, j in combinations(range(len(responses)), 2):
            cos_sim = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )
            similarities.append(cos_sim)

        return float(np.mean(similarities))
