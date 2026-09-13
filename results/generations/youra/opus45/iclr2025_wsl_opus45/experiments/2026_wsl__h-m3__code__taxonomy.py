"""TaxonomyMatrix: Build FLAN taxonomy distance matrix."""

import os
from typing import Optional

import numpy as np

import config


def build_taxonomy_distance_matrix(
    task_labels: list[str],
    flan_categories: dict[str, str],
    mode: str = "binary",
) -> np.ndarray:
    """
    Build (N, N) taxonomy distance matrix.

    Args:
        task_labels: ordered list of task names for each adapter
        flan_categories: mapping task -> category string
        mode: "binary" (0=same, 1=different) or "hierarchical"

    Returns:
        taxonomy_matrix: (N, N) float array
    """
    n = len(task_labels)
    taxonomy_matrix = np.zeros((n, n), dtype=np.float64)

    for i in range(n):
        for j in range(n):
            if i == j:
                taxonomy_matrix[i, j] = 0.0
            else:
                cat_i = flan_categories.get(task_labels[i])
                cat_j = flan_categories.get(task_labels[j])

                if cat_i is None:
                    raise ValueError(f"Unknown task: {task_labels[i]}")
                if cat_j is None:
                    raise ValueError(f"Unknown task: {task_labels[j]}")

                if mode == "binary":
                    # 0 = same category, 1 = different category
                    taxonomy_matrix[i, j] = 0.0 if cat_i == cat_j else 1.0
                elif mode == "hierarchical":
                    # Future: implement hierarchical distances
                    taxonomy_matrix[i, j] = 0.0 if cat_i == cat_j else 1.0
                else:
                    raise ValueError(f"Unknown mode: {mode}")

    return taxonomy_matrix


def extract_task_labels_from_meta(
    adapter_meta: list[dict],
) -> list[str]:
    """
    Extract ordered task name list from adapter metadata dicts.

    Args:
        adapter_meta: List of dicts with 'task' key

    Returns:
        List of task names in same order as adapter_meta
    """
    return [m['task'] for m in adapter_meta]


def save_taxonomy_matrix(
    taxonomy_matrix: np.ndarray,
    results_dir: str,
    filename: str = "taxonomy_distances.npy",
) -> None:
    """
    Save taxonomy matrix to file.

    Args:
        taxonomy_matrix: Matrix to save
        results_dir: Directory to save to
        filename: Output filename
    """
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, filename)
    np.save(out_path, taxonomy_matrix)


def validate_taxonomy_matrix(
    taxonomy_matrix: np.ndarray,
    expected_n: int = 40,
) -> None:
    """
    Validate taxonomy distance matrix structure.

    Args:
        taxonomy_matrix: Matrix to validate
        expected_n: Expected dimension

    Raises:
        ValueError: If validation fails
    """
    # Check shape
    if taxonomy_matrix.shape != (expected_n, expected_n):
        raise ValueError(
            f"Expected shape ({expected_n}, {expected_n}), "
            f"got {taxonomy_matrix.shape}"
        )

    # Check symmetry
    if not np.allclose(taxonomy_matrix, taxonomy_matrix.T):
        raise ValueError("Taxonomy matrix is not symmetric")

    # Check diagonal is zero
    if not np.allclose(np.diag(taxonomy_matrix), 0):
        raise ValueError("Taxonomy matrix diagonal is not zero")

    # Check binary values (0 or 1)
    unique_vals = np.unique(taxonomy_matrix)
    if not all(v in [0.0, 1.0] for v in unique_vals):
        raise ValueError(f"Taxonomy matrix contains non-binary values: {unique_vals}")
