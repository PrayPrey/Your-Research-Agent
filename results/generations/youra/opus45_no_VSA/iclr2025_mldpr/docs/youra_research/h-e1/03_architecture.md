# Architecture: h-e1

**Type**: EXISTENCE (PoC) | **Epic Tasks**: 6

Applied: batch-fetch-then-cache pattern (avoid per-record API calls; reduces OpenML API rate-limit risk per NFR-3)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis or existing `src/`/`code/` directory present.

---

## File Structure

```
h-e1/code/
├── config.py
├── collect.py
├── metadata_score.py
├── analysis.py
├── baselines.py
└── run.py
```

## Modules

### config.py

**Dependencies**: none

```python
MIN_DATE = "2019-01-01"
MIN_RUNS_PER_GROUP = 10
MIN_DATASETS = 200
MIN_TOTAL_RUNS = 5000
N_PERMUTATIONS = 100
N_BOOTSTRAP = 1000
PATHS = {
    "raw_metadata": "data/raw/metadata.parquet",
    "matched_runs": "data/raw/matched_runs.parquet",
    "analysis": "data/processed/analysis.parquet",
    "model_results": "results/h_e1_model.json",
    "effects": "results/h_e1_effects.json",
}
```

### collect.py (`code/collect.py`)

**Dependencies**: config, openml, pandas

```python
def collect_datasets(min_date: str) -> pd.DataFrame: ...
def get_matched_runs(dataset_id: int, min_runs: int) -> pd.DataFrame: ...
def collect_all_matched_runs(dataset_ids: list[int]) -> pd.DataFrame: ...  # writes matched_runs.parquet
def extract_controls(dataset_id: int, flow_id: int) -> dict: ...  # stability, algo_family, sklearn version
```

### metadata_score.py (`code/metadata_score.py`)

**Dependencies**: config, openml

```python
def compute_metadata_score(dataset) -> int: ...  # 0-5, per FR-2.1 rubric
def score_all_datasets(dataset_ids: list[int]) -> pd.DataFrame: ...  # writes metadata.parquet
```

### analysis.py (`code/analysis.py`)

**Dependencies**: config, statsmodels, numpy, pandas

```python
def compute_reproducibility_iqr(runs_df: pd.DataFrame) -> pd.DataFrame: ...
def build_analysis_dataset(matched_runs, metadata_scores, controls) -> pd.DataFrame: ...  # writes analysis.parquet
def fit_mixed_model(df: pd.DataFrame) -> "MixedLMResults": ...
def compute_quartile_effect(df: pd.DataFrame) -> dict: ...
def bootstrap_ci(df: pd.DataFrame, n_boot: int) -> dict: ...
```

### baselines.py (`code/baselines.py`)

**Dependencies**: config, analysis, numpy

```python
def null_baseline(df: pd.DataFrame, n_permutations: int) -> dict: ...
def size_baseline(df: pd.DataFrame) -> tuple[float, float]: ...  # (coef, pvalue)
```

### run.py (`code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
# Orchestrates: collect -> score -> build analysis dataset -> fit model
# -> quartile effect -> bootstrap CI -> baselines -> write JSON results + figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data collection | OpenML dataset discovery + matched-run aggregation (collect.py) | 11 | 3+3+3+2 |
| A-2 | Metadata scorer | 5-field completeness score (metadata_score.py) | 6 | 2+1+2+1 |
| A-3 | Control extraction | Intrinsic stability, popularity, algo family, sklearn version | 8 | 2+2+3+1 |
| A-4 | Reproducibility metrics + analysis dataset build | IQR computation, merge into analysis.parquet | 7 | 2+2+2+1 |
| A-5 | Mixed-effects model + quartile/bootstrap effects | Core statistical test of hypothesis | 12 | 3+2+4+3 |
| A-6 | Baselines (null permutation + size) | FR-6, falsification support | 6 | 2+1+2+1 |
| A-7 | Orchestration + results/figures output | run.py wiring, JSON/PNG artifacts | 5 | 2+2+1+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-5], Low(4-8): [A-2, A-3, A-4, A-6, A-7]
