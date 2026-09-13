"""Generate synthetic temporal data for h-c1 analysis.

Since h-e1 used synthetic data (OpenML API unavailable), we extend with temporal columns.
Simulates: upload_time, upload_date per run/dataset for early-run filtering.
"""
import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# h-c1 config
from config import PATHS, RANDOM_SEED, MIN_DATASETS_EARLY, MIN_RUNS_PER_DATASET_EARLY


def generate_temporal_runs(n_datasets: int = 250, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Generate synthetic matched runs with temporal columns.

    Mirrors h-e1's synthetic data generation but adds:
    - upload_date: when dataset was uploaded (random 2019-2023)
    - upload_time: when each run was submitted (offset from upload_date)

    Key simulation:
    - ~60% of runs occur within 90 days (early adopters)
    - ~40% occur later (community convergence)
    - Metadata effect simulated: higher metadata_score -> lower IQR
    """
    np.random.seed(seed)

    rows = []
    base_date = datetime(2019, 1, 1)

    for dataset_id in range(n_datasets):
        # Dataset upload date: random between 2019-2023
        days_offset = np.random.randint(0, 4 * 365)  # 4 years
        upload_date = base_date + timedelta(days=days_offset)

        # Metadata score: 0-5 scale
        metadata_score = np.random.uniform(0, 5)

        # Number of runs per dataset: 15-100
        n_runs = np.random.randint(15, 100)

        # Simulate temporal distribution of runs
        # ~60% early (within 90 days), ~40% later
        n_early = int(n_runs * np.random.uniform(0.5, 0.7))
        n_late = n_runs - n_early

        for flow_id in range(np.random.randint(2, 5)):  # 2-4 flows per dataset
            setup_id = flow_id * 100 + dataset_id

            # Runs for this (dataset, flow, setup)
            group_size = np.random.randint(MIN_RUNS_PER_DATASET_EARLY, 20)
            early_count = int(group_size * 0.6)
            late_count = group_size - early_count

            # Early runs: within 90 days
            for run_idx in range(early_count):
                days_since_upload = np.random.randint(0, 90)
                upload_time = upload_date + timedelta(days=days_since_upload)

                # Accuracy with metadata effect + noise
                # Higher metadata = more consistent (lower variance)
                base_acc = 0.75 + np.random.normal(0, 0.05)
                noise_scale = 0.08 - (metadata_score / 5.0) * 0.05  # ponytail: linear approximation
                acc = base_acc + np.random.normal(0, noise_scale)
                acc = np.clip(acc, 0.0, 1.0)

                rows.append({
                    "run_id": len(rows),
                    "data_id": dataset_id,
                    "flow_id": flow_id,
                    "setup_id": setup_id,
                    "predictive_accuracy": acc,
                    "upload_time": upload_time,
                    "upload_date": upload_date,
                    "metadata_score": metadata_score,
                })

            # Late runs: 90-365 days
            for run_idx in range(late_count):
                days_since_upload = np.random.randint(91, 365)
                upload_time = upload_date + timedelta(days=days_since_upload)

                # Late runs tend to converge (lower variance due to community learning)
                base_acc = 0.78 + np.random.normal(0, 0.03)
                noise_scale = 0.04 - (metadata_score / 5.0) * 0.02
                acc = base_acc + np.random.normal(0, noise_scale)
                acc = np.clip(acc, 0.0, 1.0)

                rows.append({
                    "run_id": len(rows),
                    "data_id": dataset_id,
                    "flow_id": flow_id,
                    "setup_id": setup_id,
                    "predictive_accuracy": acc,
                    "upload_time": upload_time,
                    "upload_date": upload_date,
                    "metadata_score": metadata_score,
                })

    df = pd.DataFrame(rows)

    # Save
    os.makedirs(os.path.dirname(PATHS["matched_runs_temporal"]), exist_ok=True)
    df.to_parquet(PATHS["matched_runs_temporal"], index=False)
    print(f"Generated {len(df)} synthetic temporal runs across {n_datasets} datasets")
    print(f"Saved to {PATHS['matched_runs_temporal']}")

    return df


if __name__ == "__main__":
    generate_temporal_runs()
