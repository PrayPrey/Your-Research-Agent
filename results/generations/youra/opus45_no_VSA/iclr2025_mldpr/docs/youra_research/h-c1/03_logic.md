# Logic: h-c1

**Type**: CONDITION (Robustness Check) | Budget: 2 subtasks (B-1, B-5 only — Medium complexity tasks)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code (h-e1/code/analysis.py, collect.py)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `compute_reproducibility_iqr`, `compute_quartile_effect`, `bootstrap_ci` (analysis.py); `get_matched_runs` (collect.py, pattern reference only — reimplemented with timestamps)

Applied: rag_search_knowledge_base("temporal subsample analysis API design") returned no domain-relevant matches (KB corpus is diffusion-model focused, out-of-domain for tabular/OpenML) — used standard pandas/OpenML API design instead.

---

## B-1: Temporal Run Collection [Complexity: 10, Budget: 3+2+3+2]

**Applied**: Standard OpenML runs API + pandas merge (no KB match; extends h-e1's `get_matched_runs` pattern)

### API Signatures

```python
def get_matched_runs_with_timestamps(dataset_id: int, min_runs: int) -> pd.DataFrame:
    """Same grouping as h-e1 get_matched_runs, plus upload_time (run) and upload_date (dataset)."""
    # returns columns: [run_id, data_id, flow_id, setup_id, predictive_accuracy, upload_time, upload_date]
    ...

def collect_all_matched_runs_temporal(dataset_ids: list[int]) -> pd.DataFrame:
    """Loop get_matched_runs_with_timestamps, concat, write PATHS['matched_runs_temporal']."""
    ...
```

### Pseudo-code

```
get_matched_runs_with_timestamps(dataset_id, min_runs):
  1. runs = openml.runs.list_runs(task=dataset_id, output_format="dataframe")
  2. run_details = openml.runs.get_runs(runs.run_id.tolist())  # batch fetch to get upload_time per run
  3. group by (flow_id, setup_id); keep groups where len >= min_runs
  4. dataset_upload_date = openml.datasets.get_dataset(dataset_id).upload_date
  5. merge upload_time (run) + upload_date (dataset, constant per dataset) onto matched rows
  6. return columns: [run_id, data_id, flow_id, setup_id, predictive_accuracy, upload_time, upload_date]

collect_all_matched_runs_temporal(dataset_ids):
  1. for did in dataset_ids: rows.append(get_matched_runs_with_timestamps(did, MIN_RUNS_PER_DATASET_EARLY))
  2. df = pd.concat(rows)
  3. df.to_parquet(PATHS["matched_runs_temporal"])
  4. return df
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-B1-1 | `get_matched_runs_with_timestamps` | Per-dataset run fetch + group-by filter + upload_time/upload_date merge |
| L-B1-2 | `collect_all_matched_runs_temporal` | Loop + concat + parquet write, rate-limit-safe batching |

---

## B-5: Quartile Effect + Bootstrap CI on Subsample [Complexity: 7, Budget: 1+3+2+1]

**Applied**: Direct reuse of h-e1's pure functions — no reimplementation, only new call site on filtered `early_df`.

### API Signatures

```python
from h_e1_code.analysis import compute_reproducibility_iqr, compute_quartile_effect, bootstrap_ci

def run_early_effect_analysis(early_analysis_df: pd.DataFrame, n_boot: int = 1000) -> dict:
    """Orchestrates B-5: iqr_df = compute_reproducibility_iqr(early_analysis_df);
    effect = compute_quartile_effect(iqr_df); ci = bootstrap_ci(iqr_df, n_boot)."""
    # returns {"iqr_top": float, "iqr_bottom": float, "relative_reduction": float,
    #          "absolute_reduction": float, "ci_lower": float, "ci_upper": float}
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| early_analysis_df | [n_early_groups, k_cols] | one row per (dataset, flow, setup), early window only |
| boot_estimates | [n_boot] | relative_reduction per resample (internal to bootstrap_ci) |

### Pseudo-code

```
run_early_effect_analysis(early_analysis_df, n_boot):
  1. iqr_df = compute_reproducibility_iqr(early_analysis_df)   # same signature as h-e1
  2. effect = compute_quartile_effect(iqr_df)                  # {iqr_top, iqr_bottom, relative_reduction, absolute_reduction}
  3. ci = bootstrap_ci(iqr_df, n_boot)                          # {ci_lower, ci_upper, boot_estimates}
  4. return {**effect, "ci_lower": ci["ci_lower"], "ci_upper": ci["ci_upper"]}
```

### Subtasks [Bundled into B-1 budget — see note]

> **Note**: Total task budget is 2 subtasks across the whole hypothesis. B-1 consumes both (L-B1-1, L-B1-2) as the highest-complexity task requiring new logic. B-5 is a direct 3-line call to h-e1's unchanged functions — no new subtask needed, implemented inline in `run.py` per architecture.md orchestration.

---

## External Dependencies API (From Actual Code)

```python
# From: docs/youra_research/h-e1/code/analysis.py (ACTUAL CODE, verified via Serena)

def compute_reproducibility_iqr(df: pd.DataFrame) -> pd.DataFrame:
    """Per-(dataset,flow,setup) IQR of predictive_accuracy. Returns df with iqr, metadata_score cols."""
    ...

def compute_quartile_effect(df: pd.DataFrame) -> dict:
    """Compare IQR: top vs bottom metadata_score quartile."""
    # returns {"iqr_top": float, "iqr_bottom": float, "relative_reduction": float, "absolute_reduction": float}
    ...

def bootstrap_ci(df: pd.DataFrame, n_boot: int) -> dict:
    """Percentile bootstrap 95% CI on relative_reduction (resample datasets, not rows)."""
    # returns {"ci_lower": float, "ci_upper": float, "boot_estimates": list[float]}
    ...
```

**Verified from**: `docs/youra_research/h-e1/code/analysis.py` (actual implementation, read via Glob + inspection — signatures match architecture.md spec, no naming drift found).

**Not used**: `fit_mixed_model` (h-e1/analysis.py) — PRD Dependencies table mentions it but h-c1 FR-1..FR-8 only require IQR + quartile effect + bootstrap CI (see architecture.md note); omitted to avoid unused import.
