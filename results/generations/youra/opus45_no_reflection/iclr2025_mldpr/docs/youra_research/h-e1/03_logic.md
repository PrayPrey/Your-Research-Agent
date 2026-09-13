# Logic: H-E1 (EXISTENCE / PoC)

**Applied**: Standard PyData stack (pandas/scipy/ruptures) — no DL framework needed, this is statistical time-series analysis, not a neural model. Confirmed via KB search: no relevant time-series/change-point patterns indexed (only diffusers repo content, similarity <0.41, irrelevant).

## Codebase Analysis (Serena)

**Project Type**: Green-field
**Status**: Green-field project — no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2/A-3: Data Loading & Gini Aggregation [Complexity: 19, Budget: 4]

### API Signatures

```python
# data.py
import pandas as pd
import numpy as np
from datasets import Dataset

def load_pwc_evaluation_tables() -> Dataset:
    """Load pwc-archive/evaluation-tables from HuggingFace."""
    ...

def parse_triplets(ds: Dataset) -> pd.DataFrame:
    """Flatten nested eval-table rows to task/dataset/metric/paper_id/date columns."""
    ...  # returns DataFrame[task, dataset, metric, paper_id, date]

def filter_date_range(
    df: pd.DataFrame, start: str = "2018-01-01", end: str = "2024-12-31"
) -> pd.DataFrame: ...

def monthly_benchmark_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot to monthly usage counts per dataset."""
    ...  # index=month (DatetimeIndex, ~72), columns=dataset, values=count

def gini(array: np.ndarray) -> float:
    """Gini coefficient of a 1D non-negative array."""
    ...

def compute_monthly_gini_series(counts: pd.DataFrame) -> pd.Series:
    """Apply gini() row-wise across monthly counts."""
    ...  # index=month (~72), values=float in [0,1]
```

### Pseudo-code (Gini computation — non-trivial)

```
gini(x):
    x = sort(x)
    n = len(x)
    cumx = cumsum(x)
    return (n + 1 - 2 * sum(cumx) / cumx[-1]) / n
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| parse_triplets output | [~326000, 5] | raw rows |
| monthly_benchmark_counts | [~72, n_datasets] | pivoted |
| compute_monthly_gini_series | [~72] | final input to models |

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Load + parse | load_pwc_evaluation_tables, parse_triplets, filter_date_range |
| L-2-2 | Gini series | monthly_benchmark_counts, gini, compute_monthly_gini_series |

---

## A-4/A-5: Baseline & Proposed Models [Complexity: 18, Budget: 4]

### API Signatures

```python
# model.py
from scipy import stats
import ruptures as rpt
import numpy as np

class MonotonicTrendModel:
    """H0: single linear trend over full series."""

    def fit(self, t: np.ndarray, y: np.ndarray) -> "MonotonicTrendModel":
        # t: [T] month index 0..71, y: [T] gini values
        ...

    def residuals(self) -> np.ndarray: ...  # [T]
    def r_squared(self) -> float: ...


class GiniChangePointDetector:
    """H1: PELT segmented trend."""

    def __init__(
        self,
        model: str = "rbf",
        min_size: int = 3,
        target_window: tuple[int, int] = (2019, 2022),
    ): ...

    def detect(
        self, gini_series: np.ndarray, penalty: float | None = None
    ) -> tuple[list[int], bool]:
        """PELT change-point detection. penalty defaults to log(n)*var(signal)."""
        ...  # returns (change_points: list[int] breakpoint indices, target_hit: bool)

    def fit_segmented_trends(
        self, t: np.ndarray, y: np.ndarray, change_points: list[int]
    ) -> list[np.ndarray]:
        """Fit linear trend per segment defined by change_points."""
        ...  # returns list of per-segment residual arrays
```

### Pseudo-code (PELT penalty + detect — non-trivial)

```
detect(gini_series, penalty=None):
    n = len(gini_series)
    if penalty is None:
        penalty = log(n) * var(gini_series)
    algo = rpt.Pelt(model=self.model, min_size=self.min_size).fit(gini_series)
    change_points = algo.predict(pen=penalty)[:-1]  # drop trailing n
    target_hit = any(idx in index_range_for(target_window) for idx in change_points)
    return change_points, target_hit
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| t, y | [72] | month index, gini values |
| change_points | [k] | k = num detected breakpoints, usually 1-3 |
| fit_segmented_trends output | list of [seg_len] | ragged, sums to 72 |

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Models | MonotonicTrendModel + GiniChangePointDetector (detect + fit_segmented_trends) |

---

## A-6: Evaluation/Gates [Complexity: 8, Budget: 4]

### API Signatures

```python
# evaluate.py
import numpy as np
import pandas as pd

def compute_bic(residuals: np.ndarray, n_params: int, n_samples: int) -> float:
    """BIC = n*log(RSS/n) + n_params*log(n)."""
    ...

def compare_models(bic_mono: float, bic_seg: float) -> dict:
    ...  # {"improvement": bool, "delta": float}  # delta = bic_mono - bic_seg

def check_target_window(
    change_points: list[int], dates: pd.DatetimeIndex, window: tuple[int, int] = (2019, 2022)
) -> list[int]:
    """Filter change_points whose date.year falls in [window[0], window[1]]."""
    ...

def run_gate_checks(
    gini_series: np.ndarray,
    dates: pd.DatetimeIndex,
    change_points: list[int],
    bic_mono: float,
    bic_seg: float,
) -> dict:
    """Aggregate PASS/FAIL for all success criteria."""
    ...  # {"cp_in_window": bool, "bic_improved": bool, "overall": "PASS"|"FAIL", "reasons": [...]}
```

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Gates | compute_bic, compare_models, check_target_window, run_gate_checks |

---

## A-7/A-8: Visualization & Orchestration [Complexity: 13, Budget: 4]

### API Signatures

```python
# visualize.py
def plot_gini_timeseries_with_changepoints(
    dates: pd.DatetimeIndex, gini_series: np.ndarray, change_points: list[int], save_path: str
) -> None: ...

def plot_segmented_vs_monotonic_fit(
    dates: pd.DatetimeIndex,
    gini_series: np.ndarray,
    mono_pred: np.ndarray,
    seg_pred: np.ndarray,
    save_path: str,
) -> None: ...  # mono_pred, seg_pred: [72]

def plot_gate_metrics_bar(gate_results: dict, save_path: str) -> None: ...


# train.py
def main() -> None:
    """load -> gini series -> fit both models -> gate check -> figures -> save results.json"""
    ...
```

### Pseudo-code (orchestration flow)

```
main():
    df = filter_date_range(parse_triplets(load_pwc_evaluation_tables()))
    counts = monthly_benchmark_counts(df)
    gini_series = compute_monthly_gini_series(counts)  # [72]
    t = arange(len(gini_series))

    mono = MonotonicTrendModel().fit(t, gini_series.values)
    bic_mono = compute_bic(mono.residuals(), n_params=2, n_samples=len(t))

    det = GiniChangePointDetector()
    cps, target_hit = det.detect(gini_series.values)
    seg_residuals = det.fit_segmented_trends(t, gini_series.values, cps)
    bic_seg = compute_bic(concatenate(seg_residuals), n_params=2*len(cps+1), n_samples=len(t))

    gates = run_gate_checks(gini_series.values, gini_series.index, cps, bic_mono, bic_seg)

    plot_gini_timeseries_with_changepoints(...)
    plot_segmented_vs_monotonic_fit(...)
    plot_gate_metrics_bar(gates, ...)
    save results.json {gates, bic_mono, bic_seg, cps, target_hit}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Timeseries + fit plots | plot_gini_timeseries_with_changepoints, plot_segmented_vs_monotonic_fit |
| L-7-2 | Gate bar plot | plot_gate_metrics_bar |
| L-8-1 | train.py wiring | main() orchestration per pseudo-code above |
| L-8-2 | results.json output | serialize gates/bic/cps/target_hit |
