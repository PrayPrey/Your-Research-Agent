# Architecture: H-M3

**Tier:** LIGHT (correlation + PCA analysis, CPU-only, ~1 min)
**Applied:** Benchmark comparison via correlation matrix + bootstrap CI (KB pattern, reused from H-M2) — no closer KB match found for 3-way PCA distinctness pattern.

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no code to analyze. `h-m2/code/` does not exist on disk (H-M2 spec references it but was never materialized); H-M3 will read `h-m2/model_scores.csv` as a plain data file only, not as an imported module.
**Analyzed Path:** `h-m2/code/` (checked, not found)
**Findings:** New implementation from scratch, single-script LIGHT tier extending H-M2's pattern (add FactScore column + PCA).

---

## Module Structure

### data.py (`h-m3/code/data.py`)

**Dependencies**: pandas

```python
def load_base_scores(csv_path: str) -> pd.DataFrame: ...
def load_factscore(csv_path: str) -> pd.DataFrame: ...  # or synth fallback if unavailable
def merge_scores(base_df: pd.DataFrame, factscore_df: pd.DataFrame) -> pd.DataFrame: ...
def validate_columns(df: pd.DataFrame, required: list[str]) -> None: ...  # raises ValueError
```

### correlations.py (`h-m3/code/correlations.py`)

**Dependencies**: numpy, scipy, data.py

```python
def compute_factscore_correlations(
    model_scores: pd.DataFrame,
    factscore_col: str = "factscore",
    truthfulqa_col: str = "truthfulqa_mc2",
    halueval_col: str = "halueval_agg",
) -> dict[str, tuple[float, float]]: ...  # name -> (r, p)

def bootstrap_ci(x: np.ndarray, y: np.ndarray, n_bootstrap: int = 1000, ci: float = 0.95, seed: int = 42) -> tuple[float, float]: ...

def check_gate(results: dict[str, tuple[float, float]], threshold: float = 0.7) -> dict: ...  # PASS/PARTIAL/FAIL
```

### pca.py (`h-m3/code/pca.py`)

**Dependencies**: numpy, sklearn.decomposition, data.py

```python
def run_pca_analysis(
    model_scores: pd.DataFrame,
    benchmark_cols: list[str] = ["factscore", "truthfulqa_mc2", "halueval_agg"],
) -> dict: ...  # {loadings, explained_variance, n_components_80pct}
```

### visualize.py (`h-m3/code/visualize.py`)

**Dependencies**: matplotlib, seaborn, correlations.py, pca.py

```python
def plot_gate_metrics(r_fs_tqa: float, r_fs_he: float, threshold: float, out_path: str) -> None: ...
def plot_correlation_heatmap(model_scores: pd.DataFrame, cols: list[str], out_path: str) -> None: ...
def plot_pca_biplot(model_scores: pd.DataFrame, pca_result: dict, cols: list[str], out_path: str) -> None: ...
def plot_scatter_matrix(model_scores: pd.DataFrame, cols: list[str], out_path: str) -> None: ...
def plot_cumulative_variance(pca_result: dict, out_path: str) -> None: ...
```

### report.py (`h-m3/code/report.py`)

**Dependencies**: correlations.py, pca.py

```python
def verify_mechanism_activation(results: dict) -> dict: ...  # per PRD FR-6.2
def write_validation_report(results: dict, gate: dict, pca_result: dict, out_path: str) -> None: ...
```

### run_experiment.py (`h-m3/code/run_experiment.py`)

**Dependencies**: all above (entry point, no class — linear script)

```python
def main() -> None: ...
```

---

## Data Flow

1. `run_experiment.py` calls `data.load_base_scores()` on `h-m2/model_scores.csv`, `data.load_factscore()` on FactScore results (leaderboard CSV or computed subset), `validate_columns()` guards required columns
2. `data.merge_scores()` → unified DataFrame, saved to `h-m3/model_scores.csv`
3. `correlations.compute_factscore_correlations()` → r(FS,TQA), r(FS,HE), r(TQA,HE) reference
4. `correlations.bootstrap_ci()` → 95% CI for each of the 3 pairs
5. `correlations.check_gate()` → PASS/PARTIAL/FAIL vs 0.7 threshold
6. `pca.run_pca_analysis()` → standardize, fit 3-component PCA, loadings + explained variance + components-for-80%
7. `visualize.*()` → 5 PNGs written to `h-m3/figures/`
8. `report.verify_mechanism_activation()` + `report.write_validation_report()` → `h-m3/04_validation.md`

---

## File Structure

```
h-m3/
  code/
    data.py
    correlations.py
    pca.py
    visualize.py
    report.py
    run_experiment.py
  figures/
    gate_metrics.png
    correlation_heatmap.png
    pca_biplot.png
    scatter_matrix.png
    cumulative_variance.png
  model_scores.csv
  correlation_results.json
  pca_results.json
  04_validation.md
```

---

## Error Handling

- Missing CSV / missing required columns → `validate_columns()` raises `ValueError` listing missing columns, caught in `main()`, logs and exits non-zero.
- FactScore data unavailable (per PRD risk) → `load_factscore()` falls back to a documented subset/proxy CSV path; if none exists, raises `FileNotFoundError` with guidance to run FactScore subset eval (out of scope to auto-run per NFR-1).
- Model population mismatch (H-M2 models vs FactScore models) → `merge_scores()` does inner join, logs N models retained; if N < 10, warn in report per NFR-2 (reproducibility/quality flag).
- All correlation/bootstrap/PCA functions guard `n < 3` → return degenerate defaults `(0.0, 1.0)` rather than crashing (H-M2 pattern).
- PCA guards `n_components > n_features` by capping at `min(3, len(benchmark_cols))`.
- No GPU/model-loading failure modes — CPU-only stats/PCA.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Data loading + merge | `data.py` load base/factscore, validate, merge | 6 | 2+1+1+2 |
| M3-2 | Correlation core | `compute_factscore_correlations` (3 pairs) | 6 | 1+1+2+2 |
| M3-3 | Bootstrap CI | `bootstrap_ci` for 3 pairs | 5 | 1+1+2+1 |
| M3-4 | Gate check | `check_gate` PASS/PARTIAL/FAIL logic | 5 | 1+1+2+1 |
| M3-5 | PCA analysis | `run_pca_analysis` standardize+fit+loadings | 7 | 2+1+2+2 |
| M3-6 | Visualization | 5 figures (gate, heatmap, biplot, scatter matrix, variance) | 9 | 2+2+2+3 |
| M3-7 | Mechanism verification + report | `verify_mechanism_activation` + `04_validation.md` | 6 | 1+2+2+1 |
| M3-8 | Entry point + wiring | `run_experiment.py` main() end-to-end | 6 | 1+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M3-6], Low(4-8): [M3-1, M3-2, M3-3, M3-4, M3-5, M3-7, M3-8]

---

## External Dependencies

None — no base hypothesis code reuse. H-M3 reads H-M2's output CSV (`h-m2/model_scores.csv`) as a data file only, not as an imported module (H-M2's `code/` directory does not exist to import from).
