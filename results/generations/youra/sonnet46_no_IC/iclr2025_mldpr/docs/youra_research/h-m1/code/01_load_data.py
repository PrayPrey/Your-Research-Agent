"""H-M1: Load preprocessed data from H-E1 and H-E1 model results."""
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
PARQUET_PATH = PROJECT_ROOT / "docs/youra_research/h-e1/results/preprocessed.parquet"
MODEL_RESULTS_PATH = PROJECT_ROOT / "docs/youra_research/h-e1/results/model_results.json"
RAW_CSV_PATH = PROJECT_ROOT / "docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv"


def load_preprocessed() -> pd.DataFrame:
    if PARQUET_PATH.exists():
        df = pd.read_parquet(PARQUET_PATH)
    elif RAW_CSV_PATH.exists():
        print(f"⚠ Parquet missing, loading raw CSV: {RAW_CSV_PATH}")
        df = pd.read_csv(RAW_CSV_PATH)
        df = df[df["N_tasks"] >= 1].copy()
        import numpy as np
        df["log_n_instances"] = np.log(df["n_instances"].clip(lower=1))
        df["log_n_features"] = np.log(df["n_features"].clip(lower=1))
        df["has_tags"] = (df["tags"].notna() & (df["tags"].str.strip() != "")).astype(int)
        df["age_years"] = (pd.Timestamp("2024-01-01") - pd.to_datetime(df["upload_date"])).dt.days / 365.25
        df["age_sq"] = df["age_years"] ** 2
        df["decade"] = pd.to_datetime(df["upload_date"]).dt.year // 10 * 10
    else:
        raise FileNotFoundError(f"Neither parquet nor raw CSV found.\nParquet: {PARQUET_PATH}\nCSV: {RAW_CSV_PATH}")

    assert len(df) == 5217, f"Expected N=5217, got {len(df)}"
    assert set(df["has_tags"].unique()).issubset({0, 1}), "has_tags must be binary"
    return df


def load_h_e1_results() -> dict | None:
    if MODEL_RESULTS_PATH.exists():
        with open(MODEL_RESULTS_PATH) as f:
            return json.load(f)
    print(f"⚠ H-E1 model_results.json not found: {MODEL_RESULTS_PATH}")
    return None


def main():
    print("=== H-M1: Data Loading ===")
    df = load_preprocessed()
    print(f"✓ Loaded N={len(df)} rows from parquet")
    print(f"  has_tags=1: {df['has_tags'].sum()} ({df['has_tags'].mean():.1%})")
    print(f"  N_tasks median={df['N_tasks'].median():.0f}, mean={df['N_tasks'].mean():.1f}")
    print(f"  decades: {sorted(df['decade'].unique())}")

    h_e1 = load_h_e1_results()
    if h_e1:
        ht = h_e1.get("proposed", {}).get("has_tags", {})
        print(f"✓ H-E1 model_results loaded: proposed IRR={ht.get('irr', 'N/A'):.4f}")
        print(f"  rc7_age_vs_decade keys: {list(h_e1.get('rc7_age_vs_decade', {}).keys())}")
    else:
        print("⚠ H-E1 results not available — will refit models")


if __name__ == "__main__":
    main()
