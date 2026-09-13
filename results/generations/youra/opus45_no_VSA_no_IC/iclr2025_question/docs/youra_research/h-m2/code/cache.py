"""Hidden state disk cache for cross-model transfer experiments."""

import os
import numpy as np


class HiddenStateCache:
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def path(self, model_key: str, split: str) -> str:
        return os.path.join(self.cache_dir, f"{model_key}_{split}.npy")

    def save(self, model_key: str, split: str, hidden: np.ndarray) -> None:
        np.save(self.path(model_key, split), hidden)

    def load(self, model_key: str, split: str) -> np.ndarray | None:
        p = self.path(model_key, split)
        if os.path.exists(p):
            return np.load(p)
        return None

    def exists(self, model_key: str, split: str) -> bool:
        return os.path.exists(self.path(model_key, split))
