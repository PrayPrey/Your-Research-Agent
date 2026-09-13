import numpy as np
import pandas as pd


def compute_entropy_from_density(density: float) -> float:
    """Binary entropy H(p) = -p*log2(p) - (1-p)*log2(1-p). Edge: p<=0 or p>=1 -> 0.0."""
    p = float(density)
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * np.log2(p) - (1.0 - p) * np.log2(1.0 - p)


def add_entropy_column(density_df: pd.DataFrame) -> pd.DataFrame:
    """Adds 'entropy' column to density_df; returns new DataFrame."""
    df = density_df.copy()
    df["entropy"] = df["reward_density"].apply(compute_entropy_from_density)
    return df


def compute_early_mean_entropy(density_df: pd.DataFrame, max_step: int = 2500) -> float:
    """Mean entropy for rows where step <= max_step."""
    early = density_df[density_df["step"] <= max_step]
    if len(early) == 0:
        return 0.0
    return float(early["entropy"].mean())


def compare_entropy_direction(data: dict) -> dict:
    """Returns delta_entropy = mean_curriculum - mean_uniform for steps<=2500."""
    curriculum_df = add_entropy_column(data["curriculum"]["density"])
    uniform_df = add_entropy_column(data["uniform"]["density"])

    mean_curriculum = compute_early_mean_entropy(curriculum_df)
    mean_uniform = compute_early_mean_entropy(uniform_df)

    return {
        "mean_entropy_curriculum_early": mean_curriculum,
        "mean_entropy_uniform_early": mean_uniform,
        "delta_entropy": mean_curriculum - mean_uniform,
    }
