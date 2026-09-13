"""Data loading and validation for h-c1."""
import numpy as np
import pandas as pd


def load_attribution_scores(npz_path: str) -> dict[str, np.ndarray]:
    """Load h-m1 attribution scores from NPZ file."""
    if not npz_path:
        raise FileNotFoundError("NPZ path not specified")

    try:
        data = np.load(npz_path)
        return {k: data[k] for k in data.files}
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Attribution scores not found at {npz_path}. "
            "Run h-m1 experiment first to generate attribution_scores.npz"
        )


def validate_scores(
    scores: dict[str, np.ndarray],
    methods: tuple,
    modes: tuple,
    min_samples: int
) -> None:
    """Validate all required score arrays exist and have valid values."""
    for method in methods:
        for mode in modes:
            key = f"{method}_{mode}"
            if key not in scores:
                raise ValueError(f"Missing key: {key}")

            arr = scores[key]
            if len(arr) < min_samples:
                raise ValueError(f"{key} has {len(arr)} samples, need >= {min_samples}")

            if np.any(np.isnan(arr)) or np.any(np.isinf(arr)):
                raise ValueError(f"{key} contains NaN or Inf values")


def build_mode_profile_df(
    scores: dict[str, np.ndarray],
    method: str,
    modes: tuple
) -> pd.DataFrame:
    """Build DataFrame with rows=probes, cols=modes for one method."""
    return pd.DataFrame({
        mode: scores[f"{method}_{mode}"]
        for mode in modes
    })
