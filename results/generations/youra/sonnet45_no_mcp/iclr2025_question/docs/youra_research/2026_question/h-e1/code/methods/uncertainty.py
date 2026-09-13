"""Uncertainty estimation methods: Semantic Entropy and Ensemble Baseline."""

from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List
from collections import Counter


class SemanticEntropyEstimator:
    """Semantic entropy with clustering (Kuhn et al. 2023)."""

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.5
    ):
        """
        Initialize semantic entropy estimator.

        Args:
            embedding_model: Sentence transformer model name
            similarity_threshold: Cosine similarity threshold for clustering
        """
        self.embedding_model = embedding_model
        self.threshold = similarity_threshold
        self.embedder = None

    def load(self) -> None:
        """Load embedding model."""
        print(f"Loading embedding model: {self.embedding_model}")
        self.embedder = SentenceTransformer(self.embedding_model)
        print("Embedding model loaded")

    def compute_uncertainty(self, answers: List[str]) -> float:
        """
        Compute semantic entropy over answer clusters.

        Args:
            answers: List of K generated answers

        Returns:
            Semantic entropy value (higher = more uncertain)
        """
        if self.embedder is None:
            self.load()

        if len(answers) == 0:
            return 0.0

        # 1. Embed all answers
        embeddings = self.embedder.encode(answers)  # Shape: [K, 384]

        # 2. Cluster semantically similar answers
        # Use agglomerative clustering with cosine distance
        if len(answers) == 1:
            clusters = np.array([0])
        else:
            # Convert threshold to distance (1 - similarity)
            distance_threshold = 1 - self.threshold
            clustering = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=distance_threshold,
                metric='cosine',
                linkage='average'
            )
            clusters = clustering.fit_predict(embeddings)

        # 3. Compute entropy over cluster distribution
        cluster_counts = Counter(clusters)
        total = len(answers)
        probabilities = [count / total for count in cluster_counts.values()]

        # Entropy: -sum(p * log(p))
        entropy = -sum(p * np.log(p) for p in probabilities if p > 0)

        return float(entropy)


class EnsembleBaseline:
    """Ensemble baseline using majority voting without clustering."""

    def compute_uncertainty(self, answers: List[str]) -> float:
        """
        Compute disagreement rate via majority voting.

        Args:
            answers: List of K generated answers

        Returns:
            Disagreement rate (1 - max_vote_fraction)
        """
        if len(answers) == 0:
            return 0.0

        # Count votes for each unique answer
        vote_counts = Counter(answers)

        # Get maximum vote count
        max_count = max(vote_counts.values())

        # Compute agreement as fraction with majority
        agreement = max_count / len(answers)

        # Return disagreement as uncertainty measure
        return 1.0 - agreement
