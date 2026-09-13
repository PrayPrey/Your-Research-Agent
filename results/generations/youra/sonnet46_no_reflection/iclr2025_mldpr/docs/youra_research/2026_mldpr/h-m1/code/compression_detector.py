"""H-M1: Compression Detector — 1.5σ threshold + consecutive flagging."""
import pandas as pd
import numpy as np


def flag_compression(
    panel_df: pd.DataFrame,
    sigma_map: pd.Series,
    threshold: float = 1.5,
    min_consecutive: int = 2,
) -> pd.DataFrame:
    """Merge sigma_map; add 'compressed' bool and 'compression_event' rolling indicator.
    Returns: panel_df + [sigma_meas, compressed, compression_event]
    """
    df = panel_df.copy()
    sigma_df = sigma_map.reset_index()
    sigma_df.columns = ["task", "dataset", "sigma_meas"]
    df = df.merge(sigma_df, on=["task", "dataset"], how="left")

    # Fill missing sigma with median
    median_sigma = df["sigma_meas"].dropna().median()
    if pd.isna(median_sigma) or median_sigma == 0:
        median_sigma = 1.0
    df["sigma_meas"] = df["sigma_meas"].fillna(median_sigma)

    # Flag quarters where score variance < threshold * sigma
    df["compressed"] = (df["score_var_top10"] < threshold * df["sigma_meas"]).astype(float)
    df["compressed"] = df["compressed"].where(df["score_var_top10"].notna(), other=np.nan)

    # Require >= min_consecutive consecutive compressed quarters
    def rolling_consecutive(s):
        return s.rolling(min_consecutive, min_periods=min_consecutive).min().fillna(0)

    df["compression_event"] = (
        df.groupby("benchmark_id")["compressed"]
        .transform(rolling_consecutive)
    )
    df["compression_event"] = df["compression_event"].fillna(0)
    return df


def summarize_compression(panel_df: pd.DataFrame) -> dict:
    """Count compression events across panel.
    Returns: {'n_compression_events': int, 'n_qualifying_benchmarks': int, 'pct_compressed': float}
    """
    if "compression_event" not in panel_df.columns:
        return {"n_compression_events": 0, "n_qualifying_benchmarks": 0, "pct_compressed": 0.0}

    n_events = int((panel_df["compression_event"] == 1.0).sum())
    n_benchmarks = int(
        panel_df[panel_df["compression_event"] == 1.0]["benchmark_id"].nunique()
    )
    total_benchmarks = int(panel_df["benchmark_id"].nunique())
    pct = n_benchmarks / total_benchmarks if total_benchmarks > 0 else 0.0

    return {
        "n_compression_events": n_events,
        "n_qualifying_benchmarks": n_benchmarks,
        "pct_compressed": round(pct, 4),
    }
