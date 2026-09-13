# Architecture: h-c2

**Type:** CONDITION (Permutation Control) | **Gate:** SHOULD_WORK | **Budget:** EXISTENCE (minimal)

Applied: Freedman-Lane residual permutation test pattern (scipy.stats.permutation_test reference)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e1)
**Status:** Patterns found from base code — PRD/brief column names do NOT match actual h-e1 implementation.
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:**
- Actual analysis dataset: `h-e1/code/data/processed/analysis.parquet` (NOT `processed_datasets.csv` as PRD assumes)
- Actual columns: `iqr`, `metadata_score`, `stability`, `log_popularity`, `algo_family`, `dataset_id` (group) — differs from PRD's `iqr_variance`, `metadata_completeness`, `algorithm_family`, `infrastructure`
- `fit_mixed_model(df)` in `h-e1/code/analysis.py` is the real regression function to reuse (formula: `iqr ~ metadata_score + stability + log_popularity + C(algo_family)`, `groups=dataset_id`, falls back to OLS if <2 groups)
- No pre-existing RandomForest-only filter/column — h-c2 must filter `algo_family == "RandomForest"` itself

**Corrected plan:** h-c2 code will subset h-e1's analysis.parquet to RandomForest rows, then run permutation test on `metadata_score` coefficient using the same formula (minus `C(algo_family)` term, since it's constant after filtering).

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| fit_mixed_model | reimplemented locally (formula adapted, no algo_family term) | `h-e1/code/analysis.py:56` (reference only) |
| analysis dataset | loaded directly via `pd.read_parquet` | `h-e1/code/data/processed/analysis.parquet` |

**Verified from:** `h-e1/code/` (actual implementation, not 03_architecture.md spec)

---

## Module Structure

### config.py (`h-c2/code/config.py`)

```python
N_PERMUTATIONS: int = 1000
RANDOM_SEED: int = 42
SOURCE_DATA_PATH: str = "../h-e1/code/data/processed/analysis.parquet"
FILTER_ALGO: str = "RandomForest"
PATHS: dict  # results/, figures/
SUCCESS_CRITERIA: dict  # percentile_rank_min=95, p_value_max=0.05, effect_ratio_max=0.05
```

### data.py (`h-c2/code/data.py`)

**Dependencies**: config

```python
def load_rf_subset(path: str, algo: str) -> pd.DataFrame: ...
    # reads analysis.parquet, filters algo_family == algo, drops C(algo_family) need
```

### permutation.py (`h-c2/code/permutation.py`)

**Dependencies**: data, statsmodels

```python
def fit_coefficient(df: pd.DataFrame) -> float: ...
    # smf.mixedlm("iqr ~ metadata_score + stability + log_popularity", groups=dataset_id)
    # falls back to OLS if <2 groups; returns params["metadata_score"]

def run_permutation_test(df: pd.DataFrame, n_perms: int, seed: int) -> dict: ...
    # returns {true_coef, perm_coefs: np.ndarray, p_value, percentile_rank, effect_ratio}
```

### evaluate.py (`h-c2/code/evaluate.py`)

**Dependencies**: permutation

```python
def check_success(result: dict, criteria: dict) -> bool: ...
def save_results(result: dict, success: bool, path: str) -> None: ...
```

### visualize.py (`h-c2/code/visualize.py`)

**Dependencies**: matplotlib

```python
def plot_permutation_histogram(result: dict, out_path: str) -> None: ...
    # histogram of perm_coefs + vertical line at true_coef + percentile annotation
def plot_effect_comparison(result: dict, out_path: str) -> None: ...
    # bar chart: true effect vs 95th percentile of |perm_coefs|
```

### run.py (`h-c2/code/run.py`)

**Dependencies**: config, data, permutation, evaluate, visualize

```python
def main() -> None: ...
    # load -> filter RF -> run_permutation_test -> check_success -> save -> plots
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup config & paths | config.py with N_PERMUTATIONS, seed, paths, criteria | 4 | 1+1+1+1 |
| A-2 | Load & filter RF subset | Read h-e1 parquet, filter algo_family==RandomForest, validate min sample size | 6 | 2+2+1+1 |
| A-3 | True coefficient fit | Adapt fit_mixed_model without algo_family term, handle OLS fallback | 8 | 3+2+2+1 |
| A-4 | Permutation loop | 1000x shuffle metadata_score, refit, collect coef array, seeded | 9 | 3+2+3+1 |
| A-5 | Statistical metrics | percentile_rank, p_value, effect_ratio computation | 5 | 1+1+2+1 |
| A-6 | Success check & save results | Compare against SUCCESS_CRITERIA, write JSON | 4 | 1+1+1+1 |
| A-7 | Visualization | Histogram + effect comparison bar chart, save to figures/ | 6 | 2+1+2+1 |
| A-8 | Integration run script | Wire all modules in run.py end-to-end | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4], Low(4-8): [A-1, A-2, A-3, A-5, A-6, A-7, A-8]

---

## Notes

- Statistical analysis only — no DL training, no GPU, single-process serial loop (1000 mixedlm fits ~10-30 min per PRD NFR-1).
- Reuses h-e1's regression formula pattern but drops `C(algo_family)` since RF-only subset makes it constant.
- Green-field for h-c2/code/ itself; base_hypothesis (h-e1) code was mandatory Serena analysis per rules.
