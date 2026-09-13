import os
import warnings
import numpy as np
from typing import Dict, Optional, Tuple


def _load_npz(path: str) -> Tuple[Dict[str, np.ndarray], np.ndarray]:
    data = np.load(path)
    scores = {
        "min":     data["min_scores"].astype(float),
        "mean":    data["mean_scores"].astype(float),
        "raw_sum": data["sum_scores"].astype(float),
    }
    labels = data["labels"].astype(int)

    if len(labels) < 100:
        raise ValueError(f"Too few samples ({len(labels)}) in {path}")
    if labels.min() == labels.max():
        raise ValueError(f"Only one class in labels from {path}")

    # Normalize to positive convention (H-E1 stores positive negated log-probs)
    if scores["min"].mean() < 0:
        scores = {k: -v for k, v in scores.items()}

    return scores, labels


def load_scores(
    model_key: str,
    dataset_name: str,
    h_e1_dir: str,
    h_m2_dir: str,
) -> Tuple[Optional[Dict[str, np.ndarray]], Optional[np.ndarray]]:
    fname = f"scores_{model_key}_{dataset_name}.npz"
    for base_dir in [h_e1_dir, h_m2_dir]:
        path = os.path.join(base_dir, fname)
        if os.path.exists(path):
            try:
                scores, labels = _load_npz(path)
                return scores, labels
            except Exception as e:
                warnings.warn(f"Failed to load {path}: {e}")
    return None, None
