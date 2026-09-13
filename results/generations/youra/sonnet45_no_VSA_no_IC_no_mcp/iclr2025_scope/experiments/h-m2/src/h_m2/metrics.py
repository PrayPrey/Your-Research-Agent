from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score
import numpy as np
from typing import Dict


class SimilarityCalculator:
    """Calculate clustering quality metrics."""

    def intra_family_similarity(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """Avg cosine similarity within clusters."""
        cluster_sims = []

        for cluster_id in np.unique(labels):
            cluster_mask = labels == cluster_id
            cluster_embs = embeddings[cluster_mask]

            if len(cluster_embs) < 2:
                continue  # Skip singletons

            # Pairwise cosine similarity
            sim_matrix = cosine_similarity(cluster_embs)

            # Upper triangle, exclude diagonal
            mask = np.triu(np.ones_like(sim_matrix, dtype=bool), k=1)
            cluster_sim = sim_matrix[mask].mean()

            cluster_sims.append(cluster_sim)

        return np.mean(cluster_sims) if cluster_sims else 0.0

    def silhouette(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """Silhouette score. Returns: float in [-1, 1]"""
        if len(np.unique(labels)) < 2:
            return 0.0
        return silhouette_score(embeddings, labels)

    def pairwise_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Full pairwise cosine similarity. [N, D] → [N, N]"""
        return cosine_similarity(embeddings)


class Evaluator:
    """Gate evaluation logic."""

    def __init__(self, similarity_threshold: float = 0.60,
                 silhouette_threshold: float = 0.3,
                 partial_threshold: float = 0.5):
        self.similarity_threshold = similarity_threshold
        self.silhouette_threshold = silhouette_threshold
        self.partial_threshold = partial_threshold
        self.calculator = SimilarityCalculator()

    def evaluate(self, embeddings: np.ndarray, labels: np.ndarray) -> Dict:
        """Calculate all metrics."""
        intra_sim = self.calculator.intra_family_similarity(embeddings, labels)
        silhouette = self.calculator.silhouette(embeddings, labels)

        gate_decision = self.check_gate(intra_sim, silhouette)

        return {
            'intra_family_similarity': intra_sim,
            'silhouette_score': silhouette,
            'gate_decision': gate_decision
        }

    def check_gate(self, intra_sim: float, silhouette: float) -> str:
        """Gate decision. Returns: "PASS" | "PARTIAL" | "FAIL"""
        if intra_sim >= self.similarity_threshold and silhouette > self.silhouette_threshold:
            return "PASS"
        elif intra_sim >= self.partial_threshold:
            return "PARTIAL"
        else:
            return "FAIL"
