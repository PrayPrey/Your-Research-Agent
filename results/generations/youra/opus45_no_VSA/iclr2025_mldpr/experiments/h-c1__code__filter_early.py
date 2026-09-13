"""Early-run temporal filter for h-c1 robustness check."""
import pandas as pd
from config import MAX_RUNS_EARLY, MAX_DAYS_EARLY, MIN_DATASETS_EARLY, MIN_RUNS_PER_DATASET_EARLY, PATHS


def filter_early_runs(runs_df: pd.DataFrame, max_runs: int = MAX_RUNS_EARLY,
                      max_days: int = MAX_DAYS_EARLY) -> pd.DataFrame:
    """Filter to first N runs within M days of dataset upload.

    Tests whether metadata effect persists before community convergence.

    Args:
        runs_df: DataFrame with run_id, data_id, upload_time, upload_date, ...
        max_runs: Maximum runs per dataset (default: 50)
        max_days: Maximum days from upload (default: 90)

    Returns:
        DataFrame: Filtered early runs only
    """
    df = runs_df.copy()

    # Ensure datetime
    df["upload_time"] = pd.to_datetime(df["upload_time"])
    df["upload_date"] = pd.to_datetime(df["upload_date"])

    # Compute days since upload
    df["days_since_upload"] = (df["upload_time"] - df["upload_date"]).dt.days

    # Filter: within time window
    in_window = df[df["days_since_upload"] <= max_days].copy()

    # Filter: first N runs per dataset (sorted by upload_time)
    early_runs = (
        in_window
        .sort_values(["data_id", "upload_time"])
        .groupby("data_id")
        .head(max_runs)
    )

    return early_runs


def validate_sample_size(early_df: pd.DataFrame,
                         min_datasets: int = MIN_DATASETS_EARLY,
                         min_runs: int = MIN_RUNS_PER_DATASET_EARLY) -> dict:
    """Validate sufficient sample size in early-run subsample.

    Returns:
        dict with n_datasets, n_runs, pass (bool)
    """
    # Count datasets with >= min_runs
    runs_per_dataset = early_df.groupby("data_id").size()
    valid_datasets = (runs_per_dataset >= min_runs).sum()

    result = {
        "n_datasets": int(valid_datasets),
        "n_runs": len(early_df),
        "pass": valid_datasets >= min_datasets
    }

    return result


if __name__ == "__main__":
    # Test filter
    df = pd.read_parquet(PATHS["matched_runs_temporal"])
    early = filter_early_runs(df)
    print(f"Full: {len(df)} runs, Early: {len(early)} runs")
    print(f"Sample validation: {validate_sample_size(early)}")
