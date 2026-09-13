"""Similarity feature extraction via sentence embeddings."""

from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import ExperimentConfig


class SimilarityFeatureExtractor:
    """Extracts similarity statistics from response embeddings."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.model = None

    def _load_model(self):
        """Lazy load the sentence transformer."""
        if self.model is None:
            print(f"Loading embedder {self.config.embedder_name}...")
            self.model = SentenceTransformer(self.config.embedder_name)
            print("Embedder loaded.")

    def embed_responses(self, responses: list[str]) -> np.ndarray:
        """Embed responses via sentence-transformers.

        Returns:
            embeddings: (n_responses, embed_dim=384)
        """
        self._load_model()
        embeddings = self.model.encode(responses, convert_to_numpy=True)
        return embeddings

    def compute_similarity_stats(self, embeddings: np.ndarray) -> np.ndarray:
        """Compute pairwise cosine similarity statistics.

        Args:
            embeddings: (n_responses, embed_dim)
        Returns:
            stats: (4,) [mean, std, min, max] of upper-triangle similarities
        """
        # Compute pairwise cosine similarity
        sim_matrix = cosine_similarity(embeddings)

        # Extract upper triangle (excluding diagonal)
        n = sim_matrix.shape[0]
        upper_tri_indices = np.triu_indices(n, k=1)
        upper_tri_values = sim_matrix[upper_tri_indices]

        if len(upper_tri_values) == 0:
            return np.array([1.0, 0.0, 1.0, 1.0])

        stats = np.array([
            upper_tri_values.mean(),
            upper_tri_values.std(),
            upper_tri_values.min(),
            upper_tri_values.max(),
        ])
        return stats

    def extract_features(self, all_responses: list[list[str]]) -> np.ndarray:
        """Extract similarity stats for all questions.

        Returns:
            sim_features: (N, 4)
        """
        print("Extracting similarity features...")
        features = []

        for idx, responses in enumerate(all_responses):
            if (idx + 1) % 50 == 0:
                print(f"Processing question {idx + 1}/{len(all_responses)}")

            embeddings = self.embed_responses(responses)
            stats = self.compute_similarity_stats(embeddings)
            features.append(stats)

        sim_features = np.stack(features, axis=0)
        print(f"Extracted features shape: {sim_features.shape}")
        return sim_features

    def load_or_extract(
        self, all_responses: list[list[str]], split: str
    ) -> np.ndarray:
        """Cache-aware wrapper: load from cache or extract."""
        cache_dir = Path(self.config.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        features_path = cache_dir / f"sim_features_{split}.npy"

        if features_path.exists():
            print(f"Loading cached similarity features for {split}...")
            return np.load(features_path)

        print(f"Extracting similarity features for {split}...")
        sim_features = self.extract_features(all_responses)

        np.save(features_path, sim_features)
        print(f"Saved similarity features cache for {split}")

        return sim_features
