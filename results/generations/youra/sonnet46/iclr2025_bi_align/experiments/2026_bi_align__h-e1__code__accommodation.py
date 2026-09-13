"""
accommodation.py - C_sem computation and OLS residualization.
"""
import numpy as np
import statsmodels.api as sm
from typing import List, Dict


def compute_cosine_similarities(
    h_next: np.ndarray,
    a_actual: np.ndarray,
    a_topic: np.ndarray,
    a_random: np.ndarray,
) -> Dict[str, np.ndarray]:
    """Compute elementwise cosine similarities (dot product for L2-normalized vectors).

    Args:
        h_next: shape (N, D) - next human turn embeddings (L2-normalized)
        a_actual: shape (N, D) - actual AI response embeddings (L2-normalized)
        a_topic: shape (N, D) - topic-matched control embeddings
        a_random: shape (N, D) - random control embeddings

    Returns:
        dict with keys 'cos_actual', 'cos_topic', 'cos_random', each shape (N,)
    """
    cos_actual = np.sum(h_next * a_actual, axis=1)
    cos_topic = np.sum(h_next * a_topic, axis=1)
    cos_random = np.sum(h_next * a_random, axis=1)
    return {
        "cos_actual": cos_actual,
        "cos_topic": cos_topic,
        "cos_random": cos_random,
    }


def residualize(cos_array: np.ndarray, covariate: np.ndarray) -> np.ndarray:
    """Compute OLS residuals of cos_array regressed on covariate.

    Args:
        cos_array: shape (N,) - dependent variable
        covariate: shape (N,) - covariate to regress out

    Returns:
        Residuals of shape (N,).
    """
    X = sm.add_constant(covariate)
    model = sm.OLS(cos_array, X)
    result = model.fit()
    return result.resid


def compute_c_sem(cos_actual: np.ndarray, cos_random: np.ndarray) -> float:
    """Compute C_sem = mean(cos_actual) - mean(cos_random).

    Args:
        cos_actual: shape (N,) - actual cosine similarities
        cos_random: shape (N,) - random control cosine similarities

    Returns:
        C_sem scalar float.
    """
    return float(np.mean(cos_actual) - np.mean(cos_random))


def apply_residualization(
    cos_dict: Dict[str, np.ndarray],
    token_counts: List[int],
    jaccard_overlaps: List[float],
) -> Dict[str, np.ndarray]:
    """Apply OLS residualization: first token length, then lexical overlap.

    Args:
        cos_dict: dict with 'cos_actual', 'cos_topic', 'cos_random'
        token_counts: list of token counts for each pair
        jaccard_overlaps: list of jaccard overlaps for each pair

    Returns:
        New dict with residualized cosine arrays.
    """
    tc = np.array(token_counts, dtype=np.float64)
    jac = np.array(jaccard_overlaps, dtype=np.float64)

    result = {}
    for key, cos_arr in cos_dict.items():
        # Step 1: residualize on token counts
        res1 = residualize(cos_arr.astype(np.float64), tc)
        # Step 2: residualize on jaccard overlaps
        res2 = residualize(res1, jac)
        result[key] = res2.astype(np.float32)

    return result
