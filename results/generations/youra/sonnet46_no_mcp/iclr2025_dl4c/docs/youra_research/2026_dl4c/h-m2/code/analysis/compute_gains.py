import numpy as np
import pandas as pd
import warnings

CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]


def compute_pass1_gains(pass1_df: pd.DataFrame) -> np.ndarray:
    """Compute pass@1 gain per 500-step interval. Returns shape (n-1,)."""
    df = pass1_df.sort_values("step").reset_index(drop=True)
    vals = df["pass1"].values
    gains = np.diff(vals)
    assert len(gains) >= 5, f"Too few gains: {len(gains)}"
    return gains


def build_pooled_observations(data: dict) -> tuple:
    """Build pooled (density, gain) pairs across all 4 conditions.
    Returns (all_densities, all_gains, condition_labels)."""
    all_densities = []
    all_gains = []
    labels = []

    for cond in CONDITIONS:
        density_df = data[cond]["density"].sort_values("step").reset_index(drop=True)
        pass1_df = data[cond]["pass1"].sort_values("step").reset_index(drop=True)

        n_ckpts = min(len(density_df), len(pass1_df))
        n_intervals = min(n_ckpts - 1, 9)

        if n_intervals < 1:
            warnings.warn(f"Condition {cond}: insufficient data for gain computation")
            continue

        densities = density_df["reward_density"].values[:n_intervals]
        gains = np.diff(pass1_df["pass1"].values[:n_intervals + 1])

        all_densities.extend(densities.tolist())
        all_gains.extend(gains.tolist())
        labels.extend([cond] * n_intervals)

    n = len(all_densities)
    if n != 36:
        warnings.warn(f"Expected 36 pooled observations, got {n} (partial data)")

    return np.array(all_densities), np.array(all_gains), labels
