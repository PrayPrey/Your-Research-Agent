# h-m1/code/encoder.py
# FrozenEncoder: wraps all-MiniLM-L6-v2 in frozen eval mode

import numpy as np
import logging

from config import ENCODER_MODEL, ENCODER_BATCH_SIZE, EMBED_DIM

logger = logging.getLogger(__name__)


class FrozenEncoder:
    """Wrapper for all-MiniLM-L6-v2 in frozen eval mode."""

    def __init__(self, model_name: str = ENCODER_MODEL) -> None:
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(model_name)
        self._model.eval()
        # Disable gradients for all parameters
        try:
            import torch
            for param in self._model.parameters():
                param.requires_grad = False
        except Exception:
            pass
        logger.info(f"FrozenEncoder loaded: {model_name}, dim={self.embed_dim}")

    def encode_batch(self, texts: list, normalize: bool = True) -> np.ndarray:
        """Encode texts in batches; returns (N, 384) float32 array.

        normalize=True applies L2 normalization per embedding.
        """
        if not texts:
            return np.zeros((0, EMBED_DIM), dtype=np.float32)
        embeddings = self._model.encode(
            texts,
            batch_size=ENCODER_BATCH_SIZE,
            normalize_embeddings=normalize,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    @property
    def embed_dim(self) -> int:
        return EMBED_DIM
