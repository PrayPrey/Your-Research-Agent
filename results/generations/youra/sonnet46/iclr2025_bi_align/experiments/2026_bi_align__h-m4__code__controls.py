"""
controls.py - Random shuffle and KNN topic-matched control embeddings.
"""
import numpy as np
from sklearn.neighbors import NearestNeighbors


def build_random_control(ai_embeddings: np.ndarray, seed: int = 42) -> np.ndarray:
    """Shuffle ai_embeddings along first axis.

    Args:
        ai_embeddings: shape (N, D)
        seed: random seed for reproducibility

    Returns:
        Shuffled array of same shape (N, D).
    """
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(ai_embeddings))
    return ai_embeddings[idx]


def build_topic_control(
    prompt_embeddings: np.ndarray,
    ai_embeddings: np.ndarray,
    k: int = 5,
) -> np.ndarray:
    """KNN topic-matched control with self-exclusion.

    For each sample i, find k+1 nearest neighbors in prompt_embeddings,
    exclude self (index 0 of results), use indices 1:k+1.
    Aggregate matched AI embeddings by mean.

    Args:
        prompt_embeddings: shape (N, D) - used for KNN lookup
        ai_embeddings: shape (N, D) - source of matched responses
        k: number of neighbors (default 5)

    Returns:
        np.ndarray of shape (N, D) - mean of matched AI embeddings.
    """
    nn = NearestNeighbors(n_neighbors=k + 1, metric="cosine", n_jobs=1)
    nn.fit(prompt_embeddings)
    _, indices = nn.kneighbors(prompt_embeddings)

    # indices shape: (N, k+1); column 0 is self
    neighbor_indices = indices[:, 1 : k + 1]  # exclude self

    # Mean of matched AI embeddings
    matched = ai_embeddings[neighbor_indices]  # (N, k, D)
    topic_control = matched.mean(axis=1)       # (N, D)
    return topic_control
