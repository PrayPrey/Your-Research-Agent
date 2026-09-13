import pandas as pd

def load_rf_subset(path: str, algo: str = "RandomForest", min_samples: int = 20) -> pd.DataFrame:
    """Load h-e1 parquet, filter algo_family==algo. Raises if <min_samples rows."""
    df = pd.read_parquet(path)
    df_rf = df[df["algo_family"] == algo].copy()
    if len(df_rf) < min_samples:
        raise ValueError(f"Only {len(df_rf)} {algo} rows (min: {min_samples})")
    return df_rf
