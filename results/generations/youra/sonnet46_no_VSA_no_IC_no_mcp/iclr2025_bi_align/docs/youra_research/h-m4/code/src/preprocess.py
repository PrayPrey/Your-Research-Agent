import numpy as np
import pandas as pd
from pathlib import Path


def load_raw(data_raw_path) -> pd.DataFrame:
    assert Path(data_raw_path).exists(), f"Raw data not found: {data_raw_path}"
    df = pd.read_csv(data_raw_path)
    assert {"kl_budget", "proxy_raw", "gold_raw"}.issubset(df.columns), "Missing columns"
    assert len(df) >= 6, f"N={len(df)} insufficient (min 6)"
    assert not df.isnull().any().any(), "NaN in raw data"
    return df


def normalize(series: pd.Series) -> pd.Series:
    return (series - series.min()) / (series.max() - series.min())


def compute_gap(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["proxy_norm"] = normalize(df["proxy_raw"])
    df["gold_norm"] = normalize(df["gold_raw"])
    df["gap"] = df["proxy_norm"] - df["gold_norm"]
    assert df["gap"].std() > 0.01, "Gap near-zero variance — normalization error"
    return df


def validate_gap(df: pd.DataFrame) -> None:
    assert not df.isnull().any().any(), "NaN in processed data"
    kl = df["kl_budget"].values
    assert all(kl[i] <= kl[i + 1] for i in range(len(kl) - 1)), "kl_budget not monotonically non-decreasing"


def save_gap(df: pd.DataFrame, path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df[["kl_budget", "proxy_norm", "gold_norm", "gap"]].to_csv(path, index=False)
