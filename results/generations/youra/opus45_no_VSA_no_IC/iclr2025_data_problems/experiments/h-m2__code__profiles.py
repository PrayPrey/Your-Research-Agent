"""Mode profile computation and persistence for h-m2."""
import json
import numpy as np


def compute_mode_profile(scores: dict) -> np.ndarray:
    """Compute L2-normalized mode profile from attribution scores.

    Args:
        scores: dict with keys 'mem', 'transfer', 'spurious' -> np.ndarray

    Returns:
        np.ndarray of shape [3]: normalized [mean_mem, mean_transfer, mean_spurious]
    """
    v = np.array([scores[m].mean() for m in ("mem", "transfer", "spurious")])
    norm = np.linalg.norm(v)
    return v / (norm + 1e-8)


def collect_seed_profile(results: dict, methods: list) -> dict:
    """Collect profile vectors for one seed.

    Args:
        results: {method: {mode: np.ndarray}} for one seed
        methods: list of method names

    Returns:
        {method: profile_vector[3]}
    """
    return {m: compute_mode_profile(results[m]) for m in methods}


def save_profiles(all_profiles: dict, path: str) -> None:
    """Save profiles dict to JSON."""
    data = {m: [v.tolist() for v in vs] for m, vs in all_profiles.items()}
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_profiles(path: str) -> dict:
    """Load profiles dict from JSON."""
    with open(path) as f:
        raw = json.load(f)
    return {m: [np.array(v) for v in vs] for m, vs in raw.items()}
