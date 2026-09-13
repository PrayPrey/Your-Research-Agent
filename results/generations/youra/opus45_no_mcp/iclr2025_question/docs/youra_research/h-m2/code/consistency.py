"""Semantic consistency scorer using SentenceTransformer embeddings"""
import numpy as np
from sentence_transformers import SentenceTransformer
import config


class SemanticConsistencyScorer:
    def __init__(self, model_name: str = None):
        """Load SentenceTransformer once."""
        model_name = model_name or config.EMBEDDING_MODEL
        self.model = SentenceTransformer(model_name)

    def encode(self, responses: list[str]) -> np.ndarray:
        """Batch encode responses to embeddings [N, dim]."""
        return self.model.encode(responses, convert_to_numpy=True, normalize_embeddings=True)

    def compute_consistency(self, responses: list[str]) -> float:
        """Compute mean pairwise cosine similarity across N responses."""
        if len(responses) < 2:
            return 1.0  # Single response = perfect consistency

        embeddings = self.encode(responses)  # [N, dim], L2-normalized
        sim_matrix = embeddings @ embeddings.T  # [N, N] cosine similarities
        n = len(responses)
        iu = np.triu_indices(n, k=1)  # Upper triangle indices, exclude diagonal
        pairwise_sims = sim_matrix[iu]
        return float(np.mean(pairwise_sims))
