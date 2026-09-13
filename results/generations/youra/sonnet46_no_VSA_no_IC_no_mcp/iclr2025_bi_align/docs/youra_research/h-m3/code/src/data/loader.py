"""Data loader for H-M3: loads H-M2 normalized gap CSV."""
import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ["kl_budget", "gap"]
MIN_N = 5


def load_dataset(csv_path: str, required_columns=None, min_n: int = MIN_N):
    """
    Load H-M2 output CSV; validate columns and row count.

    Returns:
        (kl_values, gap_values): each np.ndarray of shape (N,)
    """
    if required_columns is None:
        required_columns = REQUIRED_COLUMNS

    df = pd.read_csv(csv_path)

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found: {list(df.columns)}")

    df = df.dropna(subset=required_columns)
    if len(df) < min_n:
        raise ValueError(f"Insufficient data: N={len(df)}, minimum {min_n} required")

    df = df.sort_values("kl_budget").reset_index(drop=True)

    kl_values = df["kl_budget"].values.astype(np.float64)
    gap_values = df["gap"].values.astype(np.float64)

    assert kl_values.shape == gap_values.shape, "Shape mismatch between kl_budget and gap"
    print(f"✓ Loaded {len(df)} observations from {csv_path}")
    print(f"  kl_budget range: [{kl_values.min():.2f}, {kl_values.max():.2f}]")
    print(f"  gap range: [{gap_values.min():.4f}, {gap_values.max():.4f}]")

    return kl_values, gap_values
