# Analysis dataset building module for h-m1
import os
import numpy as np
import pandas as pd
from config import PATHS
from entropy import compute_preprocessing_entropy, compute_hyperparameter_entropy


def compute_reproducibility_iqr(runs_df: pd.DataFrame) -> pd.DataFrame:
    """Compute IQR of predictive_accuracy per (dataset, flow, setup) group."""
    def iqr(x):
        return x.quantile(0.75) - x.quantile(0.25)

    result = runs_df.groupby(["data_id", "flow_id", "setup_id"])["predictive_accuracy"].agg([
        ("iqr", iqr),
        ("mean", "mean"),
        ("std", "std"),
        ("count", "count")
    ]).reset_index()
    return result


def build_analysis_dataset(
    matched_runs: pd.DataFrame,
    metadata_scores: pd.DataFrame,
    controls: dict,
    flow_components: dict,
    hyperparams: dict,
) -> pd.DataFrame:
    """Merge all sources. Adds: prep_entropy, hyp_entropy, metadata_quartile."""
    repro = compute_reproducibility_iqr(matched_runs)
    repro = repro.rename(columns={"data_id": "dataset_id"})
    df = repro.merge(metadata_scores, on="dataset_id", how="left")

    df["stability"] = df["dataset_id"].map(lambda x: controls.get(x, {}).get("stability", 0.0))
    df["algo_family"] = df["flow_id"].map(lambda x: controls.get(x, {}).get("algo_family", "Other"))

    run_counts = matched_runs.groupby("data_id").size().reset_index(name="run_count")
    run_counts = run_counts.rename(columns={"data_id": "dataset_id"})
    df = df.merge(run_counts, on="dataset_id", how="left")
    df["log_popularity"] = np.log1p(df["run_count"].fillna(0))

    df["prep_entropy"] = df["flow_id"].map(
        lambda x: compute_preprocessing_entropy(list(flow_components.get(x, [])))
    )
    df["hyp_entropy"] = df["setup_id"].map(
        lambda x: compute_hyperparameter_entropy(dict(hyperparams.get(x, [])))
    )

    df = df.dropna(subset=["iqr", "metadata_score", "prep_entropy"])
    # For discrete scores (0-5), assign quartiles based on score value
    # Q1: 0-1 (low), Q2: 2, Q3: 3, Q4: 4-5 (high)
    def assign_quartile(score):
        if score <= 1:
            return 1
        elif score == 2:
            return 2
        elif score == 3:
            return 3
        else:
            return 4
    df["metadata_quartile"] = df["metadata_score"].apply(assign_quartile)

    os.makedirs(os.path.dirname(PATHS["analysis"]), exist_ok=True)
    df.to_parquet(PATHS["analysis"], index=False)
    print(f"  Saved analysis dataset ({len(df)} rows) to {PATHS['analysis']}")
    return df
