"""H-E1 Data Loading & Gini Aggregation"""
import pandas as pd
import numpy as np
from datasets import load_dataset
from config import DATA


def load_pwc_evaluation_tables():
    """Load pwc-archive/evaluation-tables from HuggingFace."""
    ds = load_dataset(DATA.dataset_name, split="train")
    return ds


def parse_triplets(ds) -> pd.DataFrame:
    """Flatten nested PWC eval-table rows to task/dataset/paper_date columns.

    Structure: task -> datasets[] -> sota.rows[] -> paper_date
    """
    records = []
    for row in ds:
        task = row.get("task", "")
        datasets_list = row.get("datasets", [])

        for dataset_entry in datasets_list:
            dataset_name = dataset_entry.get("dataset", "")
            sota = dataset_entry.get("sota", {})
            metrics = sota.get("metrics", [])
            sota_rows = sota.get("rows", [])

            for sota_row in sota_rows:
                paper_date = sota_row.get("paper_date", "")
                paper_title = sota_row.get("paper_title", "")

                if dataset_name and paper_date:
                    records.append({
                        "task": task,
                        "dataset": dataset_name,
                        "metric": metrics[0] if metrics else "",
                        "paper_title": paper_title,
                        "date": paper_date
                    })

    df = pd.DataFrame(records)
    if not df.empty and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
    return df


def filter_date_range(df: pd.DataFrame, start: str = None, end: str = None) -> pd.DataFrame:
    """Filter DataFrame to date range."""
    start = start or DATA.date_start
    end = end or DATA.date_end

    if df.empty or "date" not in df.columns:
        return df

    mask = (df["date"] >= start) & (df["date"] <= end)
    return df[mask].copy()


def monthly_benchmark_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot to monthly usage counts per dataset."""
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["month"] = df["date"].dt.to_period("M")

    counts = df.groupby(["month", "dataset"]).size().unstack(fill_value=0)
    counts.index = counts.index.to_timestamp()
    return counts


def gini(array: np.ndarray) -> float:
    """Gini coefficient of a 1D non-negative array."""
    array = np.asarray(array).flatten()
    array = array[array > 0]  # exclude zeros

    if len(array) == 0:
        return 0.0

    array = np.sort(array)
    n = len(array)
    cumx = np.cumsum(array)
    return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n


def compute_monthly_gini_series(counts: pd.DataFrame) -> pd.Series:
    """Apply gini() row-wise across monthly counts."""
    if counts.empty:
        return pd.Series(dtype=float)

    gini_values = counts.apply(lambda row: gini(row.values), axis=1)
    gini_values.name = "gini"
    return gini_values


def load_and_process_data():
    """Full pipeline: load -> parse -> filter -> aggregate -> gini series."""
    print("Loading PWC evaluation tables...")
    ds = load_pwc_evaluation_tables()
    print(f"  Loaded {len(ds)} rows")

    print("Parsing triplets...")
    df = parse_triplets(ds)
    print(f"  Parsed {len(df)} records")

    print(f"Filtering to {DATA.date_start} - {DATA.date_end}...")
    df = filter_date_range(df)
    print(f"  {len(df)} records in range")

    print("Computing monthly benchmark counts...")
    counts = monthly_benchmark_counts(df)
    print(f"  {len(counts)} months, {len(counts.columns)} unique datasets")

    print("Computing monthly Gini series...")
    gini_series = compute_monthly_gini_series(counts)
    print(f"  {len(gini_series)} Gini values")

    return gini_series, counts, df


if __name__ == "__main__":
    gini_series, counts, df = load_and_process_data()
    print(f"\nGini series range: [{gini_series.min():.4f}, {gini_series.max():.4f}]")
    print(f"Gini series head:\n{gini_series.head()}")
