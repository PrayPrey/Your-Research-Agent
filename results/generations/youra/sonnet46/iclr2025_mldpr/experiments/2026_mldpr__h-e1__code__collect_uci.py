"""collect_uci.py — UCI ML Repository collection + caching for H-E1."""
import time
import json
import requests
from pathlib import Path
from typing import Optional
import pandas as pd
from scorer import DTS_SECTIONS, _is_present

UCI_RATE_LIMIT = 2.0  # seconds between requests


def fetch_uci_rest_fallback(
    dataset_id: int,
    base_url: str = "https://archive.ics.uci.edu/api/dataset",
    timeout: int = 10,
) -> dict:
    """GET UCI REST API for dataset metadata.

    Args:
        dataset_id: UCI dataset ID.
        base_url: Base URL for UCI REST API.
        timeout: Request timeout in seconds.

    Returns:
        Metadata dict, or empty dict on failure.
    """
    try:
        url = f"{base_url}/{dataset_id}"
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        # Try alternate URL pattern
        url2 = f"https://archive.ics.uci.edu/static/public/{dataset_id}/"
        resp2 = requests.get(url2, timeout=timeout)
        if resp2.status_code == 200:
            return {"_from_static": True, "content": resp2.text[:500]}
    except (requests.RequestException, Exception):
        pass
    return {}


def load_or_fetch_uci(
    dataset_id: int,
    cache_dir: str,
    rate_limit_sec: float = UCI_RATE_LIMIT,
) -> dict:
    """Load from JSON cache if exists, else try ucimlrepo then REST fallback.

    Args:
        dataset_id: UCI dataset ID.
        cache_dir: Directory for JSON cache files.
        rate_limit_sec: Seconds to wait between requests.

    Returns:
        Raw metadata dict.
    """
    cache_path = Path(cache_dir) / f"uci_{dataset_id}.json"

    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    time.sleep(rate_limit_sec)

    raw = {}
    try:
        from ucimlrepo import fetch_ucirepo
        result = fetch_ucirepo(id=dataset_id)
        meta = result.metadata
        meta_dict = meta.__dict__ if hasattr(meta, "__dict__") else {}

        raw = {
            "dataset_id": str(dataset_id),
            "repository": "uci",
            # motivation
            "task_categories": meta_dict.get("task") or meta_dict.get("subject_area"),
            "language": None,
            "tags": [],
            "license": meta_dict.get("license"),
            # composition
            "size_categories": None,
            "num_rows": meta_dict.get("num_instances"),
            "num_columns": meta_dict.get("num_features"),
            "features": meta_dict.get("feature_types"),
            # collection
            "source_datasets": None,
            "annotations_creators": meta_dict.get("creators"),
            "original_data_url": meta_dict.get("url") or meta_dict.get("intro_paper", {}).get("url") if isinstance(meta_dict.get("intro_paper"), dict) else None,
            # preprocessing
            "preprocessing_steps": meta_dict.get("missing_values"),
            "data_augmentation": None,
            "data_splits": None,
            # uses
            "known_limitations": None,
            "out_of_scope_use": None,
            "discussion_best_use": meta_dict.get("purpose"),
            # distribution
            "citation": meta_dict.get("intro_paper"),
            "contact": meta_dict.get("creators"),
            "maintenance_plan": meta_dict.get("donated_by"),
            # meta
            "name": meta_dict.get("name", ""),
            "doi": meta_dict.get("doi"),
        }
    except Exception:
        # Try REST fallback
        raw = fetch_uci_rest_fallback(dataset_id)
        if raw:
            raw["dataset_id"] = str(dataset_id)
            raw["repository"] = "uci"
        else:
            raw = {"dataset_id": str(dataset_id), "repository": "uci", "_error": "fetch_failed"}

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, default=str)
    except IOError:
        pass

    return raw


def _metadata_to_binary_row(raw: dict) -> dict:
    """Convert raw metadata dict to binary field presence row."""
    all_fields = [f for fields in DTS_SECTIONS.values() for f in fields]

    row = {
        "dataset_id": raw.get("dataset_id", ""),
        "repository": "uci",
        "task_category": raw.get("task_categories", "tabular"),
        "upload_year": 2015,  # Default; UCI datasets are typically older
        "in_human_subsample": False,
    }

    for field in all_fields:
        row[field] = int(_is_present(raw.get(field)))

    return row


def _get_uci_dataset_ids() -> list[int]:
    """Get list of UCI dataset IDs via REST API."""
    try:
        resp = requests.get(
            "https://archive.ics.uci.edu/api/datasets",
            params={"skip": 0, "take": 500},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and "data" in data:
                return [item["id"] for item in data["data"] if "id" in item]
            elif isinstance(data, list):
                return [item["id"] for item in data if "id" in item]
    except Exception:
        pass

    # Fallback: use known IDs (first 100)
    return list(range(1, 101))


def collect_uci_datasets(
    cache_dir: str = "data/raw_cache",
    pilot: bool = False,
) -> pd.DataFrame:
    """Fetch UCI datasets (full population ~100); rate-limited.

    Args:
        cache_dir: Directory for JSON cache files.
        pilot: If True, collect 50 datasets for pilot check.

    Returns:
        DataFrame with DTS binary field columns.
    """
    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    print(f"  [UCI] Fetching dataset ID list...")
    dataset_ids = _get_uci_dataset_ids()

    if pilot:
        dataset_ids = dataset_ids[:50]

    print(f"  [UCI] Collecting {len(dataset_ids)} datasets...")

    rows = []
    for dataset_id in dataset_ids:
        raw = load_or_fetch_uci(dataset_id, cache_dir)
        if not raw.get("_error"):
            binary_row = _metadata_to_binary_row(raw)
            rows.append(binary_row)

    df = pd.DataFrame(rows)
    print(f"  [UCI] Collected {len(df)} datasets")
    return df
