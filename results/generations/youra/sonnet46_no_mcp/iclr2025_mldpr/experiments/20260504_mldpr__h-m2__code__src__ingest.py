"""H-M1 data ingestion: load H-E1 scores, fetch OpenML run timestamps, merge cohort."""
import json
import os
import time
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

REQUIRED_HE1_COLS = {"did", "fair_aggregate", "fair_F", "fair_A", "fair_I", "fair_R", "status"}


def load_he1_scores(scores_csv: str) -> pd.DataFrame:
    """Load H-E1 FAIR proxy scores CSV.
    Returns: DataFrame[did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, status]
    Raises: FileNotFoundError if CSV missing, ValueError if columns missing.
    """
    if not os.path.exists(scores_csv):
        raise FileNotFoundError(f"H-E1 scores CSV not found: {scores_csv}")
    df = pd.read_csv(scores_csv)
    missing = REQUIRED_HE1_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in H-E1 scores CSV: {missing}")
    df["did"] = df["did"].astype(int)
    df = df[df["status"] != "error"].copy()
    logger.info(f"Loaded {len(df)} H-E1 scores from {scores_csv}")
    return df[["did", "fair_aggregate", "fair_F", "fair_A", "fair_I", "fair_R", "status"]]


def fetch_run_timestamps(
    dataset_ids: list,
    cache_dir: str,
    retry_max: int = 3,
) -> pd.DataFrame:
    """Fetch first_run_timestamp and run_count per dataset via OpenML API.

    Strategy: bulk-fetch all tasks, filter to our dataset IDs, then batch-fetch
    runs by task ID (OpenML does not support dataset_id filter on runs directly).
    Results are cached to cache_dir/run_timestamps_bulk.json.

    Returns: DataFrame[did, first_run_timestamp, run_count]
    """
    import openml
    os.makedirs(cache_dir, exist_ok=True)
    bulk_cache = os.path.join(cache_dir, "run_timestamps_bulk.json")

    did_set = set(int(d) for d in dataset_ids)

    if os.path.exists(bulk_cache):
        with open(bulk_cache) as f:
            records = json.load(f)
        logger.info(f"Loaded run timestamps from bulk cache ({len(records)} records)")
        df = pd.DataFrame(records)
        df["did"] = df["did"].astype(int)
        df["first_run_timestamp"] = pd.to_datetime(df["first_run_timestamp"], errors="coerce")
        df["run_count"] = df["run_count"].fillna(0).astype(int)
        return df[["did", "first_run_timestamp", "run_count"]]

    # Step 1: fetch all tasks and filter to our dataset IDs
    logger.info("Fetching all OpenML tasks (bulk)...")
    for attempt in range(retry_max):
        try:
            all_tasks = openml.tasks.list_tasks(output_format="dataframe")
            break
        except Exception as e:
            if attempt < retry_max - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"Failed to fetch task list: {e}")
                all_tasks = pd.DataFrame(columns=["tid", "did"])

    our_tasks = all_tasks[all_tasks["did"].isin(did_set)][["tid", "did"]].copy()
    logger.info(f"Found {len(our_tasks)} tasks for {our_tasks['did'].nunique()} datasets")

    # Step 2: batch-fetch runs by task ID in chunks
    task_ids = our_tasks["tid"].tolist()
    CHUNK = 100
    run_records = []  # list of {run_id, task_id, upload_time}
    for i in range(0, len(task_ids), CHUNK):
        chunk = task_ids[i:i + CHUNK]
        for attempt in range(retry_max):
            try:
                runs_df = openml.runs.list_runs(task=chunk, output_format="dataframe")
                if len(runs_df) > 0:
                    col = "upload_time" if "upload_time" in runs_df.columns else None
                    for _, row in runs_df.iterrows():
                        run_records.append({
                            "task_id": int(row.get("task_id", row.get("tid", 0))),
                            "upload_time": str(row[col]) if col else None,
                        })
                break
            except Exception as e:
                if attempt < retry_max - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.warning(f"Failed runs for task chunk {i}: {e}")
                    break
        if i % 1000 == 0:
            logger.info(f"  Fetched runs for tasks {i}/{len(task_ids)}")

    # Step 3: join runs → tasks → datasets
    runs_df2 = pd.DataFrame(run_records) if run_records else pd.DataFrame(columns=["task_id", "upload_time"])
    if len(runs_df2) > 0:
        runs_df2["upload_time"] = pd.to_datetime(runs_df2["upload_time"], errors="coerce")
        task_did = our_tasks.rename(columns={"tid": "task_id"})
        runs_merged = runs_df2.merge(task_did, on="task_id", how="left")
        agg = runs_merged.groupby("did").agg(
            first_run_timestamp=("upload_time", "min"),
            run_count=("upload_time", "count"),
        ).reset_index()
    else:
        agg = pd.DataFrame(columns=["did", "first_run_timestamp", "run_count"])

    # Fill missing datasets with 0 runs
    all_did_df = pd.DataFrame({"did": list(did_set)})
    result = all_did_df.merge(agg, on="did", how="left")
    result["run_count"] = result["run_count"].fillna(0).astype(int)
    result["first_run_timestamp"] = result["first_run_timestamp"].astype(object).where(result["run_count"] > 0, None)

    records_out = result[["did", "first_run_timestamp", "run_count"]].copy()
    records_out["first_run_timestamp"] = records_out["first_run_timestamp"].astype(str).where(records_out["run_count"] > 0, None)
    with open(bulk_cache, "w") as f:
        json.dump(records_out.to_dict(orient="records"), f, default=str)
    logger.info(f"Cached run timestamps for {len(records_out)} datasets")

    result["did"] = result["did"].astype(int)
    result["first_run_timestamp"] = pd.to_datetime(result["first_run_timestamp"], errors="coerce")
    result["run_count"] = result["run_count"].fillna(0).astype(int)
    return result[["did", "first_run_timestamp", "run_count"]]


def fetch_dataset_metadata(dataset_ids: list) -> pd.DataFrame:
    """Fetch upload_date, task_type, NumberOfInstances per dataset from OpenML REST API.
    Returns: DataFrame[did, upload_date, task_type, NumberOfInstances]
    """
    import openml
    records = []
    for did in dataset_ids:
        try:
            ds = openml.datasets.get_dataset(did, download_data=False, download_qualities=True)
            upload_date = getattr(ds, "upload_date", None)
            task_type = "supervised_classification"  # default; OpenML task type lookup is separate
            n_instances = None
            if hasattr(ds, "qualities") and ds.qualities:
                n_instances = ds.qualities.get("NumberOfInstances")
            records.append({
                "did": int(did),
                "upload_date": upload_date,
                "task_type": task_type,
                "NumberOfInstances": float(n_instances) if n_instances is not None else np.nan,
            })
        except Exception as e:
            logger.warning(f"Failed metadata for did={did}: {e}")
            records.append({"did": int(did), "upload_date": None, "task_type": None, "NumberOfInstances": np.nan})
    df = pd.DataFrame(records)
    df["did"] = df["did"].astype(int)
    df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")
    return df[["did", "upload_date", "task_type", "NumberOfInstances"]]


def fetch_all_run_records(
    dataset_ids: list,
    cache_dir: str,
    retry_max: int = 3,
) -> pd.DataFrame:
    """Fetch individual run records (did, upload_time) per dataset via OpenML API.

    Unlike fetch_run_timestamps which aggregates, this returns one row per run
    so that compute_12m_run_counts can apply the exact 12-month window filter.
    Results cached to cache_dir/run_records_all.json.

    Returns: DataFrame[did, upload_time]
    """
    import openml
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "run_records_all.json")

    if os.path.exists(cache_path):
        with open(cache_path) as f:
            records = json.load(f)
        logger.info(f"Loaded {len(records)} run records from cache: {cache_path}")
        df = pd.DataFrame(records) if records else pd.DataFrame(columns=["did", "upload_time"])
        df["did"] = df["did"].astype(int)
        df["upload_time"] = pd.to_datetime(df["upload_time"], errors="coerce")
        return df[["did", "upload_time"]]

    did_set = set(int(d) for d in dataset_ids)

    logger.info("Fetching all OpenML tasks for run records (bulk)...")
    for attempt in range(retry_max):
        try:
            all_tasks = openml.tasks.list_tasks(output_format="dataframe")
            break
        except Exception as e:
            if attempt < retry_max - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"Failed to fetch task list: {e}")
                all_tasks = pd.DataFrame(columns=["tid", "did"])

    our_tasks = all_tasks[all_tasks["did"].isin(did_set)][["tid", "did"]].copy()
    logger.info(f"Found {len(our_tasks)} tasks for {our_tasks['did'].nunique()} datasets")

    task_ids = our_tasks["tid"].tolist()
    CHUNK = 100
    run_records = []
    for i in range(0, len(task_ids), CHUNK):
        chunk = task_ids[i:i + CHUNK]
        for attempt in range(retry_max):
            try:
                runs_df = openml.runs.list_runs(task=chunk, output_format="dataframe")
                if len(runs_df) > 0:
                    time_col = "upload_time" if "upload_time" in runs_df.columns else None
                    tid_col = "task_id" if "task_id" in runs_df.columns else ("tid" if "tid" in runs_df.columns else None)
                    for _, row in runs_df.iterrows():
                        run_records.append({
                            "task_id": int(row[tid_col]) if tid_col else None,
                            "upload_time": str(row[time_col]) if time_col else None,
                        })
                break
            except Exception as e:
                if attempt < retry_max - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.warning(f"Failed runs for task chunk {i}: {e}")
                    break
        if i % 1000 == 0 and i > 0:
            logger.info(f"  Fetched runs for tasks {i}/{len(task_ids)}")

    runs_df2 = pd.DataFrame(run_records) if run_records else pd.DataFrame(columns=["task_id", "upload_time"])
    if len(runs_df2) > 0:
        runs_df2["upload_time"] = pd.to_datetime(runs_df2["upload_time"], errors="coerce")
        task_did = our_tasks.rename(columns={"tid": "task_id"})
        result = runs_df2.merge(task_did, on="task_id", how="left")
        result = result[result["did"].notna()].copy()
        result["did"] = result["did"].astype(int)
        out = result[["did", "upload_time"]].dropna(subset=["upload_time"])
    else:
        out = pd.DataFrame(columns=["did", "upload_time"])

    records_out = out.copy()
    records_out["upload_time"] = records_out["upload_time"].astype(str)
    with open(cache_path, "w") as f:
        json.dump(records_out.to_dict(orient="records"), f, default=str)
    logger.info(f"Cached {len(out)} individual run records to {cache_path}")

    out["did"] = out["did"].astype(int)
    out["upload_time"] = pd.to_datetime(out["upload_time"], errors="coerce")
    return out[["did", "upload_time"]]


def build_merged_cohort(
    he1_scores: pd.DataFrame,
    run_data: pd.DataFrame,
    metadata: pd.DataFrame,
    min_run_count: int,
) -> pd.DataFrame:
    """Merge H-E1 scores + run timestamps + metadata; apply min_run_count filter.
    Returns merged DataFrame.
    """
    n0 = len(he1_scores)
    merged = he1_scores.merge(metadata, on="did", how="inner")
    logger.info(f"After metadata merge: {len(merged)} (was {n0})")
    merged = merged.merge(run_data, on="did", how="left")
    merged["run_count"] = merged["run_count"].fillna(0).astype(int)
    merged = merged[merged["run_count"] >= min_run_count].copy()
    logger.info(f"After run_count>={min_run_count} filter: {len(merged)}")
    return merged
