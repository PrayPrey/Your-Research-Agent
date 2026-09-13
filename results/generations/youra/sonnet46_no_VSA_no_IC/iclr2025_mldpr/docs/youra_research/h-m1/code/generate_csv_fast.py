"""
Generate pwc_cov_computed.csv from H-E1 cached Arrow files directly.
Uses pyarrow for fast loading without HuggingFace datasets overhead.
"""
from __future__ import annotations
import sys
import re
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.ipc as ipc
from scipy.stats import linregress

ARROW_DIR = Path("/home/PrayPrey/.cache/huggingface/datasets/pwc-archive___evaluation-tables/default/0.0.0/7dd607a42427a2c27fcedc689a7415df58788c50")
ARROW_FILES = sorted(ARROW_DIR.glob("*.arrow"))

OUT_CSV = Path(__file__).parent / "data" / "pwc_cov_computed.csv"

MIN_PAPERS = 38
MIN_COV_ROWS = 3
NORM_REGEX = re.compile(r"[^a-z0-9 ]")


def normalize_name(s: str) -> str:
    s = str(s).lower()
    s = NORM_REGEX.sub("", s)
    return re.sub(r"\s+", " ", s).strip()


def load_all_records() -> pd.DataFrame:
    """Load all Arrow files into a single DataFrame."""
    frames = []
    for arrow_file in ARROW_FILES:
        print(f"  Loading {arrow_file.name}...", flush=True)
        with open(arrow_file, "rb") as f:
            try:
                reader = ipc.open_file(f)
            except pa.lib.ArrowInvalid:
                f.seek(0)
                reader = ipc.open_stream(f)
            table = reader.read_all()
        df = table.to_pandas()
        frames.append(df)
        print(f"    {len(df)} rows, columns: {list(df.columns)[:8]}", flush=True)
    return pd.concat(frames, ignore_index=True)


def compute_cov(results_df: pd.DataFrame) -> pd.Series:
    """CoV (std/mean) of metric_value per benchmark (requires >= MIN_COV_ROWS rows)."""
    def cov_fn(vals):
        vals = vals.dropna()
        if len(vals) < MIN_COV_ROWS:
            return float("nan")
        mean = vals.mean()
        if mean == 0:
            return float("nan")
        return vals.std(ddof=1) / mean
    return results_df.groupby("benchmark_name")["metric_value"].apply(cov_fn).rename("result_CoV")


def ols_detrend(paper_counts: np.ndarray, cov_values: np.ndarray):
    sort_idx = np.argsort(paper_counts, kind="stable")
    sorted_pc = paper_counts[sort_idx]
    sorted_cov = cov_values[sort_idx]
    slope, intercept, rho, _, _ = linregress(sorted_pc, sorted_cov)
    fitted = slope * sorted_pc + intercept
    residual_cov = sorted_cov - fitted
    return sorted_pc, residual_cov, rho


def main() -> None:
    print("Loading Arrow files...", flush=True)
    df = load_all_records()
    print(f"Total records: {len(df)}", flush=True)
    print(f"Columns: {list(df.columns)}", flush=True)

    # Try to identify benchmark + paper_count + metric columns
    # Expected schema from HF dataset
    cols = set(df.columns)

    # Identify benchmark_name column
    bname_col = None
    for c in ["dataset", "benchmark_name", "task", "name"]:
        if c in cols:
            bname_col = c
            break

    # Identify paper_count column
    pc_col = None
    for c in ["paper_count", "num_papers", "papers"]:
        if c in cols:
            pc_col = c
            break

    # Identify metric_value column
    mv_col = None
    for c in ["metric_value", "score", "value", "result"]:
        if c in cols:
            mv_col = c
            break

    print(f"Using: benchmark={bname_col}, paper_count={pc_col}, metric_value={mv_col}", flush=True)

    if bname_col is None or pc_col is None:
        print("ERROR: Cannot identify required columns")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)

    # Filter benchmarks with >= MIN_PAPERS
    if pc_col in cols:
        bm_papers = df.groupby(bname_col)[pc_col].max().fillna(0)
        bm_valid = bm_papers[bm_papers >= MIN_PAPERS].index
        df_filtered = df[df[bname_col].isin(bm_valid)].copy()
    else:
        df_filtered = df.copy()

    print(f"Benchmarks with >= {MIN_PAPERS} papers: {df_filtered[bname_col].nunique()}", flush=True)

    # Compute CoV
    if mv_col:
        df_filtered = df_filtered.rename(columns={bname_col: "benchmark_name", mv_col: "metric_value"})
        cov_series = compute_cov(df_filtered)
    else:
        print("No metric_value column — using paper_count proxy for CoV")
        cov_series = pd.Series(dtype=float)

    # Build benchmark-level table
    pc_table = df.groupby(bname_col)[pc_col].max().rename("paper_count")
    merged = pc_table.reset_index().rename(columns={bname_col: "benchmark_name"})
    merged = merged[merged["benchmark_name"].isin(bm_valid)]
    if len(cov_series) > 0:
        merged = merged.set_index("benchmark_name").join(cov_series, how="inner").dropna(subset=["result_CoV"]).reset_index()
    N = len(merged)
    print(f"Benchmarks with CoV: N={N}", flush=True)

    paper_counts = merged["paper_count"].values.astype(float)
    cov_values = merged["result_CoV"].values.astype(float)

    # OLS detrend
    sorted_pc, residual_cov, rho = ols_detrend(paper_counts, cov_values)
    sort_idx = np.argsort(paper_counts, kind="stable")
    sorted_names = merged.iloc[sort_idx]["benchmark_name"].values
    sorted_cov = cov_values[sort_idx]

    out_df = pd.DataFrame({
        "benchmark_name": sorted_names,
        "paper_count": sorted_pc.astype(int),
        "cov": sorted_cov,
        "residual_cov": residual_cov,
    })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUT_CSV, index=False)
    print(f"Saved {len(out_df)} rows → {OUT_CSV}", flush=True)
    print(f"OLS rho={rho:.4f}", flush=True)


if __name__ == "__main__":
    main()
