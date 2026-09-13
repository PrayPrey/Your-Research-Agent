import numpy as np


def build_labels(item_ids: list[int], contaminated_ids: set) -> np.ndarray:
    """1 if item_id in contaminated_ids else 0, shape (n_items,)."""
    return np.array([1 if idx in contaminated_ids else 0 for idx in item_ids], dtype=np.int32)
