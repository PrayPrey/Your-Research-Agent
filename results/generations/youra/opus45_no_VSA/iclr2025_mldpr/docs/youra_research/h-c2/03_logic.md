# Logic: h-c2 (CONDITION - Permutation Control)

**Type:** Statistical analysis (no DL training, no GPU)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/analysis.py`
**Relevant Symbols**: `fit_mixed_model(df: pd.DataFrame)` (lines 56-81)

Verified: formula `iqr ~ metadata_score + stability + log_popularity + C(algo_family)`, groups=`dataset_id`, OLS fallback when `dataset_id.nunique() < 2`, returns statsmodels `result` object (not raw dict) — `result.params["metadata_score"]` is the coefficient accessor. h-c2 drops `C(algo_family)` since RF-only subset makes it constant (would be collinear/singular).

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/analysis.py:56 (ACTUAL CODE)
def fit_mixed_model(df: pd.DataFrame):
    """Random intercept per dataset_id. Formula: iqr ~ metadata_score + controls."""
    # NOT reused directly (formula differs - no algo_family term) - reimplemented in h-c2/code/permutation.py
    # Return type: statsmodels regression result; coefficient via result.params["metadata_score"]
```

Data source: `h-e1/code/data/processed/analysis.parquet` — columns `iqr, metadata_score, stability, log_popularity, algo_family, dataset_id`.

**Verified from**: `h-e1/code/analysis.py` (actual implementation, not PRD/architecture spec).

---

## A-2/A-3: Data Load + True Coefficient Fit [Complexity: 6+8=14, Budget: shared]

**Applied**: Freedman-Lane residual permutation test pattern (standard stat method, no KB match found — general PyTorch/ML KB has no permutation-test docs)

### API Signatures

```python
# data.py
def load_rf_subset(path: str, algo: str = "RandomForest") -> pd.DataFrame:
    """Load h-e1 parquet, filter algo_family==algo. Raises if <10 rows."""
    ...  # df: [n_rf, {iqr, metadata_score, stability, log_popularity, dataset_id}]

# permutation.py
def fit_coefficient(df: pd.DataFrame) -> float:
    """Fit mixedlm (OLS fallback if <2 groups), return metadata_score coef."""
    ...
```

### Pseudo-code (fit_coefficient)

```
1. if df.dataset_id.nunique() < 2:
     result = smf.ols("iqr ~ metadata_score + stability + log_popularity", df).fit()
   else:
     result = smf.mixedlm("iqr ~ metadata_score + stability + log_popularity",
                           df, groups=df.dataset_id).fit(reml=False)
2. return result.params["metadata_score"]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-C2-1 | load_rf_subset | Filter parquet to RandomForest rows, validate sample size |
| L-C2-2 | fit_coefficient | Mixed model / OLS fallback, extract metadata_score β |

---

## A-4/A-5: Permutation Loop + Metrics [Complexity: 9+5, no subtask budget left — inline in run.py]

### API Signatures

```python
# permutation.py
def run_permutation_test(df: pd.DataFrame, n_perms: int = 1000, seed: int = 42) -> dict:
    """Shuffle metadata_score n_perms times, refit, return stats dict."""
    ...
    # returns:
    # {
    #   "true_coef": float,
    #   "perm_coefs": np.ndarray,   # [n_perms]
    #   "p_value": float,           # two-sided
    #   "percentile_rank": float,   # 0-100
    #   "effect_ratio": float,      # 95th_pct(|perm_coefs|) / |true_coef|
    # }
```

### Pseudo-code

```
1. true_coef = fit_coefficient(df)
2. rng = np.random.default_rng(seed)
3. perm_coefs = []
4. for i in range(n_perms):
     df_p = df.copy()
     df_p["metadata_score"] = rng.permutation(df_p["metadata_score"].values)
     perm_coefs.append(fit_coefficient(df_p))
5. perm_coefs = np.array(perm_coefs)
6. p_value = mean(abs(perm_coefs) >= abs(true_coef))
7. percentile_rank = percentileofscore(perm_coefs, true_coef)
8. effect_ratio = percentile(abs(perm_coefs), 95) / abs(true_coef)
9. return {true_coef, perm_coefs, p_value, percentile_rank, effect_ratio}
```

---

## A-6/A-7/A-8: Evaluate, Visualize, Run [no subtask budget left — direct implementation]

```python
# evaluate.py
def check_success(result: dict, criteria: dict) -> bool:
    """percentile_rank>95 and p_value<0.05 and effect_ratio<0.05"""
    ...

def save_results(result: dict, success: bool, path: str) -> None:
    """Write JSON (perm_coefs as list) to path."""
    ...

# visualize.py
def plot_permutation_histogram(result: dict, out_path: str) -> None:
    """Histogram of perm_coefs, vline at true_coef, annotate percentile."""
    ...

def plot_effect_comparison(result: dict, out_path: str) -> None:
    """Bar chart: true |coef| vs 95th percentile |perm_coefs|."""
    ...

# run.py
def main() -> None:
    df = load_rf_subset(config.SOURCE_DATA_PATH, config.FILTER_ALGO)
    result = run_permutation_test(df, config.N_PERMUTATIONS, config.RANDOM_SEED)
    success = check_success(result, config.SUCCESS_CRITERIA)
    save_results(result, success, config.PATHS["results"])
    plot_permutation_histogram(result, config.PATHS["figures"] + "/hist.png")
    plot_effect_comparison(result, config.PATHS["figures"] + "/effect.png")
```
