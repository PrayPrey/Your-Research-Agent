# h-m1/code/projection.py
# AI-typicality geometric projection functions

import numpy as np
import logging
from sklearn.decomposition import PCA

logger = logging.getLogger(__name__)


def build_ai_typicality_vector(
    encoder,
    ai_texts: list,
    human_texts: list,
) -> np.ndarray:
    """Centroid difference: mean(ai_embs) - mean(human_embs), L2-normalized.

    Returns unit vector (384,).
    Raises ValueError if either text list is empty.
    """
    if not ai_texts:
        raise ValueError("ai_texts must be non-empty")
    if not human_texts:
        raise ValueError("human_texts must be non-empty")

    ai_embs = encoder.encode_batch(ai_texts).astype(np.float64)       # (N_ai, 384)
    human_embs = encoder.encode_batch(human_texts).astype(np.float64)  # (N_human, 384)

    vec = ai_embs.mean(axis=0) - human_embs.mean(axis=0)  # (384,)
    norm = np.linalg.norm(vec)
    if norm < 1e-10:
        logger.warning("AI-typicality vector near-zero norm; returning random unit vector")
        rng = np.random.default_rng(42)
        vec = rng.standard_normal(vec.shape)
        norm = np.linalg.norm(vec)
    return vec / norm


def compute_raw_projection(
    embeddings: np.ndarray,
    ai_typicality_vec: np.ndarray,
) -> np.ndarray:
    """Dot product of each embedding row with unit ai_typicality_vec.

    Input: (N, 384), (384,) -> Output: (N,) float64.
    """
    return embeddings.astype(np.float64) @ ai_typicality_vec.astype(np.float64)


def partial_out_q_early(
    raw_proj: np.ndarray,
    q_early_scores: np.ndarray,
) -> np.ndarray:
    """OLS residuals: regress raw_proj on q_early_scores; return residuals.

    Handles degenerate case: constant q_early_scores -> return raw_proj unchanged.
    """
    raw_proj = raw_proj.astype(np.float64)
    q = q_early_scores.astype(np.float64)

    if np.std(q) < 1e-10:
        logger.warning("q_early_scores is constant; skipping partialing")
        return raw_proj

    X = np.column_stack([np.ones(len(q)), q])
    beta, _, _, _ = np.linalg.lstsq(X, raw_proj, rcond=None)
    fitted = X @ beta
    return raw_proj - fitted


def zscore_projection(residuals: np.ndarray) -> np.ndarray:
    """Standardize residuals to z-scores (mean=0, std=1).

    Returns (N,) float64. Handles std==0 edge case (return zeros).
    """
    res = residuals.astype(np.float64)
    mu = res.mean()
    sigma = res.std()
    if sigma < 1e-10:
        logger.warning("projection residuals have near-zero std; returning zeros")
        return np.zeros_like(res)
    return (res - mu) / sigma


def build_topic_axis_vector(
    encoder,
    prompt_texts: list,
    n_components: int = 1,
) -> np.ndarray:
    """PCA first component of prompt embeddings as topic-axis direction.

    Used for discriminant validity control. Returns unit vector (384,).
    """
    if not prompt_texts:
        raise ValueError("prompt_texts must be non-empty")

    embs = encoder.encode_batch(prompt_texts).astype(np.float64)  # (N, 384)
    pca = PCA(n_components=n_components, random_state=42)
    pca.fit(embs)
    vec = pca.components_[0]  # (384,)
    norm = np.linalg.norm(vec)
    if norm < 1e-10:
        logger.warning("Topic axis vector near-zero norm")
        return vec
    return vec / norm


def placebo_permute_vector(
    encoder,
    ai_texts: list,
    human_texts: list,
    n_permutations: int = 1000,
    seed: int = 42,
) -> np.ndarray:
    """Permute AI/human labels; compute centroid difference for each permutation.

    Returns (n_permutations, 384) array of null vectors.
    """
    all_texts = list(ai_texts) + list(human_texts)
    all_embs = encoder.encode_batch(all_texts).astype(np.float64)  # (N_total, 384)
    n_ai = len(ai_texts)

    rng = np.random.default_rng(seed)
    null_vecs = np.zeros((n_permutations, all_embs.shape[1]))

    for i in range(n_permutations):
        perm = rng.permutation(len(all_embs))
        ai_perm = all_embs[perm[:n_ai]]
        hu_perm = all_embs[perm[n_ai:]]
        diff = ai_perm.mean(0) - hu_perm.mean(0)
        norm = np.linalg.norm(diff)
        null_vecs[i] = diff / (norm + 1e-10)

    return null_vecs
