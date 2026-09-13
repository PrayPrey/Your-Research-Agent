# Logic: H-M4 Saturation Detection

Applied: Standard scipy/pandas dual-criterion detection pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from H-M3 actual code
**Analyzed Path**: `docs/youra_research/h-m3/code/run.py`
**Relevant Symbols**:
- `load_timeseries(csv_path: str) -> tuple[np.ndarray, np.ndarray]` — returns (t, y)
- `extract_params(t_data, y_data, benchmark_name) -> dict` — keys: K, r, t0_relative, t0_absolute, perr, ci_95, pcov, popt, pcov_finite, bootstrap_used
- `logistic(t, K, r, t0) -> np.ndarray`
- `bootstrap_ci(t, y, popt_ref, n=500) -> tuple[np.ndarray, np.ndarray]`
- `check_pcov_validity(pcov) -> bool`
- `verify_mechanism_activated(params: dict) -> tuple[bool, dict]` — H-M3 signature differs from H-M4 usage; H-M4 defines its own version

---

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-m3/code/run.py (ACTUAL CODE)

def load_timeseries(csv_path: str) -> tuple:
    """Returns (t, y): t=months_since_release float[], y=max_score float[]"""
    ...

def extract_params(
    t_data: np.ndarray,
    y_data: np.ndarray,
    benchmark_name: str,  # "glue" or "superglue"
) -> dict:
    """Returns dict with keys: K, r, t0_relative, t0_absolute, perr, ci_95, pcov, popt,
       pcov_finite, bootstrap_used"""
    ...

def logistic(t: np.ndarray, K: float, r: float, t0: float) -> np.ndarray: ...
def bootstrap_ci(t, y, popt_ref, n=500) -> tuple: ...  # (perr, samples)
def check_pcov_validity(pcov: np.ndarray) -> bool: ...
```

**Verified from**: `docs/youra_research/h-m3/code/run.py` (actual implementation)

**Note**: H-M3 `load_timeseries` returns raw `(t, y)` — no calendar dates.
H-M4 derives `calendar_month` via `LAUNCH_DATES[bm]` + month offset.

---

## A-5: Sensitivity & Prospective [Complexity: 11, Budget: 4 subtasks → 2 used here]

### API Signatures

```python
GROUND_TRUTH  = {"glue": "2019-09", "superglue": "2021-06"}
LAUNCH_DATES  = {"glue": "2018-04", "superglue": "2019-05"}

def sensitivity_grid(
    monthly_df: pd.DataFrame,   # must have top3_mean, monthly_gain, calendar_month
    K: float,
    ks: list[float],            # threshold_k values e.g. [0.95, 0.99, 1.00]
    rates: list[float],         # threshold_rate values e.g. [0.02, 0.05, 0.10]
    ground_truth: str,          # "YYYY-MM"
) -> pd.DataFrame:
    """Returns DataFrame with columns: threshold_k, threshold_rate, sat_date, sat_error_months"""
    ...

def prospective_forecast(
    monthly_df: pd.DataFrame,   # full timeseries
    t: np.ndarray,              # months_since_release  [N]
    y: np.ndarray,              # max_score             [N]
    sat_month_idx: int,         # detected saturation index
    lookback: int = 6,          # truncate at sat_month_idx - lookback
) -> tuple[str | None, float]:
    """Returns (forecast_date: 'YYYY-MM' | None, forecast_error_months: float)"""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | sensitivity_grid | 3×3 grid enumerate, call detect_saturation_date per cell, collect errors |
| L-5-2 | prospective_forecast | Truncate at idx-lookback, re-fit logistic, find forecast sat date |

### Pseudo-code: L-5-1 sensitivity_grid

```
rows = []
peak_rate = monthly_df["monthly_gain"].max()
for tk in ks:
    for tr in rates:
        sat_date, _ = detect_saturation_date(monthly_df, K, tk, tr)
        err = compute_saturation_error(sat_date, ground_truth)
        rows.append({"threshold_k": tk, "threshold_rate": tr,
                     "sat_date": sat_date, "sat_error_months": err})
return pd.DataFrame(rows)
```

### Pseudo-code: L-5-2 prospective_forecast

```
cut = sat_month_idx - lookback          # truncation point
if cut < 6: return (None, inf)          # not enough data to refit
t_trunc, y_trunc = t[:cut], y[:cut]
params_trunc = extract_params(t_trunc, y_trunc, benchmark_name)
K_trunc = params_trunc["K"]
# rebuild truncated monthly_df from t_trunc, y_trunc
monthly_trunc = build_monthly_df(t_trunc, y_trunc, benchmark_name)
forecast_date, _ = detect_saturation_date(monthly_trunc, K_trunc)
err = compute_saturation_error(forecast_date, ground_truth)
return (forecast_date, err)
```

---

## A-7: Main + Results I/O [Complexity: 9, Budget: 2 used here]

### API Signatures

```python
def main() -> None:
    """Orchestrate full H-M4 pipeline; exit(0) on gate pass, exit(1) on fail."""
    ...

def write_results(results: dict, out_path: Path) -> None:
    """Serialize results dict to JSON at out_path."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | main() pipeline | Load → fit → detect → sensitivity → prospective → plot → gate → write |
| L-7-2 | results.json schema | Define output JSON structure |

### Pseudo-code: L-7-1 main() pipeline

```
1. Setup dirs, logging (mirror H-M3 pattern)

2. Pre-run assertions:
   assert h-m3 experiment_results.json exists
   t_glue, y_glue = load_timeseries(glue_csv)
   t_sg, y_sg     = load_timeseries(superglue_csv)

3. For each bm in [glue, superglue]:
   a. params = extract_params(t, y, bm)        # reuse H-M3
   b. K = params["K"]
   c. assert K > 0
   d. monthly_df = build_monthly_df(t, y, bm)  # adds top3_mean, monthly_gain, calendar_month
   e. assert len(monthly_df) >= 12
   f. assert {"top3_mean","monthly_gain","calendar_month"} <= set(monthly_df.columns)

4. For each bm:
   sat_date, sat_idx = detect_saturation_date(monthly_df, K)
   sat_error = compute_saturation_error(sat_date, GROUND_TRUTH[bm])
   criterion_fired = sat_date is not None

5. verify_mechanism_activated(results) → (glue_ok, sg_ok, indicators)

6. Sensitivity grid for each bm:
   grid = sensitivity_grid(monthly_df, K, [0.95,0.99,1.00], [0.02,0.05,0.10], GROUND_TRUTH[bm])

7. Prospective (GLUE only, per PRD P3):
   forecast_date, forecast_err = prospective_forecast(
       monthly_df_glue, t_glue, y_glue, sat_idx_glue)

8. Gate logic:
   gate_pass = (sat_error_glue < 6) AND (sat_error_sg < 6)

9. Plots: plot_sat_error_bar, plot_saturation_timeline, plot_dual_criterion_activation,
          plot_prospective_forecast, plot_sensitivity_heatmap

10. write_results(results, out_path)
    sys.exit(0 if gate_pass else 1)
```

### L-7-2: results.json Schema

```json
{
  "hypothesis_id": "h-m4",
  "gate_pass": true,
  "gate_result": "PASS",
  "glue": {
    "K": 0.8955,
    "sat_date": "2019-09",
    "sat_month_idx": 17,
    "sat_error_months": 0,
    "criterion_fired": true,
    "error_below_threshold": true,
    "prospective_forecast_date": "2019-08",
    "prospective_forecast_error": 1.0,
    "sensitivity_grid": [
      {"threshold_k": 0.95, "threshold_rate": 0.02, "sat_date": "...", "sat_error_months": 2}
    ]
  },
  "superglue": {
    "K": 0.8858,
    "sat_date": "2021-06",
    "sat_month_idx": 25,
    "sat_error_months": 0,
    "criterion_fired": true,
    "error_below_threshold": true,
    "sensitivity_grid": []
  },
  "mechanism_activated": {
    "glue": true,
    "superglue": true,
    "indicators": {}
  },
  "status": "completed"
}
```

---

## Summary: All 4 Subtasks

| ID | Subtask | A-Task |
|----|---------|--------|
| L-5-1 | sensitivity_grid() | A-5 |
| L-5-2 | prospective_forecast() truncated refit | A-5 |
| L-7-1 | main() pipeline with gate logic | A-7 |
| L-7-2 | results.json schema | A-7 |
