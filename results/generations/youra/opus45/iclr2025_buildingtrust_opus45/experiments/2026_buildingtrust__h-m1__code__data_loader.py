"""
Data loader for H-M1 Conditional Margin Inflation Analysis.
Loads cached arrays from H-E1 experiment.
"""

import json
import numpy as np
from pathlib import Path

from config import H_E1_CACHE_DIR, H_E1_RESULTS_JSON


def load_family_arrays(
    family: str,
    cache_dir: Path = None,
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


def validate_arrays(arrays: dict[str, np.ndarray]) -> None:
    """
    Validate loaded arrays for consistency.

    Raises:
        ValueError: If validation fails
    """
    # Check all arrays present
    required_keys = ["base_margins", "base_correctness", "inst_margins", "inst_correctness"]
    for key in required_keys:
        if key not in arrays:
            raise ValueError(f"Missing required array: {key}")

    # Check shapes - all should have same length N
    n_base = len(arrays["base_margins"])
    n_inst = len(arrays["inst_margins"])

    if len(arrays["base_correctness"]) != n_base:
        raise ValueError(f"Shape mismatch: base_margins ({n_base}) vs base_correctness ({len(arrays['base_correctness'])})")

    if len(arrays["inst_correctness"]) != n_inst:
        raise ValueError(f"Shape mismatch: inst_margins ({n_inst}) vs inst_correctness ({len(arrays['inst_correctness'])})")

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


def load_h_e1_results_json(json_path: Path = None) -> dict:
    """
    Load H-E1 experiment_results.json for reference.

    Args:
        json_path: Path to JSON file (defaults to config)

    Returns:
        Parsed JSON as dictionary
    """
    if json_path is None:
        json_path = H_E1_RESULTS_JSON

    if not json_path.exists():
        raise FileNotFoundError(f"H-E1 results not found: {json_path}")

    with open(json_path, "r") as f:
        return json.load(f)
