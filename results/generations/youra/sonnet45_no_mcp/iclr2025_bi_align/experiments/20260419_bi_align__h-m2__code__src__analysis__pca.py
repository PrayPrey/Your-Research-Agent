"""
PCA dimensionality reduction module.
Tasks: task-006, task-007 - PCA for visualization and variance analysis
"""

import numpy as np
from sklearn.decomposition import PCA
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_pca(
    embeddings: np.ndarray,
    n_components: int = 2
) -> Tuple[np.ndarray, PCA]:
    """
    Apply PCA for dimensionality reduction.

    Args:
        embeddings: Input embeddings of shape (N, D)
        n_components: Number of components to keep

    Returns:
        (reduced_embeddings, pca_model)
    """
    logger.info(f"Applying PCA: {embeddings.shape} -> ({embeddings.shape[0]}, {n_components})")

    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(embeddings)

    variance_explained = pca.explained_variance_ratio_[:n_components].sum()
    logger.info(f"Variance explained by {n_components} PCs: {variance_explained:.3f}")

    return reduced, pca


def compute_variance_explained(
    pca_model: PCA,
    n_components: int = 50
) -> np.ndarray:
    """
    Compute cumulative variance explained.

    Args:
        pca_model: Fitted PCA model
        n_components: Number of components to analyze

    Returns:
        Cumulative variance array of shape (n_components,)
    """
    variance_ratio = pca_model.explained_variance_ratio_[:n_components]
    cumulative_variance = np.cumsum(variance_ratio)

    logger.info(f"Cumulative variance for first {n_components} PCs: {cumulative_variance[-1]:.3f}")

    return cumulative_variance
