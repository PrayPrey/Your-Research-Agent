"""Mislabel injection for attribution evaluation"""
import numpy as np
import json
from typing import List, Tuple

def inject_mislabels(labels: List[int], fraction: float, seed: int) -> Tuple[List[int], List[int]]:
    """Flip binary labels for `fraction` of indices. Returns (flipped_labels, mislabeled_indices)."""
    rng = np.random.default_rng(seed)
    n_flip = int(len(labels) * fraction)
    indices = rng.choice(len(labels), size=n_flip, replace=False)
    flipped = list(labels)
    for idx in indices:
        flipped[idx] = 1 - flipped[idx]
    return flipped, sorted(indices.tolist())

def save_mislabeled_indices(indices: List[int], path: str) -> None:
    with open(path, 'w') as f:
        json.dump(indices, f)

def load_mislabeled_indices(path: str) -> List[int]:
    with open(path, 'r') as f:
        return json.load(f)
