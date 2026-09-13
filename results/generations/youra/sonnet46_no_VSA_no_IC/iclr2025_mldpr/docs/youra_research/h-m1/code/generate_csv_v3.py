"""
Fast CSV generation via direct Arrow IPC + pyarrow to_pylist.
Avoids load_dataset() overhead. ~12s total vs 30+ min.
"""
from __future__ import annotations
import time
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


def main() -> None:
    t_start = time.time()

    # Load Arrow files
    tables = []
    for af in ARROW_FILES:
        with open(af, "rb") as f:
            try:
                reader = ipc.open_file(f)
            except pa.lib.ArrowInvalid:
                f.seek(0)
                reader = ipc.open_stream(f)
            tables.append(reader.read_all())
    tbl = pa.concat_tables(tables)
    print(f"Arrow loaded: {len(tbl)} rows in {time.time()-t_start:.2f}s", flush=True)

    # Unpack to Python (datasets column is slow)
    task_col = tbl.column("task").to_pylist()
    datasets_col = tbl.column("datasets").to_pylist()
    print(f"to_pylist done in {time.time()-t_start:.2f}s", flush=True)

    bench_data: dict[str, int] = {}
    result_rows: list[tuple[str, float]] = []

    for task_name, datasets in zip(task_col, datasets_col):
        if not datasets:
            continue
        for dataset_entry in datasets:
            ds_name = dataset_entry.get("dataset", "")
            if not ds_name:
                continue
            sota = dataset_entry.get("sota") or {}
            rows = sota.get("rows") or []

            paper_titles: set[str] = set()
            for row in rows:
                pt = row.get("paper_title", "")
                if pt:
                    paper_titles.add(pt)

            paper_count = len(paper_titles)
            if paper_count < MIN_PAPERS:
                continue

            bench_name = f"{ds_name} [{task_name}]"
            if bench_name not in bench_data:
                bench_data[bench_name] = paper_count

            for row in rows:
                metrics = row.get("metrics") or {}
                mv = float("nan")
                for v in metrics.values():
                    if v is not None:
                        try:
                            mv = float(v)
                            break
                        except (TypeError, ValueError):
                            pass
                model = row.get("model_name", "")
                if not model or mv != mv:
                    continue
                result_rows.append((bench_name, mv))

    print(f"Parsed: {len(bench_data)} benches, {len(result_rows)} rows in {time.time()-t_start:.2f}s", flush=True)

    # CoV per benchmark
    from collections import defaultdict
    bench_vals: dict[str, list[float]] = defaultdict(list)
    for bench_name, mv in result_rows:
        bench_vals[bench_name].append(mv)

    records = []
    for bench_name, paper_count in bench_data.items():
        vals = bench_vals.get(bench_name, [])
        if len(vals) < MIN_COV_ROWS:
            continue
        arr = np.array(vals, dtype=float)
        mean = arr.mean()
        if mean == 0:
            continue
        cov = arr.std(ddof=1) / mean
        records.append({"benchmark_name": bench_name, "paper_count": paper_count, "cov": cov})

    merged = pd.DataFrame(records)
    N = len(merged)
    print(f"Benchmarks with CoV: N={N}", flush=True)

    paper_counts = merged["paper_count"].values.astype(float)
    cov_values = merged["cov"].values.astype(float)

    # OLS detrend (identical to H-E1 pipeline.py)
    sort_idx = np.argsort(paper_counts, kind="stable")
    sorted_pc = paper_counts[sort_idx]
    sorted_cov = cov_values[sort_idx]
    sorted_names = merged.iloc[sort_idx]["benchmark_name"].values

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
    print(f"Saved N={N} rows → {OUT_CSV}", flush=True)
    print(f"OLS rho={rho:.4f}, slope={slope:.6f}", flush=True)
    print(f"Total time: {time.time()-t_start:.2f}s", flush=True)


if __name__ == "__main__":
    main()
