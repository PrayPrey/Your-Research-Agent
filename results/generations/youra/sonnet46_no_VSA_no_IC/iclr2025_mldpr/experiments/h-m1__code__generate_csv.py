"""
Generate pwc_cov_computed.csv from H-E1 pipeline.
Run once from h-m1/code/ directory with youra-h-e1 or youra-h-m1 conda env.
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

# H-E1 code path
H_E1_CODE = Path(__file__).parent.parent.parent / "h-e1" / "code"
sys.path.insert(0, str(H_E1_CODE))

import numpy as np
import pandas as pd

from config import load_config
from ingest_pwc import fetch_pwc_benchmarks, fetch_pwc_results_via_evaluations
from derive import compute_result_cov
from pipeline import ols_detrend

OUT_CSV = Path(__file__).parent / "data" / "pwc_cov_computed.csv"


def main() -> None:
    cfg = load_config()

    print("Fetching PwC benchmarks...")
    pwc_df = fetch_pwc_benchmarks(min_papers=cfg.min_papers)
    print(f"  {len(pwc_df)} benchmarks")

    print("Fetching PwC results...")
    results_df = fetch_pwc_results_via_evaluations(pwc_df)

    print("Computing CoV...")
    cov_series = compute_result_cov(results_df)
    merged = pwc_df.set_index("name").join(cov_series, how="inner").dropna(subset=["result_CoV"])
    merged = merged.reset_index()
    N = len(merged)
    print(f"  N={N} benchmarks with CoV")

    paper_counts = merged["paper_count"].values.astype(float)
    cov_values = merged["result_CoV"].values.astype(float)

    print("OLS detrending...")
    sorted_pc, residual_cov, ols_metrics = ols_detrend(paper_counts, cov_values)

    # Build output DF sorted by paper_count ascending
    names_sorted = merged.sort_values("paper_count")["name"].values
    out_df = pd.DataFrame({
        "benchmark_name": names_sorted,
        "paper_count": sorted_pc.astype(int),
        "cov": cov_values[np.argsort(paper_counts, kind="stable")],
        "residual_cov": residual_cov,
    })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUT_CSV, index=False)
    print(f"Saved {len(out_df)} rows → {OUT_CSV}")
    print(f"OLS metrics: rho={ols_metrics['rho']:.4f}, r2={ols_metrics['r2']:.4f}")


if __name__ == "__main__":
    main()
