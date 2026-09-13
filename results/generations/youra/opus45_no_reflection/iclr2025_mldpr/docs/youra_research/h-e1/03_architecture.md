# Architecture: H-E1 (EXISTENCE / PoC)

**Applied: None** — Archon KB has no statistical time-series / change-point pattern content (indexes ML model repos only, e.g. diffusers). Confirmed via `rag_search_knowledge_base("time series change point detection pipeline")` — no relevant hits. Using canonical `ruptures` library directly per PRD/brief.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis, no existing `src/`.

---

## File Structure (EXISTENCE minimal)

```
h-e1/code/
  data.py        # PWC loading + Gini aggregation
  model.py        # baseline (monotonic) + proposed (PELT segmented) models
  train.py         # run both models on full series, no training loop (stat analysis)
  evaluate.py       # BIC/p-value comparison, gate checks
  visualize.py      # 3 required figures
  config.py         # fixed constants
```

No ablation modules, no separate `models/` package — single flat structure per EXISTENCE rules.

---

## Module Interfaces

### `data.py`

**Dependencies**: datasets (HuggingFace), pandas, numpy

```python
def load_pwc_evaluation_tables() -> "datasets.Dataset": ...
def parse_triplets(ds) -> pd.DataFrame:  # columns: task, dataset, metric, paper_id, date
def filter_date_range(df: pd.DataFrame, start="2018-01-01", end="2024-12-31") -> pd.DataFrame: ...
def monthly_benchmark_counts(df: pd.DataFrame) -> pd.DataFrame:  # index=month, cols=dataset, values=count
def gini(array: np.ndarray) -> float: ...
def compute_monthly_gini_series(counts: pd.DataFrame) -> pd.Series:  # ~72 monthly values, index=dates
```

### `model.py`

**Dependencies**: scipy, ruptures, numpy

```python
class MonotonicTrendModel:  # H0 baseline
    def fit(self, t: np.ndarray, y: np.ndarray) -> "MonotonicTrendModel": ...
    def residuals(self) -> np.ndarray: ...
    def r_squared(self) -> float: ...

class GiniChangePointDetector:  # H1 proposed
    def __init__(self, model: str = "rbf", min_size: int = 3, target_window: tuple = (2019, 2022)): ...
    def detect(self, gini_series: np.ndarray, penalty: float = None) -> tuple:  # (change_points, target_hit)
    def fit_segmented_trends(self, t: np.ndarray, y: np.ndarray, change_points: list) -> list:  # per-segment residuals
```

### `evaluate.py`

**Dependencies**: model.py, scipy.stats, numpy

```python
def compute_bic(residuals: np.ndarray, n_params: int, n_samples: int) -> float: ...
def compare_models(bic_mono: float, bic_seg: float) -> dict:  # {"improvement": bool, "delta": float}
def check_target_window(change_points: list, dates: pd.DatetimeIndex, window=(2019, 2022)) -> list: ...
def run_gate_checks(gini_series, dates, change_points, bic_mono, bic_seg) -> dict:  # PASS/FAIL + reasons
```

### `visualize.py`

**Dependencies**: matplotlib, evaluate.py outputs

```python
def plot_gini_timeseries_with_changepoints(dates, gini_series, change_points, save_path): ...
def plot_segmented_vs_monotonic_fit(dates, gini_series, mono_pred, seg_pred, save_path): ...
def plot_gate_metrics_bar(gate_results: dict, save_path): ...
```

### `train.py` (orchestration, no gradient training)

**Dependencies**: data.py, model.py, evaluate.py, visualize.py, config.py

```python
def main(): ...  # load -> gini series -> fit both models -> gate check -> figures -> save results.json
```

### `config.py`

```python
PELT_MODEL = "rbf"
MIN_SEGMENT_SIZE = 3
TARGET_WINDOW = (2019, 2022)
DATE_START = "2018-01-01"
DATE_END = "2024-12-31"
ALPHA = 0.05
FIGURES_DIR = "figures/"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup config | config.py constants, folder structure | 4 | 1+1+1+1 |
| A-2 | Data loading | HF dataset load, triplet parsing, date filter | 10 | 3+3+2+2 |
| A-3 | Gini aggregation | monthly counts + Gini coefficient series (full 326k rows, ~72 monthly points) | 9 | 2+2+3+2 |
| A-4 | Baseline model | MonotonicTrendModel (scipy linregress + BIC) | 6 | 2+1+2+1 |
| A-5 | Proposed model | GiniChangePointDetector (PELT rbf + segmented trends) | 12 | 3+3+4+2 |
| A-6 | Evaluation/gates | BIC comparison, target-window check, gate PASS/FAIL | 8 | 2+2+2+2 |
| A-7 | Visualization | 3 required figures (timeseries+CPs, fit comparison, gate bar chart) | 7 | 2+1+2+2 |
| A-8 | Orchestration | train.py wiring all modules, results.json output | 6 | 1+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-5], Low(4-8): [A-1, A-4, A-6, A-7, A-8]

---

## Data Scale Note

Full `pwc-archive/evaluation-tables` dataset (~326,000 rows) processed — no subsampling. Output is naturally small (~72 monthly Gini values) as this is a monthly-aggregation time series, per PRD §4.
