"""Uncertainty estimation methods: 4 methods for h-m1 correlation analysis."""

from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch
import re
from typing import List, Optional
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


class SelfConsistencyEstimator:
    """Self-consistency via majority voting (Wang et al. 2022) - renamed from EnsembleBaseline."""

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


class TokenVarianceEstimator:
    """Token-level variance computation."""

    def __init__(self, temperature: float = 0.7):
        """Initialize with temperature parameter."""
        self.temperature = temperature

    def compute_uncertainty(self, answers: List[str], logits_list: Optional[List[torch.Tensor]] = None) -> float:
        """
        Compute token-level variance across samples.

        Args:
            answers: List[str] - K generated answers (for fallback if no logits)
            logits_list: List[Tensor] - K logits tensors, each [seq_len, vocab_size]

        Returns:
            float - Mean variance across tokens
        """
        # If no logits provided, return simple answer diversity
        if logits_list is None or len(logits_list) == 0:
            unique_count = len(set(answers))
            return unique_count / len(answers) if len(answers) > 0 else 0.0

        # Stack logits (handle variable lengths by padding/truncating)
        min_len = min(logits.shape[0] for logits in logits_list)
        logits_aligned = torch.stack([logits[:min_len] for logits in logits_list])  # [K, seq_len, vocab_size]

        # Convert to probabilities with temperature scaling
        probs = torch.softmax(logits_aligned / self.temperature, dim=-1)  # [K, seq_len, vocab_size]

        # Compute variance across K samples
        variance = torch.var(probs, dim=0)  # [seq_len, vocab_size]

        # Return mean variance as uncertainty measure
        return float(variance.mean().item())


class VerbalizedConfidenceEstimator:
    """Verbalized confidence elicitation (VCE)."""

    def __init__(self, generator):
        """
        Initialize with generator instance.

        Args:
            generator: MistralGenerator instance for prompting
        """
        self.generator = generator

    def compute_uncertainty(self, question: str) -> float:
        """
        Extract verbalized confidence via prompting.

        Args:
            question: str - Input question

        Returns:
            float - Uncertainty (1 - confidence), range [0, 1]
        """
        # Prompt for confidence
        prompt = f"{question}\n\nProvide your answer and confidence (0-100%):"

        # Generate response (single sample)
        response = self.generator.generate_samples(prompt, k=1, temperature=0.1, max_new_tokens=100)[0]

        # Extract confidence
        confidence = self._extract_confidence(response)

        # Return uncertainty (1 - confidence)
        return 1.0 - confidence if confidence is not None else 0.5

    def _extract_confidence(self, response: str) -> Optional[float]:
        """Extract numeric confidence from response using regex."""
        # Try to find percentage pattern (e.g., "80%", "confidence: 75%")
        match = re.search(r'(\d+)\s*%', response)
        if match:
            percentage = float(match.group(1))
            # Normalize to [0, 1]
            return min(max(percentage / 100.0, 0.0), 1.0)

        # Fallback: neutral confidence
        return 0.5


# Backward compatibility alias
EnsembleBaseline = SelfConsistencyEstimator
