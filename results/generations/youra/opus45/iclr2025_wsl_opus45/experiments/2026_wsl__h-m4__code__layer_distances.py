"""LayerDistances: Grassmann distance computation per layer type."""

import os
from typing import Optional

import numpy as np
from tqdm import tqdm

import config
from adapter_loader import AdapterRecord, load_all_b_matrices


def grassmann_distance(A: np.ndarray, B: np.ndarray) -> float:
    """
    Compute Grassmann geodesic distance between column spaces of A and B.

    Uses QR decomposition followed by SVD to compute principal angles.
    Distance = ||arccos(singular_values)||_2

    Args:
        A: Matrix of shape [dim, r]
        B: Matrix of shape [dim, r]

    Returns:
        Grassmann distance (float >= 0)
    """
    # QR decomposition to get orthonormal bases
    Q_A, _ = np.linalg.qr(A)
    Q_B, _ = np.linalg.qr(B)

    # Compute inner product matrix
    M = Q_A.T @ Q_B

    # SVD to get singular values (cosines of principal angles)
    _, S, _ = np.linalg.svd(M, full_matrices=False)

    # Clamp for numerical stability (avoid arccos domain errors)
    S = np.clip(S, -1.0, 1.0)

    # Principal angles
    angles = np.arccos(S)

    # Geodesic distance is Frobenius norm of angles
    return float(np.linalg.norm(angles))


def compute_layer_type_distance_matrix(
    all_b_matrices: np.ndarray,
    layer_idx_list: Optional[list[int]] = None,
) -> np.ndarray:
    """
    Compute pairwise Grassmann distance matrix averaged over transformer layers.

    Args:
        all_b_matrices: Array of shape [n_adapters, n_layers, dim, r]
        layer_idx_list: Optional list of layer indices to use (default: all)

    Returns:
        Symmetric distance matrix of shape [n_adapters, n_adapters]
    """
    n_adapters = all_b_matrices.shape[0]
    n_layers = all_b_matrices.shape[1]

    if layer_idx_list is None:
        layer_idx_list = list(range(n_layers))

    # Initialize distance matrix
    dist_matrix = np.zeros((n_adapters, n_adapters))

    # Compute pairwise distances
    for i in range(n_adapters):
        for j in range(i + 1, n_adapters):
            layer_dists = []
            for l in layer_idx_list:
                d = grassmann_distance(
                    all_b_matrices[i, l],
                    all_b_matrices[j, l]
                )
                layer_dists.append(d)

            # Average across layers
            avg_dist = np.mean(layer_dists)
            dist_matrix[i, j] = avg_dist
            dist_matrix[j, i] = avg_dist  # Symmetric

    return dist_matrix


def compute_all_layer_type_distances(
    records: list[AdapterRecord],
    layer_types: list[str],
    verbose: bool = True,
) -> dict[str, np.ndarray]:
    """
    Compute distance matrices for all layer types.

    Args:
        records: List of AdapterRecord (40 adapters)
        layer_types: List of layer type names (e.g., ALL_LAYER_TYPES)
        verbose: Whether to show progress bars

    Returns:
        Dict mapping layer_type -> (40, 40) distance matrix
    """
    distances = {}

    iterator = tqdm(layer_types, desc="Computing layer distances") if verbose else layer_types

    for layer_type in iterator:
        if verbose:
            print(f"\nLoading B matrices for {layer_type}...")

        # Load all B matrices for this layer type
        all_b_matrices = load_all_b_matrices(records, layer_type)

        if verbose:
            print(f"  Shape: {all_b_matrices.shape}")
            print(f"  Computing pairwise distances...")

        # Compute distance matrix
        dist_matrix = compute_layer_type_distance_matrix(all_b_matrices)

        # Validate
        _validate_distance_matrix(dist_matrix, expected_n=len(records))

        distances[layer_type] = dist_matrix

        if verbose:
            print(f"  Done: mean distance = {np.mean(dist_matrix[np.triu_indices(len(records), k=1)]):.4f}")

    return distances


def _validate_distance_matrix(
    distance_matrix: np.ndarray,
    expected_n: int = 40,
) -> None:
    """Validate distance matrix properties."""
    # Check shape
    if distance_matrix.shape != (expected_n, expected_n):
        raise ValueError(
            f"Expected shape ({expected_n}, {expected_n}), "
            f"got {distance_matrix.shape}"
        )

    # Check symmetry
    if not np.allclose(distance_matrix, distance_matrix.T):
        raise ValueError("Distance matrix is not symmetric")

    # Check diagonal is zero
    if not np.allclose(np.diag(distance_matrix), 0):
        raise ValueError("Distance matrix diagonal is not zero")

    # Check all finite
    if not np.all(np.isfinite(distance_matrix)):
        raise ValueError("Distance matrix contains non-finite values")


def save_layer_distances(
    distances: dict[str, np.ndarray],
    output_path: str,
) -> None:
    """
    Save layer-type distance matrices to .npz file.

    Args:
        distances: Dict mapping layer_type -> (40, 40) distance matrix
        output_path: Path to save .npz file
    """
    np.savez(output_path, **distances)
    print(f"Saved layer distances to {output_path}")


def load_layer_distances(path: str) -> dict[str, np.ndarray]:
    """
    Load layer-type distance matrices from .npz file.

    Args:
        path: Path to .npz file

    Returns:
        Dict mapping layer_type -> (40, 40) distance matrix
    """
    data = np.load(path)
    return {key: data[key] for key in data.files}
