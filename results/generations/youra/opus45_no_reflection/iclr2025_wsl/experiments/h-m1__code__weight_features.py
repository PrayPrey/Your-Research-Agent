import numpy as np
from config import LAYER_KEYS


def extract_layer_statistics(state_dict: dict) -> np.ndarray:
    """Extract per-layer statistics from state_dict. Returns (25,) vector: 5 layers x 5 stats."""
    feats = []
    for key in LAYER_KEYS:
        w = state_dict[key].detach().cpu().numpy().ravel()
        feats.extend([w.mean(), w.std(), w.min(), w.max(), np.linalg.norm(w)])
    return np.array(feats)


def build_weight_feature_matrix(model_entries: list) -> tuple:
    """Build feature matrix from model entries.

    Args:
        model_entries: [(model_id, state_dict, test_acc), ...]

    Returns:
        features: (N, 25) array
        model_ids: list of model IDs in same order
    """
    rows, ids = [], []
    for model_id, state_dict, _ in model_entries:
        rows.append(extract_layer_statistics(state_dict))
        ids.append(model_id)
    return np.stack(rows), ids
