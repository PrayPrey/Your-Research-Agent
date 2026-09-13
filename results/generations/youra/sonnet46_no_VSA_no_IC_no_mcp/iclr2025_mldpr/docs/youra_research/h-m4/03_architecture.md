# Architecture: H-M4

**Applied**: dual-criterion saturation detection on logistic fit pipeline

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m3/code/run.py`
**Findings**: H-M3 is a single-file script. All reusable functions are top-level: `logistic`, `extract_params`, `bootstrap_ci`, `check_pcov_validity`, `load_timeseries`. Data sources: `data/glue_timeseries_clean.csv`, `data/superglue_timeseries_clean.csv`.

---

## File Organization

- `docs/youra_research/h-m4/code/run.py` — single script (extends H-M3 pattern)
- `docs/youra_research/h-m4/code/outputs/results.json`
- `docs/youra_research/h-m4/figures/` — 5 figures

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| logistic | copied/imported from h-m3 run.py | `h-m3/code/run.py:36` |
| extract_params | copied/imported from h-m3 run.py | `h-m3/code/run.py:45` |
| bootstrap_ci | copied/imported from h-m3 run.py | `h-m3/code/run.py:95` |
| check_pcov_validity | copied/imported from h-m3 run.py | `h-m3/code/run.py:119` |
| load_timeseries | copied/imported from h-m3 run.py | `h-m3/code/run.py:179` |

**Verified from**: `docs/youra_research/h-m3/code/run.py` (actual implementation)

**Note**: H-M3 `load_timeseries` reads columns `months_since_release`/`months` and `max_score`/`monthly_max`. H-M4 needs `calendar_month` column — must be derived from month index + benchmark launch date in the data prep step.

---

## Modules

### SaturationDetector (`code/run.py` — new functions)

**Dependencies**: extract_params (H-M3), load_timeseries (H-M3), pandas, dateutil

```python
GROUND_TRUTH = {"glue": "2019-09", "superglue": "2021-06"}
LAUNCH_DATES = {"glue": "2018-04", "superglue": "2019-05"}

def build_monthly_df(t: np.ndarray, y: np.ndarray, benchmark: str) -> pd.DataFrame:
    """Add top3_mean, monthly_gain, calendar_month columns."""
    ...

def detect_saturation_date(
    monthly_df: pd.DataFrame,
    K: float,
    threshold_k: float = 0.99,
    threshold_rate: float = 0.05,
) -> tuple[str | None, int | None]: ...

def compute_saturation_error(detected_date: str | None, ground_truth_date: str) -> float:
    """Returns abs error in months; float('inf') if detected_date is None."""
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, bool, dict]: ...

def prospective_forecast(
    monthly_df: pd.DataFrame,
    t: np.ndarray,
    y: np.ndarray,
    sat_month_idx: int,
    lookback: int = 6,
) -> tuple[str | None, float]: ...

def sensitivity_grid(
    monthly_df: pd.DataFrame,
    K: float,
    ks: list[float],
    rates: list[float],
    ground_truth: str,
) -> pd.DataFrame: ...
```

### Visualization (`code/run.py` — new plot functions)

**Dependencies**: matplotlib, seaborn, pandas

```python
def plot_sat_error_bar(results: dict, out_dir: Path) -> None: ...
def plot_saturation_timeline(data: dict, results: dict, params: dict, out_dir: Path) -> None: ...
def plot_dual_criterion_activation(monthly_df: pd.DataFrame, K: float, benchmark: str, sat_month_idx: int | None, out_dir: Path) -> None: ...
def plot_prospective_forecast(monthly_df: pd.DataFrame, sat_month_idx: int, forecast_date: str, out_dir: Path) -> None: ...
def plot_sensitivity_heatmap(grid_glue: pd.DataFrame, grid_superglue: pd.DataFrame, out_dir: Path) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & data prep | Create h-m4/code/, copy H-M3 reusable functions, build `build_monthly_df()` that adds top3_mean, monthly_gain, calendar_month | 8 | 2+1+3+2 |
| A-2 | detect_saturation_date | Implement dual-criterion AND logic; return (sat_date, sat_month_idx) or (None,None) | 7 | 1+2+2+2 |
| A-3 | compute_saturation_error | Implement month-arithmetic error; handle None→inf | 5 | 1+1+2+1 |
| A-4 | verify_mechanism_activated | Port from PRD pseudocode; check criterion fired + error threshold | 6 | 1+2+2+1 |
| A-5 | Sensitivity & prospective | sensitivity_grid (3×3) + prospective_forecast (truncated re-fit) | 11 | 2+3+4+2 |
| A-6 | Visualization | 5 figures: error bar, timeline, dual-criterion, prospective, heatmap | 10 | 2+2+3+3 |
| A-7 | Main + results I/O | Wire pipeline end-to-end; write results.json; pre-run assertions; gate logic | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5, A-6, A-7], Low(4-8): [A-1, A-2, A-3, A-4]
