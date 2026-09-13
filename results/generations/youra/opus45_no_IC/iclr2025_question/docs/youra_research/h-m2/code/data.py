"""H-M2 Data Loading - Load JS-divergence matrix from H-E1 results"""
import json
import numpy as np
from pathlib import Path
from config import H_E1_RESULTS, BENCHMARK_NAMES


def load_js_matrix(path: Path = H_E1_RESULTS) -> np.ndarray:
    """Load 6x6 symmetric JS-divergence matrix from H-E1 results.json."""
    if not path.exists():
        raise FileNotFoundError(f"H-E1 results not found: {path}")

    with open(path, 'r') as f:
        data = json.load(f)

    matrix = np.array(data["js_matrix"])

    # Validate shape
    assert matrix.shape == (6, 6), f"Expected (6,6), got {matrix.shape}"

    # Validate symmetry
    assert np.allclose(matrix, matrix.T), "Matrix must be symmetric"

    return matrix


def get_benchmark_order() -> list:
    """Return benchmark order matching matrix indices."""
    return BENCHMARK_NAMES
