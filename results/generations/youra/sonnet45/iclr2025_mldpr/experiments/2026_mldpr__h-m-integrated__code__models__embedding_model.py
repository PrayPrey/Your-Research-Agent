"""
Embedding Model for h-m-integrated
Sentence-transformer wrapper for semantic embeddings
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List


class EmbeddingModel:
    """Sentence-transformer wrapper for semantic embeddings."""

    def __init__(self, config):
        """
        Initialize embedding model.

        Args:
            config: ExperimentConfig instance
        """
        self.config = config
        self.embedding_config = config.embedding

        print(f"Loading embedding model: {self.embedding_config.model_name}")
        self.model = SentenceTransformer(self.embedding_config.model_name)
        print(f"Model loaded successfully. Embedding dim: {self.get_embedding_dim()}")

    def encode(self, texts: List[str], show_progress: bool = None) -> np.ndarray:
        """
        Encode texts into semantic embeddings.

        Args:
            texts: List of text strings (N samples)
            show_progress: Show progress bar (default from config)

        Returns:
            np.ndarray: [N, 384] float32 embeddings (L2-normalized)
        """
        if show_progress is None:
            show_progress = self.embedding_config.show_progress

        # Encode texts
        embeddings = self.model.encode(
            texts,
            batch_size=self.embedding_config.batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=self.embedding_config.normalize_embeddings,
            convert_to_numpy=True
        )

        # Validate output shape
        expected_dim = self.embedding_config.embedding_dim
        if embeddings.shape[1] != expected_dim:
            raise ValueError(
                f"Unexpected embedding dimension: {embeddings.shape[1]} "
                f"(expected {expected_dim})"
            )

        # Check for NaN values
        if np.isnan(embeddings).any():
            raise ValueError("NaN values detected in embeddings")

        print(f"Encoded {len(texts)} texts into {embeddings.shape} embeddings")
        return embeddings

    def get_embedding_dim(self) -> int:
        """
        Get embedding dimension.

        Returns:
            int: Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        return self.model.get_sentence_embedding_dimension()
