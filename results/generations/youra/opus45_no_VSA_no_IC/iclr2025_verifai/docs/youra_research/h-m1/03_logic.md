# Logic: H-M1 (SA Metric Correlation with Functional Correctness)

**Type**: MECHANISM

**Applied**: Standard PyTorch/scipy patterns (KB search "correlation analysis API design" returned no relevant matches, similarity <0.35 — using scipy.stats/pingouin standard APIs)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: `h-e1/code/` does not exist on disk (spec-only). No actual API signatures to verify. Green-field implementation for correlate.py; sa_tools.py re-implemented fresh per H-E1 architecture spec (no code to call via Serena).
**Analyzed Path**: N/A (glob confirmed no `h-e1/code/` directory)
**Relevant Symbols**: None — new implementation, no external dependency APIs to verify

---

## M-7: Correlation Analysis [Complexity: 10, Budget: 10]

**Applied**: scipy.stats.pointbiserialr + pingouin.partial_corr (standard library APIs, documented signatures below)

### API Signatures

```python
# code/correlate.py
import pandas as pd
from scipy.stats import pointbiserialr
import pingouin as pg

def point_biserial(df: pd.DataFrame, metric: str) -> tuple[float, float]:
    """Raw point-biserial r between df['passed'] and df[metric]. Returns (r, p)."""
    ...

def partial_corr_loc(df: pd.DataFrame, metric: str) -> tuple[float, float]:
    """Partial correlation of metric vs passed, controlling for loc. Returns (r_partial, p_partial)."""
    ...

def compute_all_correlations(
    df: pd.DataFrame,
    metrics: list[str] = ["pylint_score", "mypy_errors", "radon_cc"],
) -> dict[str, dict[str, float]]:
    """Per-metric r_raw/p_raw/r_partial/p_partial. Returns {metric: {r_raw, p_raw, r_partial, p_partial}}."""
    ...

def determine_pass(
    results: dict[str, dict[str, float]],
    threshold: float = 0.35,
    alpha: float = 0.05,
) -> tuple[bool, str, float, float]:
    """Gate check: max |r_partial| >= threshold AND its p_partial < alpha.
    Returns (passed, best_metric, best_r, best_p)."""
    ...
```

### External Library Call Signatures (verified from scipy/pingouin public API)

```python
# scipy.stats.pointbiserialr(x, y) -> PointbiserialrResult(correlation: float, pvalue: float)
# x: binary array-like (0/1), y: continuous array-like
r, p = pointbiserialr(df["passed"], df[metric])

# pingouin.partial_corr(data, x, y, covar, method="pearson") -> pd.DataFrame
# columns: n, r, CI95%, p-val (indexed by method name row)
result_df = pg.partial_corr(data=df, x=metric, y="passed", covar="loc", method="pearson")
r_partial = result_df["r"].iloc[0]
p_partial = result_df["p-val"].iloc[0]
```

### Tensor/Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| df | pd.DataFrame, [N>=500, 6] | cols: task_id, passed(int 0/1), pylint_score, mypy_errors, radon_cc, loc |
| point_biserial return | (float, float) | (r in [-1,1], p in [0,1]) |
| partial_corr_loc return | (float, float) | (r_partial, p_partial) |
| compute_all_correlations return | dict[str, dict] | 3 metrics x {r_raw,p_raw,r_partial,p_partial} |

### Pseudo-code (correlation pipeline)

```
1. for metric in [pylint_score, mypy_errors, radon_cc]:
     r_raw, p_raw = point_biserial(df, metric)          # scipy pointbiserialr(passed, metric)
     r_partial, p_partial = partial_corr_loc(df, metric)  # pingouin partial_corr covar="loc"
     results[metric] = {r_raw, p_raw, r_partial, p_partial}
2. best_metric = argmax(|results[m].r_partial| for m in metrics)
3. passed = |results[best_metric].r_partial| >= 0.35 AND results[best_metric].p_partial < 0.05
4. return passed, best_metric, r, p
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M-7-1 | point_biserial | Wrap scipy.stats.pointbiserialr(df['passed'], df[metric]) |
| L-M-7-2 | partial_corr_loc | Wrap pg.partial_corr(data=df, x=metric, y='passed', covar='loc'); extract r/p-val row |
| L-M-7-3 | compute_all_correlations | Loop metrics, aggregate raw+partial results into dict |
| L-M-7-4 | determine_pass | argmax by \|r_partial\|, threshold+alpha gate check |

---

## M-9: Full Pipeline Run [Complexity: 9, Budget: 9]

**Applied**: Standard orchestration script (no KB pattern needed)

### API Signatures

```python
# code/run.py
def main() -> None:
    """Orchestrate full H-M1 pipeline: load -> eval -> metrics -> correlate -> write -> visualize."""
    ...

def write_results(
    df: pd.DataFrame,
    results: dict[str, dict[str, float]],
    gate_passed: bool,
    best_metric: str,
    results_dir: str = "results",
) -> None:
    """Write h_m1_data.csv, h_m1_correlations.json, h_m1_summary.json."""
    ...
```

### Pseudo-code

```
1. problems = load_all_problems()                          # -> 591 Problem
2. completions = load_completions_jsonl(path)                # or generate_completions
3. passed = evaluate_all(problems, completions)               # -> dict[task_id, bool]
4. df = build_dataframe(problems, completions, passed)         # -> DataFrame N>=500
5. assert len(df) >= 500                                       # NFR-1 gate
6. results = compute_all_correlations(df)
7. gate_passed, best_metric, r, p = determine_pass(results, threshold=0.35, alpha=0.05)
8. write_results(df, results, gate_passed, best_metric)
9. generate_all_figures(df, results)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M-9-1 | main() orchestration | Wire load->eval->metrics->correlate steps in sequence |
| L-M-9-2 | write_results | Serialize df to CSV, results/summary to JSON |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] KB search reported as 1-line "Applied" (no logs)
- [x] Docstrings <=2 lines
- [x] Tensor/data shapes in table + code comments
- [x] Subtask count within budget (6 total: 4+2)
- [x] Total length < 200 lines
- [x] Codebase Analysis (Serena) section included
