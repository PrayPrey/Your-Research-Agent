"""LogLoader: Load and validate H-E1 reward density CSV logs."""

import os
import numpy as np
import pandas as pd

CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]
LOG_DIR = "h-e1/logs"
WINDOW_SIZE = 500


def load_reward_density_logs(log_dir: str = LOG_DIR) -> dict:
    """Load all 4 condition CSVs. Returns {condition: DataFrame(columns=[step, reward_density])}."""
    logs = {}
    for condition in CONDITIONS:
        csv_path = os.path.join(log_dir, f"reward_density_{condition}.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"Log file not found: {csv_path}. Run run_training.py first."
            )
        df = pd.read_csv(csv_path)
        if "step" not in df.columns or "reward_density" not in df.columns:
            raise ValueError(
                f"CSV {csv_path} missing required columns. Expected: step, reward_density"
            )
        logs[condition] = df
    return logs


def validate_full_training(
    logs: dict,
    min_rows: int = 10,
) -> tuple:
    """Validate all conditions have >= min_rows. Returns (all_valid, {condition: row_count}).
    Raises ValueError with guidance if any condition fails."""
    counts = {}
    all_valid = True
    for condition in CONDITIONS:
        df = logs.get(condition)
        if df is None:
            counts[condition] = 0
            all_valid = False
        else:
            counts[condition] = len(df)

    for c, n in counts.items():
        if n < min_rows:
            all_valid = False
            raise ValueError(
                f"Condition {c} has {n} rows, expected >= {min_rows}. Run run_training.py first."
            )

    return all_valid, counts


def compute_early_phase_density(
    df: pd.DataFrame,
    max_step: int = 2500,
    window_size: int = WINDOW_SIZE,
) -> np.ndarray:
    """Aggregate per-step rows into per-checkpoint windows for steps <= max_step.
    Returns shape (5,) — mean density for windows [1-500, 501-1000, ..., 2001-2500]."""
    early = df[df["step"] <= max_step].copy()
    early = early.assign(window=(early["step"] - 1) // window_size)
    result = early.groupby("window")["reward_density"].mean().values
    # Ensure shape (5,) — pad with NaN if fewer windows
    expected = max_step // window_size
    if len(result) < expected:
        result = np.pad(result, (0, expected - len(result)), constant_values=np.nan)
    return result.astype(float)


def compute_late_phase_density(
    df: pd.DataFrame,
    min_step: int = 2501,
    window_size: int = WINDOW_SIZE,
) -> np.ndarray:
    """Aggregate per-step rows into per-checkpoint windows for steps > min_step.
    Returns shape (5,) — mean density for windows [2501-3000, ..., 4501-5000]."""
    late = df[df["step"] > min_step].copy()
    late = late.assign(window=(late["step"] - 1) // window_size)
    result = late.groupby("window")["reward_density"].mean().values
    expected = 5
    if len(result) < expected:
        result = np.pad(result, (0, expected - len(result)), constant_values=np.nan)
    return result.astype(float)
