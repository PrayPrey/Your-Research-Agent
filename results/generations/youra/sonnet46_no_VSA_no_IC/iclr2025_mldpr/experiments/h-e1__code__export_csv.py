"""
One-shot: run H-E1 ingestion + CoV + OLS, save pwc_cov_computed.csv for H-M1.
Uses H-E1's existing pipeline so output is bit-for-bit identical to what H-E1 used.
"""
from __future__ import annotations
import sys
from pathlib import Path

_CODE_DIR = Path(__file__).parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

import numpy as np
import pandas as pd
from scipy.stats import linregress

from config import load_config
from ingest_pwc import fetch_pwc_benchmarks, fetch_pwc_results_via_evaluations
from derive import compute_result_cov

OUT_CSV = _CODE_DIR.parent.parent / "h-m1" / "code" / "data" / "pwc_cov_computed.csv"


def main() -> None:
    cfg = load_config()

    print("Fetching PwC benchmarks...")
    pwc_df = fetch_pwc_benchmarks(min_papers=cfg.min_papers)
    print(f"Benchmarks: {len(pwc_df)}")

    print("Fetching result rows...")
    results_df = fetch_pwc_results_via_evaluations(pwc_df)
    print(f"Result rows: {len(results_df)}")

    cov_series = compute_result_cov(results_df)
    merged = pwc_df.set_index("name").join(cov_series, how="inner").dropna(subset=["result_CoV"]).reset_index()
    N = len(merged)
    print(f"Benchmarks with CoV: N={N}")

    paper_counts = merged["paper_count"].values.astype(float)
    cov_values = merged["result_CoV"].values.astype(float)
    names = merged["name"].values

    sort_idx = np.argsort(paper_counts, kind="stable")
    sorted_pc = paper_counts[sort_idx]
    sorted_cov = cov_values[sort_idx]
    sorted_names = names[sort_idx]

    slope, intercept, rho, _, _ = linregress(sorted_pc, sorted_cov)
    residual_cov = sorted_cov - (slope * sorted_pc + intercept)

    out_df = pd.DataFrame({
        "benchmark_name": sorted_names,
        "paper_count": sorted_pc.astype(int),
        "cov": sorted_cov,
        "residual_cov": residual_cov,
    })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUT_CSV, index=False)
    print(f"Saved N={N} rows → {OUT_CSV}")
    print(f"OLS rho={rho:.4f}, slope={slope:.6f}")


if __name__ == "__main__":
    main()
