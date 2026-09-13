# Architecture: H-M2 (Weighted Ensemble SA Metric Correlation)

**Type**: MECHANISM | **Gate**: SHOULD_WORK

Applied: weighted-linear-combination-with-grid-search-fit (refactor-arena/sktime pattern per experiment brief; KB search returned no domain-relevant hits — irrelevant diffusion/adapter results)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: Actual code inspected directly (Serena tool unavailable — no active project registered for this path; used Read/Glob instead, per fallback). h-m1 code confirmed at `docs/youra_research/h-m1/code/`.
**Analyzed Path**: `docs/youra_research/h-m1/code/correlate.py`, `config.py`, `run.py`
**Findings**: **PRD/brief path is WRONG.** PRD says load `../h-m1/data/sa_metrics_combined.csv` — this file does not exist. Actual h-m1 output is `../h-m1/results/h_m1_data.csv` (written by `run.py`), with columns `passed` (not `pass_at_1`), `pylint_score`, `mypy_errors`, `radon_cc`, `loc`. Correlation uses `pg.partial_corr(..., y="passed", covar="loc", method="pearson")` and result column is `p_val` (not `p-val` as brief's pseudo-code assumes). H-M2 must reuse these exact column/function conventions.

---

## File Structure

- `code/config.py` - fixed config (paths, thresholds, weight grid)
- `code/data_loader.py` - load h-m1 results CSV
- `code/ensemble.py` - normalization + weighted ensemble score computation
- `code/optimize.py` - grid search over weights, select best by |r|
- `code/correlate.py` - partial correlation wrapper (reuses h-m1 pattern)
- `code/visualize.py` - bar chart + weight sensitivity curve
- `code/run.py` - main pipeline orchestration
- `requirements.txt` - scipy, pingouin, pandas, numpy, matplotlib

---

## Module Interfaces

### config.py

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    h_m1_data_path: str = "../h-m1/results/h_m1_data.csv"
    results_dir: str = "results"
    figures_dir: str = "figures"
    weight_grid_step: float = 0.1
    weight_min: float = 0.1
    weight_max: float = 0.9
    max_r_individual: float = 0.873  # pylint, from h-m1
    alpha: float = 0.05
    seed: int = 42

CONFIG = Config()
```

### data_loader.py (`code/data_loader.py`)

**Dependencies**: config, pandas

```python
import pandas as pd

def load_h_m1_data(path: str = None) -> pd.DataFrame: ...
# columns required: passed, pylint_score, radon_cc, loc
```

### ensemble.py (`code/ensemble.py`)

**Dependencies**: pandas

```python
import pandas as pd

def normalize_minmax(series: "pd.Series") -> "pd.Series": ...
def compute_ensemble_score(
    df: pd.DataFrame,
    weights: dict[str, float],
    metrics: list[str] = ["pylint_score", "radon_cc"],
) -> pd.DataFrame: ...  # adds 'ensemble' column, preserves originals
```

### correlate.py (`code/correlate.py`)

**Dependencies**: pingouin, config

```python
import pandas as pd

def partial_corr_loc(df: pd.DataFrame, metric: str) -> tuple[float, float]: ...
# reuses h-m1 pattern: pg.partial_corr(data=df, x=metric, y="passed", covar="loc", method="pearson")
# returns (r, p) from result["r"].iloc[0], result["p_val"].iloc[0]
```

### optimize.py (`code/optimize.py`)

**Dependencies**: ensemble, correlate, numpy, config

```python
def grid_search_weights(
    df,
    metrics: list[str] = ["pylint_score", "radon_cc"],
) -> tuple[dict[str, float], float, float]: ...  # best_weights, best_r, best_p
```

### visualize.py (`code/visualize.py`)

**Dependencies**: matplotlib, config

```python
def plot_gate_comparison(r_ensemble: float, r_individual_max: float, out_path: str) -> None: ...
def plot_weight_sensitivity(weight_r_pairs: list[tuple[float, float]], out_path: str) -> None: ...
def generate_all_figures(df, best_weights: dict, best_r: float, r_max_individual: float) -> None: ...
```

### run.py (`code/run.py`)

**Dependencies**: all modules above, json

```python
def main() -> None: ...
# 1. load_h_m1_data -> df (591 rows expected)
# 2. grid_search_weights -> best_weights, best_r, best_p
# 3. gate: best_r > CONFIG.max_r_individual and best_p < CONFIG.alpha
# 4. write results/h_m2_ensemble.json, h_m2_data.csv, h_m2_summary.json
# 5. generate_all_figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Setup & config | Project skeleton, requirements.txt, config.py with correct h-m1 path | 4 | 1+1+1+1 |
| E-2 | Data loading | Load h-m1 results CSV, validate columns/N=591 | 5 | 1+2+1+1 |
| E-3 | Normalization + ensemble scoring | Min-max normalize, weighted combination function | 6 | 2+1+2+1 |
| E-4 | Partial correlation module | Reuse h-m1 pg.partial_corr pattern for ensemble column | 5 | 1+2+1+1 |
| E-5 | Grid search weight optimization | Loop w_pylint in [0.1,0.9] step 0.1, select best abs(r) | 8 | 2+2+3+1 |
| E-6 | Gate evaluation & result writing | Compare r_ensemble vs 0.873, write JSON/CSV outputs | 6 | 1+2+1+2 |
| E-7 | Visualization | Bar chart (gate comparison) + weight sensitivity curve | 5 | 1+1+1+2 |
| E-8 | Full pipeline run | Orchestrate run.py, verify gate condition end-to-end | 7 | 1+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [E-1, E-2, E-3, E-4, E-5, E-6, E-7, E-8]

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| h-m1 dataset (CSV) | `pd.read_csv("../h-m1/results/h_m1_data.csv")` | `h-m1/results/h_m1_data.csv` (generated by h-m1 run.py, not present at spec time — must run h-m1 first or use as-is if already generated) |
| correlate pattern | conceptual reuse only (no direct import — h-m2 reimplements with 'ensemble' column) | `h-m1/code/correlate.py` |

**Verified from**: `docs/youra_research/h-m1/code/correlate.py`, `config.py`, `run.py` (actual implementation, not PRD/brief specs which reference a non-existent `data/sa_metrics_combined.csv`)

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (Applied line only)
- [x] Interface-only module code
- [x] 8 Epic tasks (within 6-12 MECHANISM range) with complexity
- [x] Codebase Analysis (Serena) section included — path/column discrepancy flagged
- [x] Total length < 500 lines
