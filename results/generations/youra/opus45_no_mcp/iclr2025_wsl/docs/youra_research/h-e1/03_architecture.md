# Architecture: H-E1 (Model Zoo Dataset Validity)

**Type:** EXISTENCE (PoC) | **Applied:** Pure-function statistical validation pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project, no existing code
**Analyzed Path**: N/A
**Findings**: New implementation from scratch — no base hypothesis, no existing codebase.

---

## Module Structure

### data.py (`h-e1/code/data.py`)

**Dependencies**: datasets (HuggingFace), numpy, torch (fallback)

```python
def load_accuracies() -> np.ndarray:
    """Load Model Zoo test_accuracy labels. Tries HF, falls back to direct .pt download.
    Filters NaN/corrupted entries, normalizes to [0,100]."""
    ...
```

### analysis.py (`h-e1/code/analysis.py`)

**Dependencies**: numpy, scipy.stats

```python
def validate_model_zoo_variance(accuracies: np.ndarray) -> dict:
    """Compute mean/std/min/max/quartiles/IQR outliers/Shapiro-Wilk, gate_passed = std>10.0"""
    ...
```

### visualize.py (`h-e1/code/visualize.py`)

**Dependencies**: matplotlib, analysis.py output dict

```python
def plot_gate_comparison(stats: dict, out_dir: str) -> None: ...
def plot_histogram(accuracies: np.ndarray, stats: dict, out_dir: str) -> None: ...
def plot_boxplot(accuracies: np.ndarray, out_dir: str) -> None: ...
```

### run.py (`h-e1/code/run.py`)

**Dependencies**: data.py, analysis.py, visualize.py

```python
def main() -> None:
    """Load -> validate -> plot -> print PASS/FAIL + save results.json"""
    ...
```

---

## File Organization

```
h-e1/code/
  data.py
  analysis.py
  visualize.py
  run.py
h-e1/figures/        # output plots
h-e1/results.json     # gate stats output
```

No config.py needed — single fixed threshold (10.0) hardcoded in analysis.py per PRD.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Implement `load_accuracies()`, HF primary + .pt fallback, NaN filtering | 8 | 3+2+2+1 |
| A-2 | Statistical analysis | Implement `validate_model_zoo_variance()` incl. Shapiro-Wilk, IQR outliers | 6 | 2+1+2+1 |
| A-3 | Gate validation & reporting | Wire gate_passed check, print/log PASS-FAIL, save results.json | 4 | 1+1+1+1 |
| A-4 | Visualization | Implement 3 plots (gate bar chart, histogram, boxplot) to figures/ | 6 | 2+1+1+2 |
| A-5 | End-to-end run script | `run.py` wiring all modules, error handling for load failures | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5]
