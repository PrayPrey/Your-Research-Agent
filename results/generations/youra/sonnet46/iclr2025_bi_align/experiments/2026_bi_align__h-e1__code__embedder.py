"""
embedder.py - SentenceTransformer wrapper with .npy cache support.
"""
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Optional


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "embeddings"):
        """Initialize SentenceTransformer and set cache directory."""
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.model = SentenceTransformer(model_name)
        os.makedirs(cache_dir, exist_ok=True)

    def encode(self, texts: List[str], cache_key: str) -> np.ndarray:
        """Encode texts with L2 normalization, using cache if available.

        Args:
            texts: List of strings to encode.
            cache_key: Key for caching (filename without extension).

        Returns:
            np.ndarray of shape (N, D) with L2-normalized embeddings.
        """
        cached = self.load_cache(cache_key)
        if cached is not None:
            return cached

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=256,
            show_progress_bar=True,
        )
        embeddings = np.array(embeddings, dtype=np.float32)
        self.save_cache(embeddings, cache_key)
        return embeddings

    def load_cache(self, cache_key: str) -> Optional[np.ndarray]:
        """Load embeddings from cache if exists."""
        path = os.path.join(self.cache_dir, f"{cache_key}.npy")
        if os.path.exists(path):
            return np.load(path)
        return None

    def save_cache(self, embeddings: np.ndarray, cache_key: str) -> None:
        """Save embeddings to cache."""
        path = os.path.join(self.cache_dir, f"{cache_key}.npy")
        np.save(path, embeddings)
