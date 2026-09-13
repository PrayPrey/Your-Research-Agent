# Data collection module for h-e1
import os
import openml
import pandas as pd
import numpy as np
from config import MIN_DATE, MAX_DATE, MIN_RUNS_PER_GROUP, PATHS


def collect_datasets(min_date: str = MIN_DATE) -> pd.DataFrame:
    """Query OpenML for classification datasets uploaded >= min_date."""
    print(f"Fetching OpenML datasets (min_date={min_date})...")
    datasets = openml.datasets.list_datasets(output_format="dataframe")
    datasets["upload_date"] = pd.to_datetime(datasets["upload_date"], errors="coerce")

    filtered = datasets[
        (datasets["upload_date"] >= min_date) &
        (datasets["upload_date"] <= MAX_DATE)
    ].copy()

    print(f"  Found {len(filtered)} datasets in date range")
    return filtered[["did", "name", "upload_date", "NumberOfInstances", "NumberOfClasses"]]


def get_matched_runs(dataset_id: int, min_runs: int = MIN_RUNS_PER_GROUP) -> pd.DataFrame:
    """Fetch runs for dataset, group by (flow_id, setup_id), keep groups with count >= min_runs."""
    try:
        evals = openml.evaluations.list_evaluations(
            function="predictive_accuracy",
            data=[dataset_id],
            output_format="dataframe"
        )
        if evals.empty:
            return pd.DataFrame()

        grouped = evals.groupby(["flow_id", "setup_id"])
        matched = grouped.filter(lambda x: len(x) >= min_runs)
        return matched[["run_id", "data_id", "flow_id", "setup_id", "value"]].rename(
            columns={"value": "predictive_accuracy"}
        )
    except Exception as e:
        print(f"  Warning: Error fetching runs for dataset {dataset_id}: {e}")
        return pd.DataFrame()


def collect_all_matched_runs(dataset_ids: list) -> pd.DataFrame:
    """Loop get_matched_runs over dataset_ids, concat, write PATHS['matched_runs']."""
    all_runs = []
    total = len(dataset_ids)

    for i, did in enumerate(dataset_ids):
        if (i + 1) % 50 == 0:
            print(f"  Processing dataset {i+1}/{total}...")
        runs = get_matched_runs(did)
        if not runs.empty:
            all_runs.append(runs)

    if not all_runs:
        print("Warning: No matched runs found")
        return pd.DataFrame()

    df = pd.concat(all_runs, ignore_index=True)
    os.makedirs(os.path.dirname(PATHS["matched_runs"]), exist_ok=True)
    df.to_parquet(PATHS["matched_runs"], index=False)
    print(f"  Saved {len(df)} matched runs to {PATHS['matched_runs']}")
    return df


def extract_controls(dataset_id: int, flow_id: int) -> dict:
    """Return control variables for (dataset, flow) pair."""
    controls = {
        "stability": 0.0,
        "algo_family": "unknown",
        "sklearn_version": "unknown"
    }

    try:
        dataset = openml.datasets.get_dataset(dataset_id, download_data=False)
        X, _, _, _ = dataset.get_data(dataset_format="dataframe")
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            cvs = X[numeric_cols].std() / (X[numeric_cols].mean().abs() + 1e-10)
            controls["stability"] = float(cvs.median())
    except Exception:
        pass

    try:
        flow = openml.flows.get_flow(flow_id)
        name = flow.name.lower()
        if "randomforest" in name or "random_forest" in name:
            controls["algo_family"] = "RandomForest"
        elif "gradient" in name or "gbm" in name or "xgb" in name:
            controls["algo_family"] = "GBM"
        elif "svm" in name or "svc" in name:
            controls["algo_family"] = "SVM"
        elif "neural" in name or "mlp" in name:
            controls["algo_family"] = "NeuralNetwork"
        elif "logistic" in name:
            controls["algo_family"] = "Logistic"
        elif "tree" in name:
            controls["algo_family"] = "DecisionTree"
        else:
            controls["algo_family"] = "Other"

        deps = flow.dependencies or ""
        if "sklearn" in deps:
            import re
            match = re.search(r"sklearn[=<>]+(\d+\.\d+)", deps)
            if match:
                controls["sklearn_version"] = match.group(1)
    except Exception:
        pass

    return controls
