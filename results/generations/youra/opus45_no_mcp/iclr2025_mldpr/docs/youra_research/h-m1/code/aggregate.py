"""Aggregation module to merge OpenML and S2 results."""
import pandas as pd


def build_dataset_records(high: list, low: list) -> pd.DataFrame:
    """Build unified DataFrame from high-use and low-use dataset groups."""
    records = []

    for d in high:
        records.append({
            "name": d["name"],
            "group": "high",
            "run_count": d["run_count"],
            "paper_count": d.get("paper_count", 0)
        })

    for d in low:
        records.append({
            "name": d["name"],
            "group": "low",
            "run_count": d["run_count"],
            "paper_count": d.get("paper_count", 0)
        })

    return pd.DataFrame(records)


def save_records(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
