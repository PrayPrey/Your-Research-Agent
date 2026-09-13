"""
Data loader for H-M2 Percentile-Normalized Monotonicity Attenuation Analysis.
Loads cached arrays from H-E1 experiment.
"""

import numpy as np
from pathlib import Path
from typing import Optional

from config import H_E1_CACHE_DIR, FAMILIES


def load_family_arrays(
    family: str,
    cache_dir: Optional[Path] = None,
) -> dict[str, np.ndarray]:
    """
    Load base/instruct margins and correctness arrays for one model family.

    Args:
        family: Model family name ("qwen", "mistral")
        cache_dir: Path to H-E1 cache directory (defaults to config)

    Returns:
        Dictionary with keys:
        - base_margins: (N,) float array
        - base_correctness: (N,) int array {0, 1}
        - inst_margins: (N,) float array
        - inst_correctness: (N,) int array {0, 1}
    """
    if cache_dir is None:
        cache_dir = H_E1_CACHE_DIR

    family_dir = cache_dir / family

    if not family_dir.exists():
        raise FileNotFoundError(f"Cache directory not found: {family_dir}")

    # Find array files - H-E1 uses model ID naming
    # Pattern: {org}_{model}_margins.npy, {org}_{model}_correctness.npy
    files = list(family_dir.glob("*.npy"))

    if len(files) < 4:
        raise FileNotFoundError(f"Expected 4 .npy files in {family_dir}, found {len(files)}")

    # Sort files to find base and instruct variants
    base_margins = None
    base_correctness = None
    inst_margins = None
    inst_correctness = None

    for f in files:
        name = f.stem.lower()
        if "instruct" in name or "chat" in name:
            # Instruct model
            if "margin" in name:
                inst_margins = np.load(f)
            elif "correct" in name:
                inst_correctness = np.load(f)
        else:
            # Base model
            if "margin" in name:
                base_margins = np.load(f)
            elif "correct" in name:
                base_correctness = np.load(f)

    # Validate all arrays found
    arrays = {
        "base_margins": base_margins,
        "base_correctness": base_correctness,
        "inst_margins": inst_margins,
        "inst_correctness": inst_correctness,
    }

    for key, arr in arrays.items():
        if arr is None:
            raise FileNotFoundError(f"Could not find {key} array for family {family}")

    return arrays


def validate_arrays(
    arrays: dict[str, np.ndarray],
    expected_n: int = 14042,
) -> None:
    """
    Validate loaded arrays for consistency.

    Args:
        arrays: Dictionary of arrays from load_family_arrays
        expected_n: Expected sample count (default: 14042 for MMLU test)

    Raises:
        ValueError: If validation fails
    """
    # Check all arrays present
    required_keys = ["base_margins", "base_correctness", "inst_margins", "inst_correctness"]
    for key in required_keys:
        if key not in arrays:
            raise ValueError(f"Missing required array: {key}")

    # Check shapes - all should have same length N
    for key in required_keys:
        arr = arrays[key]

        # Check 1D
        if arr.ndim != 1:
            raise ValueError(f"{key} must be 1D, got shape {arr.shape}")

        # Check sample count
        if len(arr) != expected_n:
            raise ValueError(f"{key} has {len(arr)} samples, expected {expected_n}")

    # Check correctness values are binary
    for key in ["base_correctness", "inst_correctness"]:
        unique_vals = np.unique(arrays[key])
        if not np.all(np.isin(unique_vals, [0, 1])):
            raise ValueError(f"Invalid values in {key}: expected binary {{0, 1}}, got {unique_vals}")

    # Check margins are finite
    for key in ["base_margins", "inst_margins"]:
        if not np.all(np.isfinite(arrays[key])):
            n_invalid = np.sum(~np.isfinite(arrays[key]))
            raise ValueError(f"Non-finite values in {key}: {n_invalid} invalid entries")


def load_all_families(
    families: Optional[list[str]] = None,
    cache_dir: Optional[Path] = None,
) -> dict[str, dict[str, np.ndarray]]:
    """
    Load arrays for all families.

    Args:
        families: List of family names (defaults to FAMILIES from config)
        cache_dir: Path to H-E1 cache directory

    Returns:
        Dictionary mapping family name to arrays dict
    """
    if families is None:
        families = FAMILIES

    result = {}
    for family in families:
        result[family] = load_family_arrays(family, cache_dir)

    return result
