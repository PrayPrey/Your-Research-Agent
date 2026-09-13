# Logic: H-E1 (Model Zoo Dataset Validity)

**Type:** EXISTENCE (PoC) | Budget: 0 subtasks (all Epics Low complexity)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field, no existing code
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

**Applied**: Pure-function statistical validation pattern

---

## A-1: Data Loading [Complexity: 8]

**Applied**: HF-primary-with-fallback loader pattern

### API Signatures

```python
# data.py
import numpy as np

def load_accuracies() -> np.ndarray:
    """Load Model Zoo test_accuracy labels. HF primary, .pt fallback. Filters NaN, normalizes to [0,100]."""
    ...  # returns accuracies: [N] float32, N >= 500
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| accuracies | [N] | float32, N in [500, 10000], range [0,100] |

---

## A-2: Statistical Analysis [Complexity: 6]

**Applied**: Descriptive-stats + Shapiro-Wilk normality pattern

### API Signatures

```python
# analysis.py
import numpy as np

GATE_THRESHOLD: float = 10.0

def validate_model_zoo_variance(accuracies: np.ndarray) -> dict:
    """Compute mean/std/min/max/quartiles/IQR outliers/Shapiro-Wilk; gate_passed = std > 10.0."""
    ...
```

### Return dict schema

| Key | Type | Note |
|-----|------|------|
| n_samples | int | len(accuracies) |
| mean, std, min, max | float | descriptive stats |
| q1, q2, q3, iqr | float | quartiles |
| n_outliers | int | via 1.5*IQR rule |
| shapiro_stat, shapiro_p | float | on subset <=5000 |
| gate_passed | bool | std > GATE_THRESHOLD |

---

## A-3: Gate Validation & Reporting [Complexity: 4]

### API Signatures

```python
# analysis.py (cont.) or run.py
def report_gate(stats: dict) -> str:
    """Format PASS/FAIL message from stats dict."""
    ...

def save_results(stats: dict, out_path: str = "h-e1/results.json") -> None:
    """Dump stats dict to JSON."""
    ...
```

---

## A-4: Visualization [Complexity: 6]

**Applied**: Matplotlib-figure-per-view pattern

### API Signatures

```python
# visualize.py
import numpy as np

def plot_gate_comparison(stats: dict, out_dir: str) -> None:
    """Bar chart: observed std vs GATE_THRESHOLD. Saves out_dir/gate_comparison.png."""
    ...

def plot_histogram(accuracies: np.ndarray, stats: dict, out_dir: str) -> None:
    """Histogram of accuracies with mean/std annotations. Saves out_dir/histogram.png."""
    ...

def plot_boxplot(accuracies: np.ndarray, out_dir: str) -> None:
    """Boxplot with quartiles/outliers. Saves out_dir/boxplot.png."""
    ...
```

---

## A-5: End-to-End Run Script [Complexity: 5]

### API Signatures

```python
# run.py
def main() -> None:
    """load_accuracies -> validate_model_zoo_variance -> plot_* -> print PASS/FAIL -> save_results."""
    ...

if __name__ == "__main__":
    main()
```

### Pseudo-code

```
1. accuracies = load_accuracies()  # [N]
2. if load fails: print error, exit(1)
3. stats = validate_model_zoo_variance(accuracies)
4. plot_gate_comparison(stats, "h-e1/figures/")
5. plot_histogram(accuracies, stats, "h-e1/figures/")
6. plot_boxplot(accuracies, "h-e1/figures/")
7. print(report_gate(stats))
8. save_results(stats, "h-e1/results.json")
```

---

## No Subtasks

All Epics (A-1..A-5) are Low complexity (4-8); budget allocation is 0 subtasks per Epic — implement directly in Phase 4.
