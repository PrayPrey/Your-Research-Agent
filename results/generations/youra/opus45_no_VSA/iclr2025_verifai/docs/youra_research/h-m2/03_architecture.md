# Architecture: h-m2

**Type**: MECHANISM (statistical log analysis, no neural network)
Applied: no matching KB pattern found — standard script pipeline used.

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze (h-e1 folder is a data source only: `h-e1/code/results/h-e1_iteration_logs.jsonl`, not a code dependency)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure

- `h-m2/code/data_loader.py`
- `h-m2/code/metrics.py`
- `h-m2/code/stats_test.py`
- `h-m2/code/visualize.py`
- `h-m2/code/run_analysis.py` (entrypoint)
- `h-m2/code/results/` (output: JSON metrics)
- `h-m2/figures/` (output: PNGs)

---

## Modules

### data_loader (`h-m2/code/data_loader.py`)

**Dependencies**: none

```python
def load_iteration_logs(path: str) -> list[dict]: ...
def filter_by_condition(logs: list[dict], condition: str) -> list[dict]: ...
```

### metrics (`h-m2/code/metrics.py`)

**Dependencies**: none

```python
def compute_regression_rate(logs: list[dict], condition: str) -> float: ...
def per_iteration_pass_rate(logs: list[dict], condition: str) -> dict[str, float]: ...
def build_regression_contingency_table(logs: list[dict]) -> list[list[int]]: ...
```

### stats_test (`h-m2/code/stats_test.py`)

**Dependencies**: metrics

```python
def run_mcnemar(table: list[list[int]], exact: bool = True) -> tuple[float, float]: ...
def verify_mechanism_h_m2(cascade_rate: float, reverse_rate: float, p_value: float) -> str: ...
```

### visualize (`h-m2/code/visualize.py`)

**Dependencies**: none

```python
def plot_regression_bar(cascade_rate: float, reverse_rate: float, out_path: str) -> None: ...
def plot_iteration_trajectory(rates_by_condition: dict[str, dict[str, float]], out_path: str) -> None: ...
def plot_contingency_heatmap(table: list[list[int]], out_path: str) -> None: ...
```

### run_analysis (`h-m2/code/run_analysis.py`)

**Dependencies**: data_loader, metrics, stats_test, visualize

```python
def main() -> None: ...
# loads logs -> computes rates -> mcnemar test -> verify -> save JSON + figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loader | JSONL load + condition filter | 4 | 1+1+1+1 |
| A-2 | Regression metrics | compute_regression_rate + per-iteration pass rate | 6 | 2+1+2+1 |
| A-3 | Contingency table | Build 2x2 table for McNemar input | 5 | 2+1+2+0 |
| A-4 | McNemar test | statsmodels exact test wrapper | 4 | 1+2+1+0 |
| A-5 | Mechanism verification | PASS/PARTIAL/FAIL logic + logging | 3 | 1+1+1+0 |
| A-6 | Visualization | 3 figures (bar, trajectory, heatmap) | 6 | 2+1+1+2 |
| A-7 | Pipeline entrypoint | Wire modules, save results JSON | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7]

---

## Dependencies

`statsmodels`, `numpy`, `pandas`, `matplotlib`, `seaborn`, `pyyaml` (per PRD section 7.1).
