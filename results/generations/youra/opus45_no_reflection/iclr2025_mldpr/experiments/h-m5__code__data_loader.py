"""H-M5 Data Loading: PWC dataset load, modality classification, monthly aggregation"""
import os
import pandas as pd
import numpy as np
from datasets import load_dataset
from config import CONFIG


def load_pwc_dataset(cache_dir: str = ".cache/pwc") -> pd.DataFrame:
    """Load pwc-archive/datasets train split."""
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, "pwc_datasets.parquet")

    if os.path.exists(cache_file):
        print(f"Loading from cache: {cache_file}")
        return pd.read_parquet(cache_file)

    print("Loading PWC dataset from HuggingFace...")
    ds = load_dataset(CONFIG.dataset_name, split=CONFIG.dataset_split)
    df = ds.to_pandas()
    df.to_parquet(cache_file)
    print(f"Cached to: {cache_file}")
    return df


def extract_modality_from_list(modalities_list) -> str:
    """Extract single modality from modalities list field."""
    if modalities_list is None or (isinstance(modalities_list, float) and np.isnan(modalities_list)):
        return CONFIG.default_modality
    if not isinstance(modalities_list, (list, np.ndarray)):
        return CONFIG.default_modality
    if len(modalities_list) == 0:
        return CONFIG.default_modality

    modality_map = {
        "Images": "CV",
        "Texts": "NLP",
        "Audio": "Audio",
        "Tabular Data": "Tabular",
        "3D": "CV",
        "Videos": "CV",
        "Medical": "CV",
        "Graphs": "Tabular",
        "Point Cloud": "CV",
        "Time Series": "Tabular",
        "Code": "NLP",
    }

    for mod in modalities_list:
        if mod in modality_map:
            return modality_map[mod]

    return CONFIG.default_modality


def extract_modality(task: str) -> str:
    """Keyword match task string -> CV|NLP|Audio|Tabular|Other (fallback)."""
    if not task or not isinstance(task, str):
        return CONFIG.default_modality
    task_lower = task.lower()
    for modality, keywords in CONFIG.modality_keywords.items():
        if any(kw in task_lower for kw in keywords):
            return modality
    return CONFIG.default_modality


def build_monthly_counts(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate benchmark usage by month x modality x benchmark using introduced_date."""
    df = raw_df.copy()

    df["introduced_date"] = pd.to_datetime(df["introduced_date"], errors="coerce")
    df = df.dropna(subset=["introduced_date"])

    start = pd.Timestamp(CONFIG.date_start)
    end = pd.Timestamp(CONFIG.date_end)
    df = df[(df["introduced_date"] >= start) & (df["introduced_date"] <= end)]

    if "modalities" in df.columns:
        df["modality"] = df["modalities"].apply(extract_modality_from_list)
    elif "tasks" in df.columns:
        def extract_task_text(tasks):
            if tasks is None or (isinstance(tasks, float) and np.isnan(tasks)):
                return ""
            if isinstance(tasks, list) and len(tasks) > 0:
                if isinstance(tasks[0], dict):
                    return tasks[0].get("task", "")
                return str(tasks[0])
            return str(tasks)
        df["task_text"] = df["tasks"].apply(extract_task_text)
        df["modality"] = df["task_text"].apply(extract_modality)
    else:
        df["modality"] = CONFIG.default_modality

    df["month"] = df["introduced_date"].dt.to_period("M")

    benchmark_col = "name" if "name" in df.columns else df.columns[0]

    num_papers_col = "num_papers" if "num_papers" in df.columns else None
    if num_papers_col:
        df["count"] = df[num_papers_col].fillna(1).astype(int)
    else:
        df["count"] = 1

    counts = df.groupby(["month", "modality", benchmark_col])["count"].sum().reset_index()
    counts.columns = ["month", "modality", "benchmark", "count"]

    print(f"Built monthly counts: {len(counts)} records")
    print(f"  Modality distribution:")
    mod_dist = counts.groupby("modality")["count"].sum()
    for mod, cnt in mod_dist.items():
        print(f"    {mod}: {cnt}")

    return counts
