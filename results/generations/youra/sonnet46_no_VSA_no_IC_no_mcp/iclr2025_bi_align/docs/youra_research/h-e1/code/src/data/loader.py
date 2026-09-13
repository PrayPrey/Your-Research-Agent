import pandas as pd

REQUIRED_COLS = ["kl_budget", "rm_score", "gold_preference"]


def load_dataset(csv_path: str, dataset_name: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"{dataset_name}: missing columns {missing}")
    paired = df[REQUIRED_COLS].dropna()
    if len(paired) < 5:
        raise ValueError(
            f"{dataset_name}: only {len(paired)} non-null paired rows (need >= 5)"
        )
    return df
