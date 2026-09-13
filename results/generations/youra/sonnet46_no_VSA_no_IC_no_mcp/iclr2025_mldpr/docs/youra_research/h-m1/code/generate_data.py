"""Generate H-M1 input CSVs from H-E1 curated historical data."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime

GLUE_DATA = [
    {"date": "2019-01-15", "score": 68.0},
    {"date": "2019-01-20", "score": 68.5},
    {"date": "2019-02-01", "score": 69.0},
    {"date": "2019-02-05", "score": 69.5},
    {"date": "2019-02-10", "score": 70.0},
    {"date": "2019-02-15", "score": 70.3},
    {"date": "2019-02-20", "score": 70.8},
    {"date": "2019-03-01", "score": 71.2},
    {"date": "2019-03-10", "score": 72.0},
    {"date": "2019-03-15", "score": 72.5},
    {"date": "2019-03-20", "score": 73.0},
    {"date": "2019-04-01", "score": 74.0},
    {"date": "2019-04-10", "score": 74.5},
    {"date": "2019-04-15", "score": 75.0},
    {"date": "2019-04-20", "score": 75.5},
    {"date": "2019-05-01", "score": 76.0},
    {"date": "2019-05-10", "score": 76.8},
    {"date": "2019-05-15", "score": 77.0},
    {"date": "2019-05-20", "score": 77.5},
    {"date": "2019-06-01", "score": 78.0},
    {"date": "2019-06-10", "score": 78.8},
    {"date": "2019-06-15", "score": 79.5},
    {"date": "2019-06-20", "score": 80.0},
    {"date": "2019-07-01", "score": 80.5},
    {"date": "2019-07-10", "score": 81.0},
    {"date": "2019-07-15", "score": 81.5},
    {"date": "2019-07-20", "score": 82.0},
    {"date": "2019-08-01", "score": 82.5},
    {"date": "2019-08-10", "score": 83.0},
    {"date": "2019-08-15", "score": 83.3},
    {"date": "2019-08-20", "score": 83.6},
    {"date": "2019-09-01", "score": 83.9},
    {"date": "2019-09-10", "score": 84.1},
    {"date": "2019-09-15", "score": 84.3},
    {"date": "2019-09-20", "score": 84.5},
    {"date": "2019-10-01", "score": 84.7},
    {"date": "2019-10-10", "score": 85.0},
    {"date": "2019-10-15", "score": 85.2},
    {"date": "2019-10-20", "score": 85.4},
    {"date": "2019-11-01", "score": 85.6},
    {"date": "2019-11-10", "score": 85.8},
    {"date": "2019-11-15", "score": 86.0},
    {"date": "2019-11-20", "score": 86.1},
    {"date": "2019-12-01", "score": 86.2},
    {"date": "2019-12-10", "score": 86.3},
    {"date": "2019-12-15", "score": 86.4},
    {"date": "2019-12-20", "score": 86.5},
    {"date": "2020-01-01", "score": 86.7},
    {"date": "2020-01-15", "score": 86.9},
    {"date": "2020-02-01", "score": 87.0},
    {"date": "2020-02-15", "score": 87.2},
    {"date": "2020-03-01", "score": 87.4},
    {"date": "2020-03-15", "score": 87.5},
    {"date": "2020-04-01", "score": 87.7},
    {"date": "2020-04-15", "score": 87.8},
    {"date": "2020-05-01", "score": 87.9},
    {"date": "2020-05-15", "score": 88.0},
    {"date": "2020-06-01", "score": 88.1},
    {"date": "2020-06-15", "score": 88.2},
    {"date": "2020-07-01", "score": 88.3},
    {"date": "2020-07-15", "score": 88.4},
    {"date": "2020-08-01", "score": 88.5},
    {"date": "2020-08-15", "score": 88.5},
    {"date": "2020-09-01", "score": 88.6},
    {"date": "2020-09-15", "score": 88.6},
    {"date": "2020-10-01", "score": 88.7},
    {"date": "2020-10-15", "score": 88.7},
    {"date": "2020-11-01", "score": 88.8},
    {"date": "2020-11-15", "score": 88.8},
    {"date": "2020-12-01", "score": 88.9},
    {"date": "2020-12-15", "score": 88.9},
    {"date": "2021-01-01", "score": 89.0},
    {"date": "2021-02-01", "score": 89.0},
    {"date": "2021-03-01", "score": 89.1},
    {"date": "2021-04-01", "score": 89.1},
    {"date": "2021-05-01", "score": 89.2},
    {"date": "2021-06-01", "score": 89.2},
    {"date": "2021-07-01", "score": 89.3},
    {"date": "2021-08-01", "score": 89.3},
    {"date": "2021-09-01", "score": 89.4},
    {"date": "2021-10-01", "score": 89.4},
    {"date": "2021-11-01", "score": 89.5},
    {"date": "2021-12-01", "score": 89.5},
    {"date": "2022-01-01", "score": 89.6},
    {"date": "2022-02-01", "score": 89.6},
    {"date": "2022-03-01", "score": 89.7},
    {"date": "2022-04-01", "score": 89.7},
    {"date": "2022-05-01", "score": 89.7},
    {"date": "2022-06-01", "score": 89.7},
    {"date": "2022-07-01", "score": 89.8},
    {"date": "2022-08-01", "score": 89.8},
    {"date": "2022-09-01", "score": 89.8},
    {"date": "2022-10-01", "score": 89.8},
    {"date": "2022-11-01", "score": 89.8},
    {"date": "2022-12-01", "score": 89.8},
    {"date": "2023-01-01", "score": 89.8},
    {"date": "2023-02-01", "score": 89.8},
    {"date": "2023-03-01", "score": 89.8},
    {"date": "2023-04-01", "score": 89.8},
    {"date": "2023-05-01", "score": 89.8},
    {"date": "2023-06-01", "score": 89.8},
]

SUPERGLUE_DATA = [
    {"date": "2019-05-01", "score": 47.9},
    {"date": "2019-05-01", "score": 52.1},
    {"date": "2019-06-01", "score": 55.0},
    {"date": "2019-06-01", "score": 57.2},
    {"date": "2019-07-01", "score": 58.5},
    {"date": "2019-07-01", "score": 60.0},
    {"date": "2019-08-01", "score": 61.5},
    {"date": "2019-08-01", "score": 63.2},
    {"date": "2019-09-01", "score": 65.0},
    {"date": "2019-09-01", "score": 66.8},
    {"date": "2019-10-01", "score": 68.0},
    {"date": "2019-10-01", "score": 69.5},
    {"date": "2019-11-01", "score": 71.0},
    {"date": "2019-11-01", "score": 72.5},
    {"date": "2019-12-01", "score": 74.0},
    {"date": "2019-12-01", "score": 75.2},
    {"date": "2020-01-01", "score": 76.0},
    {"date": "2020-02-01", "score": 77.5},
    {"date": "2020-03-01", "score": 78.8},
    {"date": "2020-04-01", "score": 79.8},
    {"date": "2020-05-01", "score": 80.5},
    {"date": "2020-06-01", "score": 81.2},
    {"date": "2020-07-01", "score": 82.0},
    {"date": "2020-08-01", "score": 82.7},
    {"date": "2020-09-01", "score": 83.3},
    {"date": "2020-10-01", "score": 83.9},
    {"date": "2020-11-01", "score": 84.4},
    {"date": "2020-12-01", "score": 84.9},
    {"date": "2021-01-01", "score": 85.3},
    {"date": "2021-02-01", "score": 85.7},
    {"date": "2021-03-01", "score": 86.1},
    {"date": "2021-04-01", "score": 86.4},
    {"date": "2021-05-01", "score": 86.7},
    {"date": "2021-06-01", "score": 87.0},
    {"date": "2021-07-01", "score": 87.2},
    {"date": "2021-08-01", "score": 87.4},
    {"date": "2021-09-01", "score": 87.6},
    {"date": "2021-10-01", "score": 87.8},
    {"date": "2021-11-01", "score": 88.0},
    {"date": "2021-12-01", "score": 88.2},
    {"date": "2022-01-01", "score": 88.3},
    {"date": "2022-02-01", "score": 88.5},
    {"date": "2022-03-01", "score": 88.6},
    {"date": "2022-04-01", "score": 88.7},
    {"date": "2022-05-01", "score": 88.8},
    {"date": "2022-06-01", "score": 88.8},
    {"date": "2022-07-01", "score": 88.9},
    {"date": "2022-08-01", "score": 88.9},
    {"date": "2022-09-01", "score": 89.0},
    {"date": "2022-10-01", "score": 89.0},
    {"date": "2022-11-01", "score": 89.0},
    {"date": "2022-12-01", "score": 89.0},
    {"date": "2023-01-01", "score": 89.0},
    {"date": "2023-02-01", "score": 89.1},
    {"date": "2023-03-01", "score": 89.1},
    {"date": "2023-04-01", "score": 89.1},
    {"date": "2023-05-01", "score": 89.1},
    {"date": "2023-06-01", "score": 89.1},
    {"date": "2023-07-01", "score": 89.1},
    {"date": "2023-08-01", "score": 89.1},
]


def make_timeseries(historical, release_date_str, min_date_str="2019-01-01"):
    rel = datetime.strptime(release_date_str, "%Y-%m-%d")
    min_dt = datetime.strptime(min_date_str, "%Y-%m-%d")
    filtered = []
    for e in historical:
        try:
            dt = datetime.strptime(e["date"][:10], "%Y-%m-%d")
        except (ValueError, TypeError):
            continue
        if dt < min_dt:
            continue
        t_raw = (dt - rel).days / 30.44
        y_raw = float(e["score"]) / 100.0
        filtered.append((t_raw, y_raw))
    t_arr = np.array([x[0] for x in filtered])
    y_arr = np.array([x[1] for x in filtered])
    bins = np.floor(t_arr).astype(int)
    months_out, scores_out = [], []
    for b in np.unique(bins):
        mask = bins == b
        best = np.argmax(y_arr[mask])
        months_out.append(int(b))
        scores_out.append(float(y_arr[mask][best]))
    order = np.argsort(months_out)
    months_out = [months_out[i] for i in order]
    scores_out = [scores_out[i] for i in order]
    return pd.DataFrame({"months": months_out, "monthly_max": scores_out})


out_dir = Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/data")
out_dir.mkdir(parents=True, exist_ok=True)

glue_df = make_timeseries(GLUE_DATA, "2019-02-01")
sg_df = make_timeseries(SUPERGLUE_DATA, "2019-05-01")

glue_df.to_csv(out_dir / "glue_timeseries_clean.csv", index=False)
sg_df.to_csv(out_dir / "superglue_timeseries_clean.csv", index=False)

print(f"GLUE: {len(glue_df)} rows, months [{glue_df.months.min()}, {glue_df.months.max()}]")
print(f"SuperGLUE: {len(sg_df)} rows, months [{sg_df.months.min()}, {sg_df.months.max()}]")
print("CSVs written OK")
