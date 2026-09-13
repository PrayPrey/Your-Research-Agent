# Phase 3: Logic Design — H-E1

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design (no `code/` directory exists yet for h-e1; archived prior attempts under `_archive/` are unrelated superseded runs, not a base hypothesis)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Preparation [Complexity: 2, Budget: 3]

**Applied**: sklearn StandardScaler + pandas filtering

### API Signatures

```python
def load_benchmark_data(cache_path: str = "data/olleaderboard.parquet") -> pd.DataFrame:
    """Load Open LLM Leaderboard results, cache locally."""
    ...

def filter_models(
    df: pd.DataFrame,
    benchmarks: list[str],
    min_benchmarks: int = 4,
    date_min: str = "2023-01-01",
    date_max: str = "2025-12-31",
) -> pd.DataFrame:
    """Apply inclusion criteria (FR-02.1-02.3). Raises ValueError if N < 80."""
    ...

def build_matrices(
    df: pd.DataFrame,
    benchmarks: list[str],
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Impute + standardize Y, build X confounds.
    Returns Y: (N, 6), X: (N, 2), model_names: list[str]
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| df (filtered) | (N, ~9) | N >= 80 rows |
| Y | (N, 6) | z-scored benchmark matrix |
| X | (N, 2) | col0=log10(params), col1=release_date as ordinal float (days since epoch) |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_benchmark_data | HF datasets API + parquet cache |
| L-1-2 | filter_models | non-null params, >=4/6 benchmarks, date range, assert N>=80 |
| L-1-3 | build_matrices | column-mean impute -> StandardScaler -> Y; log10 params + ordinal date -> X |

---

## A-2: OLS Residualization [Complexity: 2, Budget: 2]

**Applied**: statsmodels OLS, per-column loop

### API Signatures

```python
def residualize(Y: np.ndarray, X: np.ndarray) -> tuple[np.ndarray, list[float]]:
    """OLS residualize each column of Y on X (with intercept).
    Returns Y_resid: (N, 6), r_squared: list[float] len 6
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| Y | (N, 6) | input, standardized |
| X | (N, 2) | confounds, no intercept column |
| X_design | (N, 3) | sm.add_constant(X) |
| Y_resid | (N, 6) | residuals, same shape as Y |
| r_squared | (6,) | one R² per benchmark, for FR-03/acceptance criteria |

### Pseudo-code

```
X_design = add_constant(X)                      # (N, 3)
Y_resid = zeros((N, 6))
r_squared = []
for i in range(6):
    model = OLS(Y[:, i], X_design).fit()
    Y_resid[:, i] = model.resid                  # (N,)
    r_squared.append(model.rsquared)
return Y_resid, r_squared
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | residualize | per-column OLS(y_i ~ log_params + release_date), store resid + R² |

---

## A-3: PCA + Permutation Test [Complexity: 3, Budget: 4]

**Applied**: sklearn PCA, column-wise independent permutation null

### API Signatures

```python
def run_pca(Y_resid: np.ndarray) -> dict:
    """Fit full PCA on Y_resid.
    Returns {lambda_1: float, variance_explained_pc1: float,
             loadings: np.ndarray (6,), eigenvalues: np.ndarray (6,)}
    """
    ...

def permutation_test(
    Y_resid: np.ndarray,
    n_perms: int = 1000,
    seed: int = 42,
) -> dict:
    """Column-wise independent permutation null for lambda_1.
    Returns {lambda_1_observed: float, null_dist: np.ndarray (n_perms,),
             p_value: float, threshold_95: float}
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| Y_resid | (N, 6) | PCA input |
| eigenvalues | (6,) | pca.explained_variance_ |
| loadings | (6,) | pca.components_[0, :], PC1 loadings |
| Y_perm | (N, 6) | each column independently permuted (breaks cross-benchmark correlation, preserves marginals) |
| null_dist | (1000,) | lambda_1 per permutation |

### Pseudo-code

```
# Observed
pca = PCA(n_components=6).fit(Y_resid)
lambda_1_observed = pca.explained_variance_[0]
variance_explained_pc1 = pca.explained_variance_ratio_[0]
loadings = pca.components_[0, :]

# Null (column-wise permutation breaks between-column correlation only)
rng = np.random.default_rng(seed)
null_dist = np.empty(n_perms)
for i in range(n_perms):
    Y_perm = Y_resid.copy()
    for j in range(Y_perm.shape[1]):
        Y_perm[:, j] = rng.permutation(Y_perm[:, j])
    null_dist[i] = PCA(n_components=1).fit(Y_perm).explained_variance_[0]

p_value = (np.sum(null_dist >= lambda_1_observed) + 1) / (n_perms + 1)
threshold_95 = np.percentile(null_dist, 95)
hypothesis_passed = bool(p_value < 0.05)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | run_pca | full PCA(n_components=6) on Y_resid, extract lambda_1/loadings/variance ratio |
| L-3-2 | permutation_test | 1000x independent per-column permutation, refit PCA(n_components=1), compute p_value + 95th percentile |

---

## A-4: Output Assembly [Complexity: 1, Budget: 1]

**Applied**: json.dump per FR-06 schema

### API Signatures

```python
def build_results(
    n_models: int,
    pca_result: dict,
    perm_result: dict,
    benchmarks: list[str],
) -> dict:
    """Assemble h_e1_results.json per PRD section 4.2 schema."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | build_results | map pca/perm outputs to output schema dict, zip loadings with benchmark names |
