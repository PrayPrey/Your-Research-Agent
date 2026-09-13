"""
Fast CSV generation: reads HF Arrow files directly with pyarrow (row iteration).
Replicates H-E1 ingest_pwc.py logic without HuggingFace datasets library.
"""
from __future__ import annotations
import sys
import re
from pathlib import Path

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


def _extract_year(date_str) -> int | None:
    if not date_str:
        return None
    try:
        return int(str(date_str)[:4])
    except (ValueError, TypeError):
        return None


def _get_primary_metric_value(metrics) -> float:
    if not metrics:
        return float("nan")
    if isinstance(metrics, dict):
        for v in metrics.values():
            if v is not None:
                try:
                    return float(v)
                except (TypeError, ValueError):
                    continue
    return float("nan")


def read_arrow_file(path: Path) -> list[dict]:
    """Read Arrow file, return list of Python dicts."""
    with open(path, "rb") as f:
        try:
            reader = ipc.open_file(f)
        except pa.lib.ArrowInvalid:
            f.seek(0)
            reader = ipc.open_stream(f)
        table = reader.read_all()
    return table.to_pylist()


def main() -> None:
    print("Loading Arrow records...", flush=True)
    all_records = []
    for af in ARROW_FILES:
        print(f"  {af.name}...", flush=True)
        records = read_arrow_file(af)
        all_records.extend(records)
    print(f"Total task records: {len(all_records)}", flush=True)

    # Pass 1: build benchmark-level stats (paper_count, year, rows per benchmark)
    bench_data: dict[str, dict] = {}
    result_rows: list[dict] = []

    for record in all_records:
        task_name = record.get("task", "")
        for dataset_entry in (record.get("datasets") or []):
            if not isinstance(dataset_entry, dict):
                continue
            ds_name = dataset_entry.get("dataset", "")
            if not ds_name:
                continue
            sota = dataset_entry.get("sota") or {}
            rows = sota.get("rows") or []

            paper_titles: set[str] = set()
            years: list[int] = []
            for row in rows:
                pt = row.get("paper_title", "")
                if pt:
                    paper_titles.add(pt)
                y = _extract_year(row.get("paper_date", ""))
                if y:
                    years.append(y)

            paper_count = len(paper_titles)
            if paper_count < MIN_PAPERS:
                continue

            bench_name = f"{ds_name} [{task_name}]"
            if bench_name not in bench_data:
                bench_data[bench_name] = {
                    "paper_count": paper_count,
                    "year_introduced": min(years) if years else None,
                    "task_name": task_name,
                    "dataset_name": ds_name,
                }

            for row in rows:
                metric_val = _get_primary_metric_value(row.get("metrics") or {})
                model = row.get("model_name", "")
                if not model or np.isnan(metric_val):
                    continue
                result_rows.append({
                    "benchmark_name": bench_name,
                    "model": model,
                    "metric_value": metric_val,
                    "year": _extract_year(row.get("paper_date", "")),
                })

    print(f"Benchmarks >= {MIN_PAPERS} papers: {len(bench_data)}", flush=True)
    print(f"Result rows: {len(result_rows)}", flush=True)

    results_df = pd.DataFrame(result_rows)
    pwc_df = pd.DataFrame([
        {"name": k, "paper_count": v["paper_count"]}
        for k, v in bench_data.items()
    ])

    # Compute CoV
    def cov_fn(vals):
        vals = vals.dropna()
        if len(vals) < MIN_COV_ROWS:
            return float("nan")
        mean = vals.mean()
        if mean == 0:
            return float("nan")
        return vals.std(ddof=1) / mean

    cov_series = results_df.groupby("benchmark_name")["metric_value"].apply(cov_fn).rename("result_CoV")

    merged = pwc_df.set_index("name").join(cov_series, how="inner").dropna(subset=["result_CoV"]).reset_index()
    N = len(merged)
    print(f"Benchmarks with CoV: N={N}", flush=True)

    paper_counts = merged["paper_count"].values.astype(float)
    cov_values = merged["result_CoV"].values.astype(float)

    # OLS detrend (same as H-E1 pipeline.py)
    sort_idx = np.argsort(paper_counts, kind="stable")
    sorted_pc = paper_counts[sort_idx]
    sorted_cov = cov_values[sort_idx]
    slope, intercept, rho, _, _ = linregress(sorted_pc, sorted_cov)
    residual_cov = sorted_cov - (slope * sorted_pc + intercept)
    sorted_names = merged.iloc[sort_idx]["name"].values

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
