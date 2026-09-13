# Architecture: H-M2

**Tier:** LIGHT (correlation analysis, CPU-only, ~1 min)
**Applied:** Benchmark comparison via correlation matrix + bootstrap CI (KB pattern)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no code to analyze. No `h-m2/code/` exists yet; H-M1's `data.py`/`analysis.py` are for a different (MI/probe) pipeline, not reusable here.
**Analyzed Path:** N/A
**Findings:** New implementation from scratch — single-script LIGHT tier, no external module reuse needed.

---

## Module Structure

### data.py (`h-m2/code/data.py`)

**Dependencies**: pandas

```python
def load_model_scores(csv_path: str) -> pd.DataFrame: ...
def validate_columns(df: pd.DataFrame, required: list[str]) -> None: ...  # raises ValueError
```

### correlations.py (`h-m2/code/correlations.py`)

**Dependencies**: numpy, scipy, data.py

```python
def compute_halueval_correlations(
    model_scores: pd.DataFrame,
    truthfulqa_col: str = "truthfulqa_mc2",
    halueval_cols: list[str] = ["halueval_qa", "halueval_dialogue", "halueval_summarization"],
) -> dict[str, tuple[float, float]]: ...  # name -> (r, p)

def bootstrap_ci(x: np.ndarray, y: np.ndarray, n_bootstrap: int = 1000, ci: float = 0.95, seed: int = 42) -> tuple[float, float]: ...

def check_gate(results: dict[str, tuple[float, float]], threshold: float = 0.7) -> dict: ...
```

### visualize.py (`h-m2/code/visualize.py`)

**Dependencies**: matplotlib, seaborn, correlations.py

```python
def plot_correlation_heatmap(model_scores: pd.DataFrame, cols: list[str], out_path: str) -> None: ...
def plot_scatter(model_scores: pd.DataFrame, x_col: str, y_col: str, r: float, out_path: str) -> None: ...
def plot_gate_metrics(r_cross: float, threshold: float, out_path: str) -> None: ...
```

### report.py (`h-m2/code/report.py`)

**Dependencies**: correlations.py

```python
def write_validation_report(results: dict, gate: dict, out_path: str) -> None: ...
```

### run_experiment.py (`h-m2/code/run_experiment.py`)

**Dependencies**: all above (entry point, no class — linear script)

```python
def main() -> None: ...
```

---

## Data Flow

1. `run_experiment.py` calls `data.load_model_scores()` → loads `h-m1/model_scores.csv` (or fallback CSV), `validate_columns()` checks required columns exist
2. `correlations.compute_halueval_correlations()` → Spearman r for cross-benchmark + intra-HaluEval pairs
3. `correlations.bootstrap_ci()` → 95% CI on primary r(HaluEval_agg, TruthfulQA)
4. `correlations.check_gate()` → PASS/FAIL against r < 0.7 threshold
5. `visualize.*()` → 3 PNGs written to `h-m2/figures/`
6. `report.write_validation_report()` → `h-m2/04_validation.md`

---

## File Structure

```
h-m2/
  code/
    data.py
    correlations.py
    visualize.py
    report.py
    run_experiment.py
  figures/
    correlation_heatmap.png
    scatter_halueval_truthfulqa.png
    gate_metrics.png
  04_validation.md
```

---

## Error Handling

- Missing CSV / missing required columns → `validate_columns()` raises `ValueError` with column list, caught in `main()`, logs and exits non-zero (no silent fallback — data correctness is required for a stats result).
- If `h-m1/model_scores.csv` lacks HaluEval columns → fallback per PRD: raise `FileNotFoundError`-style message pointing to lm-eval-harness fallback path (out of scope to auto-run).
- All correlation/bootstrap functions guard `n < 3` → return `(0.0, 1.0)` / `(-1.0, 1.0)` rather than crashing on degenerate input (mirrors H-E1 pattern).
- No GPU/model-loading failure modes — CPU-only stats, so no OOM/device handling needed.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Data loading | `data.py` load + column validation | 5 | 1+1+1+2 |
| M2-2 | Correlation core | `compute_halueval_correlations` (cross + intra) | 7 | 2+1+2+2 |
| M2-3 | Bootstrap CI | `bootstrap_ci` implementation | 5 | 1+1+2+1 |
| M2-4 | Gate check | `check_gate` PASS/FAIL logic | 4 | 1+1+1+1 |
| M2-5 | Visualization | heatmap, scatter, gate bar chart | 8 | 2+2+2+2 |
| M2-6 | Report writer | `04_validation.md` generation | 5 | 1+1+2+1 |
| M2-7 | Entry point + wiring | `run_experiment.py` main() | 6 | 1+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M2-1, M2-2, M2-3, M2-4, M2-5, M2-6, M2-7]

---

## External Dependencies

None — no base hypothesis code reuse. H-M2 reads H-M1's output CSV (`h-m1/model_scores.csv`) as a data file only, not as an imported module.
