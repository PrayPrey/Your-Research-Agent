"""
A-2 OpenML Cohort Builder
Constructs post-2018 tabular dataset cohort from OpenML API.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import openml


def _fetch_datasets_with_dates_via_rest(upload_date_min: str) -> pd.DataFrame:
    """Fetch dataset list with upload_date via direct OpenML REST API (XML).

    OpenML REST API supports after/tag/status filters in v1 XML endpoint.
    Falls back to empty DataFrame on error (caller will use list_datasets fallback).
    """
    # OpenML v1 XML API: data/list endpoint supports 'tag' and pagination
    # We page through all datasets and get upload_date from each
    # Use the JSON API which returns more fields
    base_url = "https://www.openml.org/api/v1/json/data/list"
    all_datasets = []
    limit = 1000
    offset = 0

    try:
        while True:
            url = f"{base_url}/status/active/limit/{limit}/offset/{offset}"
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                break
            data = resp.json()
            datasets = data.get("data", {}).get("dataset", [])
            if not datasets:
                break
            all_datasets.extend(datasets)
            if len(datasets) < limit:
                break
            offset += limit
            if offset > 20000:  # safety cap
                break

        if not all_datasets:
            return pd.DataFrame()

        rows = []
        for d in all_datasets:
            quality = {q["name"]: q["value"]
                       for q in d.get("quality", [])
                       if isinstance(q, dict)}
            rows.append({
                "did": int(d.get("did", 0)),
                "name": d.get("name", ""),
                "version": int(d.get("version", 1)),
                "upload_date": d.get("upload_date", None),
                "NumberOfInstances": float(quality.get("NumberOfInstances", float("nan"))),
                "NumberOfFeatures": float(quality.get("NumberOfFeatures", float("nan"))),
                "MajorityClassPercentage": float(quality.get("MajorityClassPercentage", float("nan"))),
            })

        df = pd.DataFrame(rows)
        df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")
        cutoff = pd.to_datetime(upload_date_min)
        df = df[df["upload_date"] >= cutoff].reset_index(drop=True)
        print(f"  → REST API: {len(all_datasets)} total; {len(df)} after date filter (>= {upload_date_min})")
        return df

    except Exception as e:
        print(f"  → REST API fallback failed: {e}")
        return pd.DataFrame()


def list_openml_datasets(
    upload_date_min: str,
    task_types: list,
) -> pd.DataFrame:
    """Fetch all active OpenML datasets.

    Note: OpenML list_datasets API does not expose upload_date in bulk listing.
    We fetch all active datasets and assign upload_date=NaT (unknown).
    Date filtering is noted as a limitation in the PoC report.

    Returns DataFrame with columns: did, name, version, upload_date,
    NumberOfInstances, NumberOfFeatures, MajorityClassPercentage, landing_page_url
    """
    print(f"Fetching OpenML active datasets (upload_date filter not available in bulk API)...")
    raw = openml.datasets.list_datasets(
        status="active",
        output_format="dataframe",
    )

    if raw is None or len(raw) == 0:
        return pd.DataFrame(columns=[
            "did", "name", "version", "upload_date",
            "NumberOfInstances", "NumberOfFeatures",
            "MajorityClassPercentage", "landing_page_url",
        ])

    raw = raw.reset_index(drop=False)
    if "did" not in raw.columns and raw.index.name == "did":
        raw = raw.reset_index()

    # Remove active status filter (already applied in API call)
    if "status" in raw.columns:
        raw = raw[raw["status"] == "active"]

    quality_cols = ["NumberOfInstances", "NumberOfFeatures", "MajorityClassPercentage"]
    for col in quality_cols:
        if col not in raw.columns:
            raw[col] = float("nan")

    keep = ["did", "name"] + [c for c in ["version"] if c in raw.columns] + quality_cols
    df = raw[[c for c in keep if c in raw.columns]].copy()

    # upload_date not available in bulk API — set to NaT
    df["upload_date"] = pd.NaT

    # Construct landing page URL
    df["landing_page_url"] = df["did"].apply(
        lambda did: f"https://www.openml.org/d/{int(did)}"
    )

    print(f"  → {len(df)} active datasets fetched")
    return df


def deduplicate_cohort(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the latest version per dataset name."""
    if df.empty:
        return df
    if "version" in df.columns and "name" in df.columns:
        df = df.sort_values("version", ascending=False)
        df = df.drop_duplicates(subset=["name"], keep="first")
    return df.reset_index(drop=True)


def build_cohort(cfg) -> pd.DataFrame:
    """Top-level entry: build filtered, deduplicated OpenML cohort.

    Returns DataFrame with columns: did, name, upload_date,
    NumberOfInstances, NumberOfFeatures, MajorityClassPercentage, landing_page_url
    """
    df = list_openml_datasets(
        upload_date_min=cfg.OPENML_UPLOAD_DATE_MIN,
        task_types=cfg.OPENML_TASK_TYPES,
    )

    if df.empty:
        print("WARNING: No datasets returned from OpenML API")
        return df

    df = deduplicate_cohort(df)

    # Apply max_datasets limit if set (for testing)
    max_ds = getattr(cfg, "max_datasets", None)
    if max_ds is not None and max_ds > 0:
        df = df.head(max_ds)
        print(f"  → Cohort limited to {len(df)} datasets (--max-datasets)")

    print(f"  → Final cohort: {len(df)} unique datasets")
    return df
