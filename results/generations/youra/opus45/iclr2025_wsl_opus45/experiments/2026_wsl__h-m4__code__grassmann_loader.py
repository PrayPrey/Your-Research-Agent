"""GrassmannLoader: Load or compute Grassmann distance matrix from H-E1."""

import json
import os
from pathlib import Path
from typing import Optional

import numpy as np

import config


def load_or_compute_distances(
    h_e1_hypothesis_dir: str,
    force_recompute: bool = False,
) -> tuple[np.ndarray, list[dict]]:
    """
    Load precomputed distances from H-E1 results, or recompute from adapters.

    Args:
        h_e1_hypothesis_dir: Path to H-E1 hypothesis directory
        force_recompute: If True, recompute even if cached file exists

    Returns:
        distance_matrix: (40, 40) symmetric float array
        adapter_meta: list of {adapter_path, task, seed, category}
    """
    results_dir = os.path.join(h_e1_hypothesis_dir, "results")
    npy_path = os.path.join(results_dir, "pairwise_distances.npy")
    meta_path = os.path.join(results_dir, "adapter_metadata.json")

    if not force_recompute and os.path.exists(npy_path) and os.path.exists(meta_path):
        # Load from cache
        dist = np.load(npy_path)
        meta = load_adapter_metadata(results_dir)
        validate_distance_matrix(dist)
        return dist, meta

    # Fallback: recompute via H-E1 bridge
    from h_e1_bridge import compute_pairwise_matrix

    adapter_dir = os.path.join(h_e1_hypothesis_dir, "adapters")
    if not os.path.exists(adapter_dir):
        raise FileNotFoundError(f"Adapter directory not found: {adapter_dir}")

    adapter_paths = sorted([
        os.path.join(adapter_dir, p)
        for p in os.listdir(adapter_dir)
        if "_seed" in p
    ])

    if len(adapter_paths) == 0:
        raise ValueError(f"No adapters found in {adapter_dir}")

    dist, meta = compute_pairwise_matrix(adapter_paths)
    validate_distance_matrix(dist)

    # Save for future use
    np.save(npy_path, dist)
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)

    return dist, meta


def validate_distance_matrix(
    distance_matrix: np.ndarray,
    expected_n: int = 40,
) -> None:
    """
    Assert shape (N,N), symmetric, zero diagonal, finite values.

    Args:
        distance_matrix: Matrix to validate
        expected_n: Expected dimension (default 40 for 8 tasks x 5 seeds)

    Raises:
        ValueError: If validation fails
    """
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


def load_adapter_metadata(
    h_e1_results_dir: str,
) -> list[dict]:
    """
    Load adapter_metadata.json from H-E1 results.

    Args:
        h_e1_results_dir: Path to H-E1 results directory

    Returns:
        List of dicts with keys: adapter_path, task, seed, category
    """
    meta_path = os.path.join(h_e1_results_dir, "adapter_metadata.json")

    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Adapter metadata not found: {meta_path}")

    with open(meta_path, 'r') as f:
        metadata = json.load(f)

    # Validate structure
    if not isinstance(metadata, list):
        raise ValueError("adapter_metadata.json should be a list")

    if len(metadata) != config.N_ADAPTERS:
        raise ValueError(
            f"Expected {config.N_ADAPTERS} adapters, got {len(metadata)}"
        )

    # Validate each entry has required keys
    required_keys = {'task', 'seed', 'category'}
    for i, entry in enumerate(metadata):
        missing = required_keys - set(entry.keys())
        if missing:
            raise ValueError(f"Entry {i} missing keys: {missing}")

    return metadata
