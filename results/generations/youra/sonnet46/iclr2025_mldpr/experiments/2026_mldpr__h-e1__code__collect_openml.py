"""collect_openml.py — OpenML API collection + caching for H-E1."""
import json
import random
from pathlib import Path
import pandas as pd
import openml
from scorer import DTS_SECTIONS, _is_present


def load_or_fetch_openml(
    dataset_id: int,
    cache_dir: str,
) -> dict:
    """Load from JSON cache if exists, else fetch via openml.datasets.get_dataset().

    Args:
        dataset_id: OpenML dataset ID.
        cache_dir: Directory for JSON cache files.

    Returns:
        Raw metadata dict.
    """
    cache_path = Path(cache_dir) / f"openml_{dataset_id}.json"

    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    raw = {}
    try:
        ds = openml.datasets.get_dataset(dataset_id, download_data=False)
        desc = ds.description or ""
        raw = {
            "dataset_id": str(dataset_id),
            "repository": "openml",
            # motivation
            "task_categories": getattr(ds, "tag", None) or None,
            "language": None,  # OpenML doesn't have language field
            "tags": list(ds.tag) if hasattr(ds, "tag") and ds.tag else [],
            "license": getattr(ds, "licence", None),
            # composition
            "size_categories": None,
            "num_rows": getattr(ds, "qualities", {}).get("NumberOfInstances") if hasattr(ds, "qualities") else None,
            "num_columns": getattr(ds, "qualities", {}).get("NumberOfFeatures") if hasattr(ds, "qualities") else None,
            "features": list(ds.features.values()) if hasattr(ds, "features") and ds.features else None,
            # collection
            "source_datasets": None,
            "annotations_creators": None,
            "original_data_url": getattr(ds, "url", None),
            # preprocessing
            "preprocessing_steps": "preprocessing" in desc.lower() if desc else None,
            "data_augmentation": None,
            "data_splits": None,
            # uses
            "known_limitations": None,
            "out_of_scope_use": None,
            "discussion_best_use": None,
            # distribution
            "citation": getattr(ds, "citation", None),
            "contact": getattr(ds, "creator", None),
            "maintenance_plan": None,
            # meta
            "task_type": getattr(ds, "default_target_attribute", ""),
            "name": getattr(ds, "name", ""),
        }
    except Exception as e:
        raw = {"dataset_id": str(dataset_id), "repository": "openml", "_error": str(e)}

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, default=str)
    except IOError:
        pass

    return raw


def stratified_sample_openml(
    df: pd.DataFrame,
    n: int,
    seed: int = 42,
) -> pd.DataFrame:
    """Stratify by task_type column.

    Args:
        df: DataFrame with 'task_type' column.
        n: Target sample size.
        seed: Random seed.

    Returns:
        Sampled DataFrame of length <= n.
    """
    if "task_type" not in df.columns or len(df) == 0:
        return df.sample(min(n, len(df)), random_state=seed)

    result_frames = []
    groups = df.groupby("task_type", observed=True)
    total = len(df)

    for task_type, group in groups:
        quota = max(1, int(n * len(group) / total))
        sampled = group.sample(min(quota, len(group)), random_state=seed)
        result_frames.append(sampled)

    if not result_frames:
        return df.sample(min(n, len(df)), random_state=seed)

    result = pd.concat(result_frames, ignore_index=True)

    # Trim or fill to reach n
    if len(result) > n:
        result = result.sample(n, random_state=seed)
    elif len(result) < n:
        remainder = n - len(result)
        remaining = df[~df.index.isin(result.index)]
        if len(remaining) > 0:
            extra = remaining.sample(min(remainder, len(remaining)), random_state=seed)
            result = pd.concat([result, extra], ignore_index=True)

    return result.reset_index(drop=True)


def _metadata_to_binary_row(raw: dict) -> dict:
    """Convert raw metadata dict to binary field presence row."""
    all_fields = [f for fields in DTS_SECTIONS.values() for f in fields]

    row = {
        "dataset_id": raw.get("dataset_id", ""),
        "repository": "openml",
        "task_category": raw.get("task_type", "tabular"),
        "upload_year": 2020,
        "in_human_subsample": False,
    }

    for field in all_fields:
        row[field] = int(_is_present(raw.get(field)))

    return row


def collect_openml_datasets(
    n_samples: int = 200,
    cache_dir: str = "data/raw_cache",
    pilot: bool = False,
) -> pd.DataFrame:
    """Bulk-list OpenML datasets; stratified sample by task_type.

    Args:
        n_samples: Target number of datasets.
        cache_dir: Directory for JSON cache files.
        pilot: If True, collect 50 datasets for pilot check.

    Returns:
        DataFrame with DTS binary field columns.
    """
    if pilot:
        n_samples = 50

    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    print(f"  [OpenML] Listing all datasets...")
    try:
        all_datasets = openml.datasets.list_datasets(output_format="dataframe")
    except Exception as e:
        print(f"  [OpenML] Warning: listing failed ({e}), using smaller subset")
        try:
            all_datasets = openml.datasets.list_datasets(output_format="dataframe", size=1000)
        except Exception:
            return pd.DataFrame()

    print(f"  [OpenML] Total available: {len(all_datasets)}")

    # Stratified sample by task_type (use default_target_attribute as proxy)
    if "did" not in all_datasets.columns:
        print("  [OpenML] Warning: 'did' column missing")
        return pd.DataFrame()

    # Add task_type column for stratification
    if "format" in all_datasets.columns:
        all_datasets["task_type"] = all_datasets["format"].fillna("tabular")
    else:
        all_datasets["task_type"] = "tabular"

    sampled_df = stratified_sample_openml(all_datasets, n_samples, seed=42)
    print(f"  [OpenML] Sampled {len(sampled_df)} datasets (target: {n_samples})")

    rows = []
    for _, row in sampled_df.iterrows():
        dataset_id = int(row["did"])
        raw = load_or_fetch_openml(dataset_id, cache_dir)
        if not raw.get("_error"):
            binary_row = _metadata_to_binary_row(raw)
            rows.append(binary_row)

    df = pd.DataFrame(rows)
    print(f"  [OpenML] Collected {len(df)} datasets")
    return df
