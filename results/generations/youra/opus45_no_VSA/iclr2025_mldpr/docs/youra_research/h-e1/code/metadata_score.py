# Metadata completeness scoring module for h-e1
import os
import openml
import pandas as pd
from config import PATHS


def compute_metadata_score(dataset) -> int:
    """Compute 5-field metadata completeness score (0-5)."""
    score = 0
    desc = (dataset.description or "").lower()

    # Feature description present (+1)
    if len(desc) > 100 and "feature" in desc:
        score += 1

    # Target description present (+1)
    if dataset.default_target_attribute:
        score += 1

    # Missing value handling documented (+1)
    if "missing" in desc or dataset.ignore_attribute:
        score += 1

    # Data collection context documented (+1)
    if any(kw in desc for kw in ["collected", "source", "origin", "study", "survey"]):
        score += 1

    # Version/changelog present (+1)
    if hasattr(dataset, "version") and dataset.version and dataset.version > 1:
        score += 1

    return score


def score_all_datasets(dataset_ids: list) -> pd.DataFrame:
    """Compute metadata scores for all datasets, write metadata.parquet."""
    records = []
    total = len(dataset_ids)

    for i, did in enumerate(dataset_ids):
        if (i + 1) % 50 == 0:
            print(f"  Scoring dataset {i+1}/{total}...")
        try:
            dataset = openml.datasets.get_dataset(did, download_data=False)
            score = compute_metadata_score(dataset)
            records.append({
                "dataset_id": did,
                "metadata_score": score,
                "n_instances": dataset.qualities.get("NumberOfInstances", 0) if dataset.qualities else 0,
            })
        except Exception as e:
            print(f"  Warning: Could not score dataset {did}: {e}")

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(PATHS["raw_metadata"]), exist_ok=True)
    df.to_parquet(PATHS["raw_metadata"], index=False)
    print(f"  Saved {len(df)} metadata scores to {PATHS['raw_metadata']}")
    return df
