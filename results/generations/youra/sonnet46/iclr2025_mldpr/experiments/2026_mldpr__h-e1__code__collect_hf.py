"""collect_hf.py — HuggingFace Hub API collection + caching for H-E1."""
import time
import json
import os
import random
from pathlib import Path
from typing import Optional
import pandas as pd
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError

SEED = 42
HF_RATE_LIMIT_SEC = 1.0    # unauthenticated (1 req/sec)
HF_RATE_LIMIT_AUTH = 0.2   # authenticated (5 req/sec)

# DTS fields extracted from HF card_data
HF_DTS_FIELDS = [
    "task_categories", "language", "tags", "license",
    "size_categories", "num_rows", "num_columns", "features",
    "source_datasets", "annotations_creators", "original_data_url",
    "preprocessing_steps", "data_augmentation", "data_splits",
    "known_limitations", "out_of_scope_use", "discussion_best_use",
    "citation", "contact", "maintenance_plan",
]

TASK_BINS = {
    "nlp": ["text", "question", "translation", "summarization", "nlp", "language-modeling",
            "token", "named", "fill", "text-classification", "text2text", "dialogue"],
    "cv": ["image", "visual", "object", "video", "depth", "segmentation"],
    "audio": ["audio", "speech", "automatic-speech"],
    "tabular": ["tabular", "structured", "regression", "classification", "time-series"],
}


def _classify_task(tags: list) -> str:
    """Classify dataset into task bin from tags."""
    if not tags:
        return "other"
    tags_lower = [str(t).lower() for t in tags]
    for bin_name, keywords in TASK_BINS.items():
        if any(any(k in tag for k in keywords) for tag in tags_lower):
            return bin_name
    return "other"


def _get_upload_year(dataset_info) -> int:
    """Extract upload year from DatasetInfo."""
    try:
        if hasattr(dataset_info, "created_at") and dataset_info.created_at:
            return dataset_info.created_at.year
        if hasattr(dataset_info, "lastModified") and dataset_info.lastModified:
            return dataset_info.lastModified.year
    except Exception:
        pass
    return 2020  # default pre-2021


def stratified_sample_hf(
    dataset_list: list,
    n: int,
    seed: int = SEED,
) -> list:
    """Stratify dataset_list by (task_category_bin x upload_year_bin).

    Args:
        dataset_list: List of DatasetInfo objects.
        n: Target sample size.
        seed: Random seed.

    Returns:
        List of DatasetInfo objects (length <= n).
    """
    rng = random.Random(seed)

    bins: dict[tuple, list] = {}
    for ds in dataset_list:
        tags = list(ds.tags or []) if hasattr(ds, "tags") else []
        task_bin = _classify_task(tags)
        year = _get_upload_year(ds)
        year_bin = "pre2021" if year < 2021 else "post2021"
        key = (task_bin, year_bin)
        bins.setdefault(key, []).append(ds)

    total = sum(len(v) for v in bins.values())
    if total == 0:
        return []

    # Proportional quota
    quotas: dict[tuple, int] = {}
    for key, items in bins.items():
        quotas[key] = int(n * len(items) / total)

    # Distribute remainder
    assigned = sum(quotas.values())
    remainder = n - assigned
    if remainder > 0:
        sorted_bins = sorted(bins.keys(), key=lambda k: len(bins[k]), reverse=True)
        for i in range(remainder):
            quotas[sorted_bins[i % len(sorted_bins)]] += 1

    result = []
    for key, items in bins.items():
        quota = quotas.get(key, 0)
        sampled = rng.sample(items, min(quota, len(items)))
        result.extend(sampled)

    return result[:n]


def load_or_fetch_hf(
    dataset_id: str,
    cache_dir: str,
    api: HfApi,
    rate_limit_sec: float = HF_RATE_LIMIT_SEC,
    max_retries: int = 3,
) -> dict:
    """Load from JSON cache if exists, else fetch from HF API with retry/backoff.

    Args:
        dataset_id: HuggingFace dataset ID (e.g., "glue").
        cache_dir: Directory for JSON cache files.
        api: HfApi instance.
        rate_limit_sec: Seconds to wait between requests.
        max_retries: Max retry attempts on 429.

    Returns:
        Raw metadata dict (serialized DatasetInfo fields).
    """
    cache_path = Path(cache_dir) / f"hf_{dataset_id.replace('/', '__')}.json"

    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass  # Re-fetch if cache is corrupt

    raw = {}
    for attempt in range(max_retries):
        try:
            info = api.dataset_info(dataset_id, timeout=30)
            # Serialize card_data fields
            card = info.card_data or {}
            if hasattr(card, "__dict__"):
                card = card.__dict__
            elif hasattr(card, "to_dict"):
                card = card.to_dict()

            raw = {
                "dataset_id": dataset_id,
                "repository": "huggingface",
                "task_categories": card.get("task_categories") or getattr(info, "task_categories", None),
                "language": card.get("language") or getattr(info, "language", None),
                "tags": list(info.tags or []) if hasattr(info, "tags") else [],
                "license": card.get("license") or getattr(info, "license", None),
                "size_categories": card.get("size_categories"),
                "num_rows": None,  # Not directly available from dataset_info
                "num_columns": None,
                "features": card.get("features"),
                "source_datasets": card.get("source_datasets"),
                "annotations_creators": card.get("annotations_creators"),
                "original_data_url": card.get("original_data_url"),
                "preprocessing_steps": card.get("preprocessing_steps"),
                "data_augmentation": card.get("data_augmentation"),
                "data_splits": card.get("train-eval-index") or card.get("data_splits"),
                "known_limitations": card.get("known_limitations"),
                "out_of_scope_use": card.get("out_of_scope_use"),
                "discussion_best_use": card.get("discussion_best_use"),
                "citation": card.get("citation") or getattr(info, "citation", None),
                "contact": card.get("contact"),
                "maintenance_plan": card.get("maintenance_plan"),
                "created_at": str(getattr(info, "created_at", "")),
                "upload_year": _get_upload_year(info),
            }
            break
        except HfHubHTTPError as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                wait = (2 ** attempt) * rate_limit_sec
                time.sleep(wait)
                continue
            else:
                raw = {"dataset_id": dataset_id, "repository": "huggingface", "_error": str(e)}
                break
        except Exception as e:
            raw = {"dataset_id": dataset_id, "repository": "huggingface", "_error": str(e)}
            break
    else:
        raw = {"dataset_id": dataset_id, "repository": "huggingface", "_error": "max_retries_exceeded"}

    # Cache the result
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, default=str)
    except IOError:
        pass

    return raw


def _metadata_to_binary_row(raw: dict) -> dict:
    """Convert raw metadata dict to binary field presence row."""
    from scorer import DTS_SECTIONS, _is_present

    row = {
        "dataset_id": raw.get("dataset_id", ""),
        "repository": raw.get("repository", "huggingface"),
        "task_category": raw.get("task_categories", None),
        "upload_year": raw.get("upload_year", 2020),
        "in_human_subsample": False,
    }

    all_fields = [f for fields in DTS_SECTIONS.values() for f in fields]
    for field in all_fields:
        row[field] = int(_is_present(raw.get(field)))

    return row


def collect_hf_datasets(
    n_samples: int = 500,
    cache_dir: str = "data/raw_cache",
    hf_token: Optional[str] = None,
    pilot: bool = False,
) -> pd.DataFrame:
    """Collect HF Hub metadata; stratified sample n_samples datasets.

    Args:
        n_samples: Target number of datasets.
        cache_dir: Directory for JSON cache files.
        hf_token: Optional HF API token for higher rate limits.
        pilot: If True, collect n_pilot_per_repo=50 datasets for pilot check.

    Returns:
        DataFrame with columns: dataset_id, repository, task_category, upload_year,
        [DTS binary field columns], in_human_subsample.
    """
    if pilot:
        n_samples = 50

    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    api = HfApi(token=hf_token)
    rate_limit = HF_RATE_LIMIT_AUTH if hf_token else HF_RATE_LIMIT_SEC

    print(f"  [HF] Listing datasets (this may take a moment)...")
    try:
        dataset_list = list(api.list_datasets(limit=5000))
    except Exception as e:
        print(f"  [HF] Warning: list_datasets failed ({e}), using smaller sample")
        dataset_list = list(api.list_datasets(limit=1000))

    print(f"  [HF] Total available: {len(dataset_list)}")

    sampled = stratified_sample_hf(dataset_list, n_samples, seed=SEED)
    print(f"  [HF] Sampled {len(sampled)} datasets (target: {n_samples})")

    rows = []
    for ds in sampled:
        dataset_id = ds.id if hasattr(ds, "id") else str(ds)
        raw = load_or_fetch_hf(dataset_id, cache_dir, api, rate_limit_sec=rate_limit)
        if not raw.get("_error"):
            row = _metadata_to_binary_row(raw)
            rows.append(row)
        time.sleep(rate_limit)

    df = pd.DataFrame(rows)
    print(f"  [HF] Collected {len(df)} datasets")
    return df
