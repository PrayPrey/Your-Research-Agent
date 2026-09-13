# Logic: H-M2 (Weighted Ensemble SA Metric Correlation)

**Applied**: weighted-linear-combination-with-grid-search-fit (no domain-relevant KB hits — irrelevant diffusion/LoRA results returned for "weighted ensemble correlation optimization")

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: API signatures verified from actual h-m1 code (Serena unavailable for this path; used Read tool directly, per architecture doc's documented fallback).
**Analyzed Path**: `docs/youra_research/h-m1/code/correlate.py`
**Relevant Symbols**: `partial_corr_loc(df, metric) -> tuple[float, float]` — uses `pg.partial_corr(data=df, x=metric, y="passed", covar="loc", method="pearson")`, returns `(result["r"].iloc[0], result["p_val"].iloc[0])`. Column names confirmed: `passed`, `loc` (not `pass_at_1`/PRD's assumed names).

---

## A-1..A-8: All Epics [Complexity: Low, Budget: 0 subtasks each]

All 8 epics are Low complexity (4-8) per architecture — no further subtask breakdown needed.

### API Signatures

```python
# config.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    h_m1_data_path: str = "../h-m1/results/h_m1_data.csv"
    results_dir: str = "results"
    figures_dir: str = "figures"
    weight_grid_step: float = 0.1
    weight_min: float = 0.1
    weight_max: float = 0.9
    max_r_individual: float = 0.873
    alpha: float = 0.05
    seed: int = 42

CONFIG = Config()


# data_loader.py
import pandas as pd

def load_h_m1_data(path: str = None) -> pd.DataFrame:
    """Load h-m1 results CSV; validate required columns + N=591."""
    ...  # required cols: passed, pylint_score, radon_cc, loc


# ensemble.py
import pandas as pd

def normalize_minmax(series: pd.Series) -> pd.Series:
    """(x - min) / (max - min)."""
    ...

def compute_ensemble_score(
    df: pd.DataFrame,
    weights: dict[str, float],   # {"pylint_score": w, "radon_cc": 1-w}
    metrics: list[str] = ["pylint_score", "radon_cc"],
) -> pd.DataFrame:
    """Adds 'ensemble' column = sum(weights[m] * normalize_minmax(df[m])). Preserves originals."""
    ...


# correlate.py
import pandas as pd
import pingouin as pg

def partial_corr_loc(df: pd.DataFrame, metric: str) -> tuple[float, float]:
    """Reuses h-m1 pattern exactly. Returns (r, p)."""
    result = pg.partial_corr(data=df, x=metric, y="passed", covar="loc", method="pearson")
    return float(result["r"].iloc[0]), float(result["p_val"].iloc[0])


# optimize.py
def grid_search_weights(
    df: pd.DataFrame,
    metrics: list[str] = ["pylint_score", "radon_cc"],
) -> tuple[dict[str, float], float, float]:
    """Grid search w_pylint in [0.1,0.9] step 0.1; w_radon=1-w_pylint. Returns (best_weights, best_r, best_p)."""
    ...


# visualize.py
def plot_gate_comparison(r_ensemble: float, r_individual_max: float, out_path: str) -> None: ...
def plot_weight_sensitivity(weight_r_pairs: list[tuple[float, float]], out_path: str) -> None: ...
def generate_all_figures(df: pd.DataFrame, best_weights: dict, best_r: float, r_max_individual: float) -> None: ...


# run.py
def main() -> None: ...
```

### Tensor Shapes / Data Shapes (non-obvious only)

| Variable | Shape/Type | Note |
|----------|-----------|------|
| df | DataFrame [591, ...] | passed, pylint_score, radon_cc, loc |
| weights | dict[str, float] | {"pylint_score": w, "radon_cc": 1-w}, w in [0.1,0.9] |
| weight_r_pairs | list[(float, float)] | (w_pylint, r) for sensitivity curve, len=9 |

### Pseudo-code: grid_search_weights (only non-trivial algorithm)

```
best_r, best_p, best_weights = None, None, None
weight_r_pairs = []
for w in arange(0.1, 0.9+step, 0.1):
    weights = {"pylint_score": w, "radon_cc": 1 - w}
    df_e = compute_ensemble_score(df, weights)
    r, p = partial_corr_loc(df_e, "ensemble")
    weight_r_pairs.append((w, r))
    if best_r is None or abs(r) > abs(best_r):
        best_r, best_p, best_weights = r, p, weights
return best_weights, best_r, best_p  # also stash weight_r_pairs for visualize.py
```

### Pseudo-code: run.py main() (orchestration only)

```
1. df = load_h_m1_data(CONFIG.h_m1_data_path)
2. best_weights, best_r, best_p = grid_search_weights(df)
3. gate = best_r > CONFIG.max_r_individual and best_p < CONFIG.alpha
4. write results/h_m2_ensemble.json {best_weights, best_r, best_p, gate}
5. write results/h_m2_data.csv (df + ensemble column at best_weights)
6. write results/h_m2_summary.json
7. generate_all_figures(df, best_weights, best_r, CONFIG.max_r_individual)
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: docs/youra_research/h-m1/code/correlate.py (ACTUAL CODE)
def partial_corr_loc(df: pd.DataFrame, metric: str) -> tuple[float, float]:
    """pg.partial_corr(data=df, x=metric, y='passed', covar='loc', method='pearson')."""
    result = pg.partial_corr(data=df, x=metric, y="passed", covar="loc", method="pearson")
    return float(result["r"].iloc[0]), float(result["p_val"].iloc[0])
```

**Verified from**: `docs/youra_research/h-m1/code/correlate.py` (actual implementation, not PRD which references non-existent `data/sa_metrics_combined.csv` and `pass_at_1` column).

**Note**: h-m2 does not import h-m1 code directly — it reimplements `partial_corr_loc` locally with the `ensemble` column, using identical column names (`passed`, `loc`) and result field (`p_val`) confirmed above.

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Applied line included (1 line)
- [x] Docstrings <= 2 lines
- [x] Tensor/data shapes in comments + table for non-obvious cases only
- [x] 0 subtasks (all Low complexity, matches budget)
- [x] Codebase Analysis (Serena) section included
- [x] External Dependencies API section with verified h-m1 signature
- [x] Total length < 200 lines
