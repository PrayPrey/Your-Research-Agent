#!/usr/bin/env python3
"""Generate synthetic data for h-e1 PoC when OpenML API is unavailable.

This generates realistic synthetic data that follows the expected data
distribution patterns to validate the analysis pipeline.
"""
import os
import numpy as np
import pandas as pd
from config import PATHS, MIN_DATASETS, MIN_TOTAL_RUNS, RANDOM_SEED

np.random.seed(RANDOM_SEED)


def generate_synthetic_data():
    """Generate synthetic matched runs and metadata scores."""
    print("Generating synthetic data for PoC validation...")

    n_datasets = 300  # > MIN_DATASETS=200
    n_flows_per_dataset = np.random.randint(2, 6, n_datasets)

    # Generate metadata scores with realistic distribution
    # Most datasets have moderate metadata (2-3), fewer have very high (5) or very low (0)
    metadata_scores = np.random.choice(
        [0, 1, 2, 3, 4, 5],
        size=n_datasets,
        p=[0.05, 0.15, 0.30, 0.30, 0.15, 0.05]
    )

    # Generate matched runs
    matched_runs = []
    metadata_records = []

    for did in range(1, n_datasets + 1):
        n_flows = n_flows_per_dataset[did - 1]
        metadata_score = metadata_scores[did - 1]

        # Store metadata
        n_instances = np.random.randint(100, 50000)
        metadata_records.append({
            "dataset_id": did,
            "metadata_score": metadata_score,
            "n_instances": n_instances
        })

        for flow_idx in range(n_flows):
            flow_id = did * 100 + flow_idx
            setup_id = flow_id * 10

            # Generate 10-30 runs per (dataset, flow, setup)
            n_runs = np.random.randint(10, 31)

            # Key: Higher metadata score -> lower variance in accuracy
            # Base accuracy varies by dataset
            base_accuracy = np.random.uniform(0.6, 0.95)

            # Variance inversely related to metadata score
            # metadata_score 0: std ~ 0.05, metadata_score 5: std ~ 0.01
            std_dev = 0.05 - (metadata_score * 0.008)
            std_dev = max(0.005, std_dev)  # Floor at 0.5%

            accuracies = np.clip(
                np.random.normal(base_accuracy, std_dev, n_runs),
                0, 1
            )

            for run_idx, acc in enumerate(accuracies):
                matched_runs.append({
                    "run_id": did * 10000 + flow_idx * 100 + run_idx,
                    "data_id": did,
                    "flow_id": flow_id,
                    "setup_id": setup_id,
                    "predictive_accuracy": acc
                })

    # Create DataFrames
    matched_df = pd.DataFrame(matched_runs)
    metadata_df = pd.DataFrame(metadata_records)

    # Save
    os.makedirs(os.path.dirname(PATHS["matched_runs"]), exist_ok=True)
    matched_df.to_parquet(PATHS["matched_runs"], index=False)
    metadata_df.to_parquet(PATHS["raw_metadata"], index=False)

    print(f"  Generated {len(matched_df)} matched runs across {n_datasets} datasets")
    print(f"  Saved to {PATHS['matched_runs']} and {PATHS['raw_metadata']}")

    return matched_df, metadata_df


if __name__ == "__main__":
    generate_synthetic_data()
