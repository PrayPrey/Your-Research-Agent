# Architecture: h-c1

**Type**: CONDITION (Robustness Check) | **Epic Tasks**: 8

Applied: reuse-core-compute-recollect-for-missing-fields pattern (h-e1's cached analysis.parquet lacks `upload_time`/`run_id`; temporal filter requires re-collecting matched runs with timestamps, then reusing h-e1's pure statistical functions unchanged)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (h-e1/code/)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: h-e1's actual `analysis.py` functions (`compute_reproducibility_iqr`, `compute_quartile_effect`, `bootstrap_ci`) operate on plain DataFrames and are directly reusable. **However**, h-e1's cached `data/processed/analysis.parquet` has NO `run_id`/`upload_time`/`upload_date` columns — h-e1's `run.py` generates **synthetic controls** (OpenML API was unavailable) and never merges real timestamps. PRD's assumption of temporal columns in `analysis_dataset.parquet` is WRONG (spec vs. implementation mismatch). h-c1 must re-collect matched runs including `upload_time` via `collect.py`'s `get_matched_runs()` (which already queries OpenML evaluations with timestamps) before filtering — cannot just filter existing h-e1 parquet.

---

## File Structure

```
h-c1/code/
├── config.py
├── collect_temporal.py
├── filter_early.py
├── analysis.py          (thin re-export/wrapper of h-e1 functions)
└── run.py
```

## Modules

### config.py

**Dependencies**: none

```python
MAX_RUNS_EARLY = 50
MAX_DAYS_EARLY = 90
MIN_DATASETS_EARLY = 100
MIN_RUNS_PER_DATASET_EARLY = 5
N_BOOTSTRAP = 1000
RANDOM_SEED = 42
FULL_SAMPLE_EFFECT_PCT = 42.1   # from h-e1/results/h_e1_effects.json
PERSISTENCE_RATIO_MIN = 0.5
RELATIVE_REDUCTION_MIN = 0.20
PATHS = {
    "matched_runs_temporal": "data/raw/matched_runs_temporal.parquet",
    "early_runs": "data/processed/early_runs.parquet",
    "effects": "results/h_c1_effects.json",
    "figures_dir": "figures/",
}
```

### collect_temporal.py (`code/collect_temporal.py`)

**Dependencies**: config, openml, pandas
**Reuses**: `h_e1.collect.get_matched_runs` pattern (extends with `upload_time`, dataset `upload_date`)

```python
def get_matched_runs_with_timestamps(dataset_id: int, min_runs: int) -> pd.DataFrame: ...
    # same as h-e1 get_matched_runs() + adds upload_time (run) and upload_date (dataset)
def collect_all_matched_runs_temporal(dataset_ids: list[int]) -> pd.DataFrame: ...
    # writes matched_runs_temporal.parquet with columns:
    # data_id, flow_id, setup_id, predictive_accuracy, upload_time, upload_date
```

### filter_early.py (`code/filter_early.py`)

**Dependencies**: config, pandas

```python
def filter_early_runs(runs_df: pd.DataFrame, max_runs: int = 50, max_days: int = 90) -> pd.DataFrame: ...
    # days_since_upload = upload_time - upload_date; filter <= max_days; groupby(data_id).head(max_runs)
def validate_sample_size(early_df: pd.DataFrame, min_datasets: int, min_runs: int) -> dict: ...
    # returns {"n_datasets": int, "n_runs": int, "pass": bool}
```

### analysis.py (`code/analysis.py`)

**Dependencies**: h_e1.analysis (import, no reimplementation)

```python
from h_e1_code.analysis import (
    compute_reproducibility_iqr,   # REUSE unchanged
    compute_quartile_effect,       # REUSE unchanged
    bootstrap_ci,                  # REUSE unchanged
)

def build_early_analysis_dataset(early_runs: pd.DataFrame, metadata_scores: pd.DataFrame) -> pd.DataFrame: ...
    # mirrors h-e1 build_analysis_dataset(), skips synthetic controls (not needed for quartile test)
def compute_persistence_ratio(early_effect_pct: float, full_effect_pct: float) -> float: ...
```

### run.py (`code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
# Orchestrates: collect_temporal -> filter_early -> validate_sample_size
# -> build_early_analysis_dataset -> compute_reproducibility_iqr -> compute_quartile_effect
# -> bootstrap_ci -> compute_persistence_ratio -> write JSON + figures
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| compute_reproducibility_iqr | `from h_e1_code.analysis import compute_reproducibility_iqr` | `h-e1/code/analysis.py` |
| compute_quartile_effect | `from h_e1_code.analysis import compute_quartile_effect` | `h-e1/code/analysis.py` |
| bootstrap_ci | `from h_e1_code.analysis import bootstrap_ci` | `h-e1/code/analysis.py` |
| score_all_datasets | `from h_e1_code.metadata_score import score_all_datasets` | `h-e1/code/metadata_score.py` |
| get_matched_runs (pattern reference only) | n/a — reimplemented in `collect_temporal.py` | `h-e1/code/collect.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, read via Serena)

**Note**: `fit_mixed_model` and `null_baseline`/`size_baseline` (mentioned in PRD as reusable) are NOT required by h-c1 FRs (FR-1..FR-8 only need IQR + quartile effect + bootstrap CI); omitted to avoid unused imports.

**Note**: `h-e1/results/h_e1_effects.json` provides `full_sample_effect = 42.1` — loaded directly, not recomputed.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Temporal run collection | Extend h-e1 run-matching to include upload_time/upload_date (collect_temporal.py) | 10 | 3+2+3+2 |
| B-2 | Early-run filter | Time-window + first-N-runs filter, groupby logic (filter_early.py) | 6 | 2+1+2+1 |
| B-3 | Sample size validation | FR-3 threshold check + warning logging | 4 | 1+1+1+1 |
| B-4 | Early analysis dataset build | Merge filtered runs + metadata scores, mirror h-e1 build step | 6 | 2+2+1+1 |
| B-5 | Quartile effect + bootstrap CI on subsample | Reuse h-e1 functions on early_df | 7 | 1+3+2+1 |
| B-6 | Persistence ratio + gate decision | Compare early vs full effect, PASS/FAIL per FR-6 | 5 | 1+2+1+1 |
| B-7 | Results export | JSON with required fields (FR-7) | 3 | 1+1+0+1 |
| B-8 | Visualization + orchestration | effect_comparison.png, run.py wiring | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-1, B-5], Low(4-8): [B-2, B-3, B-4, B-6, B-7, B-8]
