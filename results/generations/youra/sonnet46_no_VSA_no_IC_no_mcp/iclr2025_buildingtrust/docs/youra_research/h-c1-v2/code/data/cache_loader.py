"""Load pre-computed h-c1 results and h-m1 label-preservation mask."""
import json, os
import numpy as np
from typing import Dict, Optional

from typing import NamedTuple

# Redefine CellECE locally to avoid h-c1 import chain issues
class CellECE(NamedTuple):
    cell_id: str
    model_id: str
    ece_clean: float
    ece_adv: float
    delta_ece: float
    n_clean: int
    n_adv: int


def load_h_c1_cache(results_file: str) -> Dict[str, Dict[str, CellECE]]:
    """
    Load pre-computed h-c1 CellECE objects from hc1_results.json.
    JSON cells is a list of dicts with keys:
      model_id, cell_id, ece_clean, ece_adv, delta_ece, n_clean, n_adv
    Returns: {model_id: {cell_id: CellECE}}
    """
    if not os.path.exists(results_file):
        raise FileNotFoundError(f"H-C1 cache not found: {results_file}")

    with open(results_file) as f:
        data = json.load(f)

    if "cells" not in data:
        raise ValueError(f"hc1_results.json missing 'cells' key")

    cache: Dict[str, Dict[str, CellECE]] = {}
    for cell in data["cells"]:
        model_id = cell["model_id"]
        cell_id = cell["cell_id"]
        cell_ece = CellECE(
            cell_id=cell_id,
            model_id=model_id,
            ece_clean=cell["ece_clean"],
            ece_adv=cell["ece_adv"],
            delta_ece=cell["delta_ece"],
            n_clean=cell["n_clean"],
            n_adv=cell["n_adv"],
        )
        if model_id not in cache:
            cache[model_id] = {}
        cache[model_id][cell_id] = cell_ece

    print(f"✓ Loaded h-c1 cache: {len(cache)} models, cells: {list(next(iter(cache.values())).keys())}")
    return cache


def load_label_preservation_mask(mask_path: str) -> Optional[np.ndarray]:
    """Load h-m1 label-preservation mask. Returns bool array or None if missing."""
    if not os.path.exists(mask_path):
        print(f"⚠ Label preservation mask not found at {mask_path} — skipping")
        return None
    return np.load(mask_path)


def validate_cache_schema(data: dict) -> bool:
    """Verify cache contains 'cells' with required fields."""
    if "cells" not in data:
        return False
    required = {"model_id", "cell_id", "ece_clean", "ece_adv", "delta_ece", "n_clean", "n_adv"}
    if not data["cells"]:
        return False
    return required.issubset(set(data["cells"][0].keys()))
