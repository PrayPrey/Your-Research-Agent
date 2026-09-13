# Entropy computation module for h-m1
import numpy as np
from scipy.stats import entropy as scipy_entropy
from collections import Counter
from config import N_BINS


def compute_preprocessing_entropy(flow_components: list) -> float:
    """Shannon entropy (base 2) of component frequency distribution. Empty list -> 0.0."""
    if not flow_components:
        return 0.0
    counts = Counter(flow_components)
    probs = np.array(list(counts.values())) / len(flow_components)
    result = float(scipy_entropy(probs, base=2))
    if not np.isfinite(result):
        return 0.0
    return result


def bin_continuous(values: list, n_bins: int = N_BINS) -> np.ndarray:
    """np.digitize into n_bins equal-width bins. Returns bin index array."""
    arr = np.array(values, dtype=float)
    if len(arr) == 0:
        return np.array([], dtype=int)
    vmin, vmax = arr.min(), arr.max()
    if vmin == vmax:
        return np.zeros(len(arr), dtype=int)
    bins = np.linspace(vmin, vmax, n_bins + 1)
    return np.digitize(arr, bins[:-1]) - 1


def compute_hyperparameter_entropy(hyperparams: dict) -> float:
    """Discretize numeric values into bins, then Shannon entropy. Empty dict -> 0.0."""
    if not hyperparams:
        return 0.0

    numeric_vals = []
    for v in hyperparams.values():
        try:
            numeric_vals.append(float(v))
        except (ValueError, TypeError):
            continue

    if not numeric_vals:
        return 0.0

    bins = bin_continuous(numeric_vals, n_bins=N_BINS)
    counts = np.bincount(bins)
    probs = counts[counts > 0] / len(bins)
    result = float(scipy_entropy(probs, base=2))
    if not np.isfinite(result):
        return 0.0
    return result
