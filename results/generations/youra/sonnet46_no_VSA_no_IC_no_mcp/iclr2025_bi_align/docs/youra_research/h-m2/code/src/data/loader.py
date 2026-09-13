import pandas as pd

REQUIRED_COLS = ["kl_budget", "rm_score", "gold_preference"]


def load_dataset(csv_path: str) -> pd.DataFrame:
    """Load h-m1 divergence curve CSV; validate columns; sort by kl_budget; assert N >= 5."""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df[REQUIRED_COLS].isnull().any().any():
        raise ValueError("NaN values found in required columns")

    df = df.sort_values("kl_budget").reset_index(drop=True)

    if len(df) < 5:
        raise ValueError(f"Too few rows: {len(df)} < 5")

    return df
