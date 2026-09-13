# Logic: h-e1

**Type**: EXISTENCE (PoC) | Budget: 4 subtasks (A-1, A-5 only)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Collection [Complexity: 11, Budget: 3+3+3+2]

**Applied**: batch-fetch-then-cache (from architecture.md); openml.datasets.list_datasets / openml.runs.list_runs standard usage (no KB match found in Archon - out-of-domain corpus)

### API Signatures

```python
def collect_datasets(min_date: str) -> pd.DataFrame:
    """Query OpenML for classification datasets uploaded >= min_date."""
    # returns columns: [did, name, upload_date, NumberOfInstances, NumberOfClasses]
    ...

def get_matched_runs(dataset_id: int, min_runs: int) -> pd.DataFrame:
    """Fetch runs for dataset, group by (flow_id, setup_id), keep groups with count >= min_runs."""
    # returns columns: [run_id, dataset_id, flow_id, setup_id, predictive_accuracy]
    ...

def collect_all_matched_runs(dataset_ids: list[int]) -> pd.DataFrame:
    """Loop get_matched_runs over dataset_ids, concat, write PATHS['matched_runs']."""
    ...

def extract_controls(dataset_id: int, flow_id: int) -> dict:
    """Return {'stability': float, 'algo_family': str, 'sklearn_version': str}."""
    ...
```

### Tensor Shapes

Not applicable (tabular pandas pipeline, no tensors).

### Pseudo-code

```
collect_datasets(min_date):
  1. df = openml.datasets.list_datasets(output_format="dataframe")
  2. filter df.upload_date >= min_date AND task_type == classification
  3. return df[[did, name, upload_date, NumberOfInstances, NumberOfClasses]]

get_matched_runs(dataset_id, min_runs):
  1. runs = openml.runs.list_runs(task=dataset_id, output_format="dataframe")  # batch call, cache locally
  2. group by (flow_id, setup_id); keep groups where len >= min_runs
  3. return flattened run rows with predictive_accuracy per run

collect_all_matched_runs(dataset_ids):
  1. for did in dataset_ids: rows.append(get_matched_runs(did, MIN_RUNS_PER_GROUP))
  2. df = pd.concat(rows)
  3. df.to_parquet(PATHS["matched_runs"])
  4. return df
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A1-1 | `collect_datasets` | OpenML dataset list query + date/task-type filter |
| L-A1-2 | `get_matched_runs` | Per-dataset run fetch + group-by matched-run filter |
| L-A1-3 | `collect_all_matched_runs` | Loop + concat + parquet write, rate-limit-safe batching |
| L-A1-4 | `extract_controls` | Stability/algo-family/sklearn-version extraction per (dataset, flow) |

---

## A-5: Mixed-Effects Model + Quartile/Bootstrap Effects [Complexity: 12, Budget: 3+2+4+3]

**Applied**: statsmodels MixedLM standard API (`smf.mixedlm(formula, data, groups=...)`); percentile bootstrap for CI

### API Signatures

```python
def fit_mixed_model(df: pd.DataFrame) -> "MixedLMResults":
    """Random intercept per dataset_id. Formula: iqr ~ metadata_score + stability + log_popularity + C(algo_family)"""
    ...

def compute_quartile_effect(df: pd.DataFrame) -> dict:
    """Compare IQR: top vs bottom metadata_score quartile."""
    # returns {"iqr_top": float, "iqr_bottom": float,
    #          "relative_reduction": float, "absolute_reduction": float}
    ...

def bootstrap_ci(df: pd.DataFrame, n_boot: int) -> dict:
    """Percentile bootstrap 95% CI on relative_reduction (resample datasets, not rows)."""
    # returns {"ci_lower": float, "ci_upper": float, "boot_estimates": list[float]}
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| df | [n_groups, k_cols] | one row per (dataset, flow, setup) |
| boot_estimates | [n_boot] | relative_reduction per resample |

### Pseudo-code

```
fit_mixed_model(df):
  1. formula = "iqr ~ metadata_score + stability + log_popularity + C(algo_family)"
  2. model = smf.mixedlm(formula, df, groups=df["dataset_id"])
  3. result = model.fit(reml=False)
  4. assert result.converged  # NFR-2
  5. return result

compute_quartile_effect(df):
  1. q1, q3 = df.metadata_score.quantile([0.25, 0.75])
  2. bottom = df[df.metadata_score <= q1]; top = df[df.metadata_score >= q3]
  3. iqr_bottom, iqr_top = bottom.iqr.median(), top.iqr.median()
  4. abs_red = iqr_bottom - iqr_top
  5. rel_red = abs_red / iqr_bottom
  6. return {iqr_top, iqr_bottom, relative_reduction: rel_red, absolute_reduction: abs_red}

bootstrap_ci(df, n_boot):
  1. dataset_ids = df.dataset_id.unique()
  2. for i in range(n_boot):
       sample_ids = np.random.choice(dataset_ids, len(dataset_ids), replace=True)
       boot_df = df[df.dataset_id.isin(sample_ids)]
       estimates.append(compute_quartile_effect(boot_df)["relative_reduction"])
  3. ci_lower, ci_upper = np.percentile(estimates, [2.5, 97.5])
  4. return {ci_lower, ci_upper, boot_estimates: estimates}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A5-1 | `fit_mixed_model` | MixedLM formula spec, fit, convergence assertion |
| L-A5-2 | `compute_quartile_effect` | Quartile split + relative/absolute IQR reduction |
| L-A5-3 | `bootstrap_ci` | Dataset-level resampling loop + percentile CI |
| L-A5-4 | Diagnostics | Residual heteroscedasticity check + Cook's D (NFR-2) |
