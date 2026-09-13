"""Feature extraction: per-layer weight statistics."""
import numpy as np
import torch
from torch import Tensor
from typing import Tuple, List


def layer_statistics(w: Tensor) -> np.ndarray:
    """Compute 7 statistics for one weight tensor.

    Stats: mean, std, min, max, frobenius_norm, spectral_norm, sparsity
    Dropped L2 norm (redundant with Fro for flattened tensor) to hit 7×21=147.
    """
    w_np = w.detach().float().numpy()
    v = w_np.flatten()

    mean = float(v.mean())
    std = float(v.std())
    min_val = float(v.min())
    max_val = float(v.max())
    fro = float(np.linalg.norm(w_np))

    w_2d = w_np.reshape(w_np.shape[0], -1)
    try:
        svs = np.linalg.svd(w_2d, compute_uv=False)
        spectral = float(svs[0]) if len(svs) > 0 else 0.0
    except:
        spectral = 0.0

    sparsity = float((np.abs(v) < 1e-6).mean())

    return np.array([mean, std, min_val, max_val, fro, spectral, sparsity], dtype=np.float32)


def extract_weight_statistics(state_dict: dict) -> np.ndarray:
    """Extract statistics from all weight tensors (skip 1D params like bias/BN)."""
    feats = []
    for name, param in state_dict.items():
        if 'weight' in name.lower() and param.dim() >= 2:
            feats.append(layer_statistics(param))

    if not feats:
        return np.zeros(147, dtype=np.float32)

    return np.concatenate(feats)


def build_feature_matrix(items: List[Tuple[dict, float]]) -> Tuple[np.ndarray, np.ndarray]:
    """Build feature matrix X and label vector y from (state_dict, accuracy) pairs."""
    X_list = []
    y_list = []

    for state_dict, acc in items:
        feat = extract_weight_statistics(state_dict)
        X_list.append(feat)
        y_list.append(acc)

    X = np.stack(X_list)
    y = np.array(y_list, dtype=np.float32)

    return X, y
