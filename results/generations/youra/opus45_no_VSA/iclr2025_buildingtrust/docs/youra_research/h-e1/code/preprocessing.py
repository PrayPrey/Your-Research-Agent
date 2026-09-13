"""Preprocessing: filtering, imputation, matrix construction."""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

BENCHMARKS = ["IFEval", "BBH", "MATH Lvl 5", "GPQA", "MUSR", "MMLU-PRO"]
BENCHMARK_COLS = ["IFEval", "BBH", "MATH Lvl 5", "GPQA", "MUSR", "MMLU-PRO"]


def filter_models(
    df: pd.DataFrame,
    min_benchmarks: int = 4,
    date_start: str = "2023-01-01",
    date_end: str = "2025-12-31",
    min_sample_size: int = 80,
) -> pd.DataFrame:
    """Apply inclusion criteria per FR-02."""
    n_before = len(df)

    # Filter by param count availability
    if "#Params (B)" in df.columns:
        df = df[df["#Params (B)"].notna() & (df["#Params (B)"] > 0)].copy()
    elif "Params" in df.columns:
        df = df[df["Params"].notna() & (df["Params"] > 0)].copy()
    n_after_params = len(df)
    print(f"Filter: params available: {n_before} -> {n_after_params}")

    # Filter by benchmark coverage
    available_benchmarks = [b for b in BENCHMARK_COLS if b in df.columns]
    df["benchmark_count"] = df[available_benchmarks].notna().sum(axis=1)
    df = df[df["benchmark_count"] >= min_benchmarks].copy()
    n_after_bench = len(df)
    print(f"Filter: >={min_benchmarks} benchmarks: {n_after_params} -> {n_after_bench}")

    # Date filter if date column exists
    if "Submission Date" in df.columns:
        df["submission_dt"] = pd.to_datetime(df["Submission Date"], errors="coerce")
        df = df[
            (df["submission_dt"] >= date_start) &
            (df["submission_dt"] <= date_end)
        ].copy()
    n_after_date = len(df)
    print(f"Filter: date range: {n_after_bench} -> {n_after_date}")

    if len(df) < min_sample_size:
        raise ValueError(
            f"N={len(df)} after filtering, below minimum {min_sample_size}. "
            f"Counts: params={n_after_params}, bench={n_after_bench}, date={n_after_date}"
        )

    return df


def impute_missing(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Column-mean imputation for remaining missing values."""
    df = df.copy()
    for col in cols:
        if col in df.columns:
            missing_pct = df[col].isna().mean()
            if missing_pct > 0.30:
                print(f"Warning: {col} has {missing_pct:.1%} missing values")
            df[col] = df[col].fillna(df[col].mean())
    return df


def build_matrices(df: pd.DataFrame) -> tuple:
    """Build Y (benchmarks) and X (confounds) matrices.

    Returns:
        Y: (N, 6) standardized benchmark scores
        X: (N, 2) confounds [log_params, release_date_ordinal]
        model_names: list of model identifiers
    """
    available_benchmarks = [b for b in BENCHMARK_COLS if b in df.columns]
    df = impute_missing(df, available_benchmarks)

    Y_raw = df[available_benchmarks].values.astype(float)
    scaler = StandardScaler()
    Y = scaler.fit_transform(Y_raw)

    # Build confounds
    if "#Params (B)" in df.columns:
        log_params = np.log10(df["#Params (B)"].values.astype(float))
    else:
        log_params = np.log10(df["Params"].values.astype(float))

    if "submission_dt" in df.columns:
        release_ordinal = df["submission_dt"].apply(lambda x: x.toordinal() if pd.notna(x) else np.nan).values.astype(float)
        release_ordinal = np.nan_to_num(release_ordinal, nan=np.nanmean(release_ordinal))
    else:
        release_ordinal = np.zeros(len(df))

    X = np.column_stack([log_params, release_ordinal])

    model_names = df["fullname"].tolist() if "fullname" in df.columns else df.index.tolist()

    return Y, X, model_names, available_benchmarks
