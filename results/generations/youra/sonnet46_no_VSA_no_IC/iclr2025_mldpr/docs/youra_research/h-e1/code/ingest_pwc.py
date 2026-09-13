import re
import pandas as pd
import numpy as np
from datasets import load_dataset
from config import MIN_PAPERS, NORM_REGEX

# HuggingFace dataset replacing unavailable PwC REST API
PWC_HF_DATASET = "pwc-archive/evaluation-tables"


def normalize_name(s: str) -> str:
    s = str(s).lower()
    s = re.sub(NORM_REGEX, "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _extract_year(date_str: str):
    if not date_str:
        return None
    try:
        return int(str(date_str)[:4])
    except (ValueError, TypeError):
        return None


def _get_primary_metric_value(metrics: dict) -> float:
    """Get first non-null numeric metric value."""
    if not metrics:
        return float("nan")
    for v in metrics.values():
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return float("nan")


def fetch_pwc_benchmarks(min_papers: int = MIN_PAPERS) -> pd.DataFrame:
    """
    Load PwC evaluation tables from HuggingFace (pwc-archive/evaluation-tables).
    Returns DataFrame: name, name_norm, paper_count, year_introduced.
    Benchmarks (dataset+task combinations) with >= min_papers unique papers.
    """
    print(f"Loading PwC data from HuggingFace ({PWC_HF_DATASET})...")
    ds = load_dataset(PWC_HF_DATASET, split="train")
    print(f"  Loaded {len(ds)} task records")

    # Parse: for each task, each dataset is a benchmark
    bench_rows = []
    for record in ds:
        task_name = record.get("task", "")
        for dataset_entry in (record.get("datasets") or []):
            ds_name = dataset_entry.get("dataset", "")
            if not ds_name:
                continue
            sota = dataset_entry.get("sota") or {}
            rows = sota.get("rows") or []

            # Count unique papers
            paper_titles = set()
            years = []
            for row in rows:
                pt = row.get("paper_title", "")
                if pt:
                    paper_titles.add(pt)
                pd_str = row.get("paper_date", "")
                y = _extract_year(pd_str)
                if y:
                    years.append(y)

            paper_count = len(paper_titles)
            if paper_count < min_papers:
                continue

            year_introduced = min(years) if years else None

            # Benchmark name = "Task | Dataset" combo for uniqueness
            bench_name = f"{ds_name} [{task_name}]"
            bench_rows.append({
                "name": bench_name,
                "dataset_name": ds_name,
                "task_name": task_name,
                "paper_count": paper_count,
                "year_introduced": year_introduced,
                "num_rows": len(rows),
            })

    df = pd.DataFrame(bench_rows)
    if df.empty:
        print("WARNING: No benchmarks found")
        return df

    df["name_norm"] = df["name"].apply(normalize_name)
    # Also add dataset_name_norm for joining with OpenML/Yang (dataset name only)
    df["dataset_name_norm"] = df["dataset_name"].apply(normalize_name)
    df = df.drop_duplicates("name_norm")
    print(f"PwC benchmarks after >= {min_papers} papers filter: {len(df)}")
    return df


def fetch_pwc_results_via_evaluations(pwc_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract result rows from the cached HF dataset.
    Returns DataFrame[benchmark_name, model, metric_value, year].
    """
    print(f"Loading PwC result rows from HuggingFace ({PWC_HF_DATASET})...")
    ds = load_dataset(PWC_HF_DATASET, split="train")

    # Build lookup from dataset+task → benchmark_name
    valid_names = set(pwc_df["name"].tolist())

    all_rows = []
    for record in ds:
        task_name = record.get("task", "")
        for dataset_entry in (record.get("datasets") or []):
            ds_name = dataset_entry.get("dataset", "")
            bench_name = f"{ds_name} [{task_name}]"
            if bench_name not in valid_names:
                continue

            sota = dataset_entry.get("sota") or {}
            rows = sota.get("rows") or []
            for row in rows:
                metric_val = _get_primary_metric_value(row.get("metrics") or {})
                year = _extract_year(row.get("paper_date", ""))
                model = row.get("model_name", "")
                if not model or np.isnan(metric_val):
                    continue
                all_rows.append({
                    "benchmark_name": bench_name,
                    "model": model,
                    "metric_value": metric_val,
                    "year": year,
                })

    if not all_rows:
        print("  No result rows found")
        return pd.DataFrame(columns=["benchmark_name", "model", "metric_value", "year"])

    df = pd.DataFrame(all_rows)
    print(f"  Result rows extracted: {len(df)}")
    return df
