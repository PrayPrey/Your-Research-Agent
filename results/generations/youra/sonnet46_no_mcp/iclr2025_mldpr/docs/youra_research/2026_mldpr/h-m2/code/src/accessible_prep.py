"""H-M2 accessible prep: compute 12-month run counts and accessible score splits."""
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def compute_12m_run_counts(datasets_df: pd.DataFrame, runs_df: pd.DataFrame, window_days: int = 365) -> pd.DataFrame:
    """Add run_count_12m column: count of runs within window_days of dataset upload."""
    df = datasets_df.copy()
    if runs_df is None or len(runs_df) == 0:
        df["run_count_12m"] = 0
        return df
    runs = runs_df.copy()
    runs["upload_time"] = pd.to_datetime(runs["upload_time"], errors="coerce")
    merged = df[["did", "upload_date"]].merge(runs, on="did", how="left")
    merged["upload_date"] = pd.to_datetime(merged["upload_date"], errors="coerce")
    merged["days_since"] = (merged["upload_time"] - merged["upload_date"]).dt.days
    valid = merged[(merged["days_since"] >= 0) & (merged["days_since"] <= window_days)]
    counts = valid.groupby("did").size().reset_index(name="run_count_12m")
    df = df.merge(counts, on="did", how="left")
    df["run_count_12m"] = df["run_count_12m"].fillna(0).astype(int)
    return df


def compute_accessible_score(datasets_df: pd.DataFrame, fair_scores_df: pd.DataFrame) -> pd.DataFrame:
    """Merge fair_A and compute high_accessible (median split)."""
    df = datasets_df.copy()
    if "fair_A" not in df.columns:
        scores = fair_scores_df[["did", "fair_A"]].copy()
        df = df.merge(scores, on="did", how="left")
    median_a = df["fair_A"].median()
    df["high_accessible"] = (df["fair_A"] >= median_a).astype(int)
    logger.info(f"Accessible median split at {median_a:.3f}: high={df['high_accessible'].sum()}, low={(df['high_accessible']==0).sum()}")
    return df


def build_analysis_df(datasets_df: pd.DataFrame, runs_df: pd.DataFrame, fair_scores_df: pd.DataFrame, min_pairs: int = 30) -> pd.DataFrame:
    """Full pipeline: 12m counts → accessible score → validate."""
    df = compute_12m_run_counts(datasets_df, runs_df)
    df = compute_accessible_score(df, fair_scores_df)
    validate_preconditions(df, min_pairs)
    return df


def validate_preconditions(df: pd.DataFrame, min_pairs: int = 30):
    """Raise ValueError if groups too small for analysis."""
    if "high_accessible" not in df.columns:
        raise ValueError("high_accessible column missing")
    n_high = (df["high_accessible"] == 1).sum()
    n_low = (df["high_accessible"] == 0).sum()
    min_group = min(n_high, n_low)
    if min_group < min_pairs:
        raise ValueError(f"Insufficient group size: min({n_high},{n_low})={min_group} < {min_pairs}")
    logger.info(f"Preconditions OK: high={n_high}, low={n_low}, min_pairs={min_pairs}")
