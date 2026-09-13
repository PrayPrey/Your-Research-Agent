# Architecture: H-M2 — AIC-Based Model Comparison

**Applied**: reuse-prior-experiment pattern (H-E1 fitting.py reused directly)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1 + H-M1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`, `docs/youra_research/h-m1/code/`
**Findings**: H-E1 `fitting.py` already implements `logistic()`, `fit_linear()`, and `_r2_aic()` (which includes AIC). Column names in actual CSVs are `months` and `monthly_max` (not `month_idx`/`max_score` as PRD states — trust the code). H-M1 `run.py` shows single-file pattern with inline data loading, fitting, and figures.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| logistic | `sys.path` insert or copy | `h-e1/code/fitting.py` |
| fit_linear | same | `h-e1/code/fitting.py` |
| _r2_aic | same | `h-e1/code/fitting.py` |
| glue CSV | relative path | `h-e1/code/data/glue_timeseries_clean.csv` |
| superglue CSV | relative path | `h-e1/code/data/superglue_timeseries_clean.csv` |

**Verified from**: `docs/youra_research/h-e1/code/` and `docs/youra_research/h-m1/code/run.py`

---

## File Organization

```
docs/youra_research/h-m2/
  code/
    run.py        # single script: load → fit → AIC → gate → figures → results.json
  figures/        # 4 output figures (auto-created)
  results.json    # gate result + all AIC values
  experiment.log  # timestamped trace
```

---

## Module Structure

### run.py (`docs/youra_research/h-m2/code/run.py`)

**Dependencies**: numpy, scipy, matplotlib, pandas; reuses fitting logic from h-e1/code/fitting.py (copied inline or sys.path)

Single-file design — ~200 lines. Functions:

```python
# Data
def load_timeseries(csv_path: str) -> tuple[np.ndarray, np.ndarray]: ...
    # returns (t, y); columns: months, monthly_max
    # raises FileNotFoundError with clear message if missing

# Models
def logistic(t, K, r, t0) -> np.ndarray: ...           # reuse from h-e1/fitting.py
def fit_logistic(t, y) -> dict: ...                     # reuse from h-e1/fitting.py; keys: popt, aic, converged
def fit_linear(t, y) -> dict: ...                       # reuse from h-e1/fitting.py; keys: coeffs, aic
def fit_power_law(t, y) -> dict: ...                    # new; keys: popt, aic, converged
def _r2_aic(y, y_pred, k) -> tuple[float, float]: ...  # reuse from h-e1/fitting.py

# AIC
def compute_delta_aic(fit_a: dict, fit_b: dict) -> float: ...  # fit_a["aic"] - fit_b["aic"]

# Gate
def verify_gate(results: dict) -> tuple[bool, dict]: ...
    # primary: delta_log_vs_lin < -4 for both benchmarks
    # secondary: delta_log_vs_pl < -2 for both benchmarks

# Figures (4 total, saved to h-m2/figures/)
def plot_gate_metrics(results: dict, out_dir: Path) -> None: ...    # FR-7.1 bar chart + threshold lines
def plot_model_fits(data: dict, fits: dict, out_dir: Path) -> None: ...  # FR-7.2 overlay 2 subplots
def plot_residuals(data: dict, fits: dict, out_dir: Path) -> None: ...   # FR-7.3 residuals vs time
def plot_aic_comparison(results: dict, out_dir: Path) -> None: ...       # FR-7.4 grouped bar chart

# Output
def write_results(results: dict, gate: tuple, out_path: Path) -> None: ...  # results.json
def setup_logging(log_path: Path) -> logging.Logger: ...

# Entry
def main() -> None: ...
    # 1. load GLUE + SuperGLUE
    # 2. fit all 3 models for each benchmark
    # 3. compute delta AICs
    # 4. verify gate
    # 5. generate 4 figures
    # 6. write results.json + experiment.log
    # 7. print summary table

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & data loading | Project structure, load CSVs, validate columns, log stats | 5 | 1+1+1+2 |
| A-2 | Reuse H-E1 fitting code | Copy/import logistic, fit_logistic, fit_linear, _r2_aic; verify column name mapping | 6 | 2+2+1+1 |
| A-3 | Power law model | Implement fit_power_law (a*(t+1)^b, k=2, curve_fit with bounds) | 5 | 1+1+2+1 |
| A-4 | AIC comparison & gate | compute_delta_aic, verify_gate (primary + secondary thresholds) | 7 | 2+1+2+2 |
| A-5 | Figures (4 required) | gate metrics bar, model fit overlay, residuals, AIC grouped bar | 9 | 2+1+3+3 |
| A-6 | Results output & integration | write_results (results.json), experiment.log, stdout summary, end-to-end run | 6 | 1+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5], Low(4-8): [A-1, A-2, A-3, A-4, A-6]

---

## Notes for Phase 4 Coder

- **Column names**: actual CSVs use `months` and `monthly_max` (from H-M1 run.py), NOT `month_idx`/`max_score` as the PRD states.
- **Fitting code**: copy the 3 reused functions from `h-e1/code/fitting.py` inline — avoids sys.path manipulation across experiment directories.
- **Figures output dir**: `docs/youra_research/h-m2/figures/` — create with `Path(...).mkdir(parents=True, exist_ok=True)`.
- **Power law singularity**: use `t + 1` (t is 0-based months index).
- **Gate sign convention**: ΔAIC = AIC_logistic − AIC_linear; negative means logistic preferred; gate passes at < −4.
