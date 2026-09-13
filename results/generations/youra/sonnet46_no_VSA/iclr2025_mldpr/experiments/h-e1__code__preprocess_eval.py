"""
Preprocess pwc-archive/evaluation-tables into a flat CSV with task_path, paper_url, paper_date.
Uses PyArrow native ops to avoid slow Python-level iteration.
Saves: eval_flat.parquet (cached for reuse).
"""

import os
import glob
import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.compute as pc
import pandas as pd

ARROW_DIR = (
    "/home/PrayPrey/.cache/huggingface/datasets/"
    "pwc-archive___evaluation-tables/default/0.0.0/"
    "7dd607a42427a2c27fcedc689a7415df58788c50/"
)
OUT_FILE = "eval_flat.parquet"


def load_all_shards():
    files = sorted(glob.glob(os.path.join(ARROW_DIR, "*.arrow")))
    tables = []
    for f in files:
        reader = ipc.open_stream(f)
        tables.append(reader.read_all())
    return pa.concat_tables(tables)


def extract_task_paper_url(tbl: pa.Table) -> pd.DataFrame:
    """
    For each task row, explode datasets list → sota.rows list → extract paper_url, paper_date.
    Uses PyArrow repeated list_flatten + struct field extraction for speed.
    """
    # Combine chunks to single arrays
    task_col = tbl["task"].combine_chunks()
    datasets_col = tbl["datasets"].combine_chunks()

    # Step 1: track which task each dataset entry belongs to
    # list_offsets gives the boundaries in the flattened array
    datasets_offsets = datasets_col.offsets.to_pylist()  # length n_tasks+1
    datasets_flat = pc.list_flatten(datasets_col)  # struct array, len = sum(len(datasets_i))

    # Step 2: build task_slug for each flattened dataset entry
    # For task i, datasets_offsets[i]..datasets_offsets[i+1] rows belong to task i
    n_tasks = len(task_col)
    task_slugs_per_ds = []
    for i in range(n_tasks):
        slug = task_col[i].as_py() or ""
        slug = slug.lower().strip().replace(" ", "-").replace("_", "-")
        count = datasets_offsets[i + 1] - datasets_offsets[i]
        task_slugs_per_ds.extend([slug] * count)

    # Step 3: extract sota.rows from each flattened dataset entry
    sota_col = datasets_flat.field("sota")  # struct array
    rows_col = sota_col.field("rows")  # list<struct> array

    # offsets for sota rows per dataset entry
    rows_offsets = rows_col.offsets.to_pylist()  # length len(datasets_flat)+1
    rows_flat = pc.list_flatten(rows_col)  # struct array

    # Step 4: map task_slug to each row entry
    n_ds = len(datasets_flat)
    task_slugs_per_row = []
    for i in range(n_ds):
        slug = task_slugs_per_ds[i]
        count = rows_offsets[i + 1] - rows_offsets[i]
        task_slugs_per_row.extend([slug] * count)

    # Step 5: extract paper_url and paper_date from rows_flat struct
    paper_url_col = rows_flat.field("paper_url")
    paper_date_col = rows_flat.field("paper_date")

    result = pd.DataFrame({
        "task_path": task_slugs_per_row,
        "paper_url": paper_url_col.to_pylist(),
        "paper_date": paper_date_col.to_pylist(),
    })
    return result


def main():
    if os.path.exists(OUT_FILE):
        print(f"Cache found: {OUT_FILE} — loading")
        df = pd.read_parquet(OUT_FILE)
        print(f"Loaded {len(df)} rows, {df['task_path'].nunique()} tasks")
        return df

    print("Loading Arrow shards...")
    tbl = load_all_shards()
    print(f"Loaded {len(tbl)} task rows")

    print("Extracting paper_url via PyArrow...")
    df = extract_task_paper_url(tbl)
    print(f"Extracted {len(df)} rows, {df['task_path'].nunique()} tasks")
    print(f"Non-null paper_url: {df['paper_url'].notna().sum()}")

    # Extract pub_year from paper_date
    df["pub_year"] = pd.to_datetime(df["paper_date"], errors="coerce").dt.year

    df.to_parquet(OUT_FILE, index=False)
    print(f"Saved: {OUT_FILE}")
    return df


if __name__ == "__main__":
    df = main()
    print(df.head())
    print(df.dtypes)
