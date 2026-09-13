"""Data loader for H-M3 experiment.

Loads margin and correctness arrays from H-E1 cache.
Adapted from original spec which expected full logits - uses actual cache structure.
"""
import numpy as np
from pathlib import Path
from typing import Optional

from config import H_E1_CACHE_DIR, FAMILIES, EXPECTED_N, CACHE_FILE_PATTERNS


def load_margins_and_correctness(
    family: str,
    cache_dir: Optional[Path] = None,
) -> dict[str, np.ndarray]:
    """Load margin and correctness arrays for one family.

    Args:
        family: Model family name ('qwen' or 'mistral')
        cache_dir: Optional cache directory override

    Returns:
        Dictionary with keys:
            - base_margins: (N,) margin values for base model
            - base_correctness: (N,) binary correctness for base model
            - inst_margins: (N,) margin values for instruct model
            - inst_correctness: (N,) binary correctness for instruct model
    """
    cache_dir = cache_dir or H_E1_CACHE_DIR

    if family not in CACHE_FILE_PATTERNS:
        raise ValueError(f"Unknown family: {family}. Expected one of {list(CACHE_FILE_PATTERNS.keys())}")

    patterns = CACHE_FILE_PATTERNS[family]

    data = {}
    for key, filename in patterns.items():
        filepath = cache_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Cache file not found: {filepath}")
        data[key] = np.load(filepath)

    return data


def validate_cache(
    data: dict[str, np.ndarray],
    expected_n: int = EXPECTED_N,
) -> None:
    """Validate cache data shapes and values.

    Args:
        data: Dictionary from load_margins_and_correctness
        expected_n: Expected number of samples

    Raises:
        ValueError: If validation fails
    """
    required_keys = ["base_margins", "base_correctness", "inst_margins", "inst_correctness"]

    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")

        arr = data[key]
        if arr.shape != (expected_n,):
            raise ValueError(f"{key}: expected shape ({expected_n},), got {arr.shape}")

    # Validate correctness arrays are binary
    for key in ["base_correctness", "inst_correctness"]:
        unique_vals = np.unique(data[key])
        if not np.all(np.isin(unique_vals, [0, 1])):
            raise ValueError(f"{key}: expected binary values (0, 1), got {unique_vals}")

    # Validate margins are non-negative (margin = top1_logit - top2_logit)
    for key in ["base_margins", "inst_margins"]:
        if np.any(data[key] < 0):
            raise ValueError(f"{key}: expected non-negative margins")


def load_all_families(
    families: Optional[list[str]] = None,
    cache_dir: Optional[Path] = None,
) -> dict[str, dict[str, np.ndarray]]:
    """Load data for all specified families.

    Args:
        families: List of family names to load (default: FAMILIES from config)
        cache_dir: Optional cache directory override

    Returns:
        Dictionary mapping family -> data dict
    """
    families = families or FAMILIES
    cache_dir = cache_dir or H_E1_CACHE_DIR

    all_data = {}
    for family in families:
        data = load_margins_and_correctness(family, cache_dir)
        validate_cache(data)
        all_data[family] = data

    return all_data
