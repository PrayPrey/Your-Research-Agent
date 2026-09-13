# Architecture: H-E1 (Existence Test — Latent Factor Survival)

**Type**: EXISTENCE (PoC) — minimal pipeline, no ablation modules
**Applied**: Standard PCA + permutation significance test pattern (statsmodels OLS residualization → sklearn PCA → permutation null)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze (prior archived attempts under `_archive/` are not a base hypothesis and are not reused)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch, following PRD module names in Section 7

---

## 1. Module Structure

Data flow: `data_loader` → `preprocessing` → `analysis` → `visualization`, orchestrated by `h_e1_eigenvalue_test.py`.

### data_loader (`data_loader.py`)

**Dependencies**: datasets, pandas

```python
def load_leaderboard(cache_path: str = "outputs/raw_leaderboard.parquet") -> pd.DataFrame: ...
def load_from_cache_or_api(cache_path: str) -> pd.DataFrame: ...
```

### preprocessing (`preprocessing.py`)

**Dependencies**: pandas, numpy, sklearn.preprocessing.StandardScaler

```python
BENCHMARKS = ["ifeval", "bbh", "math_hard", "gpqa", "musr", "mmlu_pro"]

def filter_models(df: pd.DataFrame, min_benchmarks: int = 4,
                   date_start: str = "2023-01-01", date_end: str = "2025-12-31") -> pd.DataFrame: ...
def impute_missing(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame: ...
def build_matrices(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Returns (Y standardized benchmark matrix N x 6, X confound matrix N x 2 [log_params, release_date])"""
```

### analysis (`analysis.py`)

**Dependencies**: statsmodels, sklearn.decomposition.PCA, numpy

```python
def residualize(Y: np.ndarray, X: np.ndarray) -> tuple[np.ndarray, list[float]]:
    """Returns (Y_resid N x 6, r_squared_per_benchmark)"""

def fit_pca(Y_resid: np.ndarray) -> dict:
    """Returns {eigenvalues, variance_ratio, loadings_pc1}"""

def permutation_test(Y_resid: np.ndarray, n_perms: int = 1000, seed: int = 42) -> dict:
    """Returns {lambda_obs, null_dist, p_value, threshold_95}"""

def check_assumptions(Y_resid: np.ndarray, X: np.ndarray) -> dict:
    """Returns {shapiro_p, vif, kmo}"""
```

### visualization (`visualization.py`)

**Dependencies**: matplotlib

```python
def plot_permutation_dist(null_dist: list[float], lambda_obs: float, threshold_95: float, out_path: str) -> None: ...
def plot_scree(eigenvalues: list[float], out_path: str) -> None: ...
def plot_pc1_loadings(loadings: list[float], labels: list[str], out_path: str) -> None: ...
```

### orchestrator (`h_e1_eigenvalue_test.py`)

```python
def main() -> dict:
    """Runs full pipeline, writes outputs/h_e1_results.json, returns results dict"""
```

---

## 2. File Organization

```
h-e1/code/
  data_loader.py
  preprocessing.py
  analysis.py
  visualization.py
  h_e1_eigenvalue_test.py
  requirements.txt
h-e1/outputs/
  h_e1_results.json
  benchmark_matrix.csv
  residualized_matrix.csv
  permutation_dist.png
  scree_plot.png
  pc1_loadings.png
```

No `config.py` — single fixed run config (benchmark list, seed=42, n_perms=1000, date range) lives as module-level constants in `preprocessing.py` / `analysis.py` per PoC rule (no ablation config surface needed).

---

## 3. Error Handling & Validation Checkpoints

| Checkpoint | Location | Failure Mode |
|---|---|---|
| API load returns 0 rows | `data_loader.load_leaderboard` | raise `RuntimeError` |
| N < 80 after filtering | `preprocessing.filter_models` | raise `ValueError` with filter counts logged (NFR-03) |
| Any benchmark >30% missing after filter | `preprocessing.impute_missing` | log warning, proceed |
| OLS fit failure (singular X) | `analysis.residualize` | raise `ValueError`, report VIF |
| PCA eigenvalues NaN | `analysis.fit_pca` | raise `RuntimeError` |
| Permutation null empty/degenerate | `analysis.permutation_test` | assert `len(null_dist) == n_perms` |
| Output schema incomplete | `h_e1_eigenvalue_test.main` | assert all keys in Section 4.2 output schema present before json.dump |

Each filtering step logs `(step_name, n_before, n_after)` to satisfy NFR-02 reproducibility requirement.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loader | HF datasets API load + local parquet cache | 6 | 2+1+1+2 |
| A-2 | Filtering | Apply inclusion criteria (params, benchmarks, date), log counts | 5 | 2+1+1+1 |
| A-3 | Preprocessing | Impute, standardize, build Y/X matrices | 5 | 2+1+1+1 |
| A-4 | Residualization | OLS per benchmark, extract residuals + R² | 6 | 2+2+1+1 |
| A-5 | PCA fit | Fit PCA on residuals, extract eigenvalues/loadings | 4 | 1+1+1+1 |
| A-6 | Permutation test | 1000-iter column permutation null, p-value, threshold | 7 | 2+2+2+1 |
| A-7 | Assumption checks | Shapiro-Wilk, VIF, KMO | 5 | 2+1+1+1 |
| A-8 | Visualization | 3 plots (null dist, scree, loadings) | 4 | 1+1+1+1 |
| A-9 | Orchestration + output | Wire pipeline, write results JSON, assertions | 5 | 1+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1,A-2,A-3,A-4,A-5,A-6,A-7,A-8,A-9]

---

## External Dependencies

None — green-field, no base hypothesis code reused.
