# Architecture: H-M1
# Findable FAIR Sub-Criteria → Time-to-First-Run Survival Analysis

**Applied**: Survival analysis observational study pipeline pattern
**Applied**: Propensity-score-matched KM + Cox PH incremental extension pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (h-e1/code/)
**Analyzed Path**: `docs/youra_research/20260504_mldpr/h-e1/code/`
**Findings**: H-E1 uses flat `src/` module layout with `config.py` at root; modules are `collect_openml.py`, `score_fuji.py`, `analyze.py`, `visualize.py`, `main.py`. FAIR scores output to `results/fair_scores.csv` with columns `did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, status`. Fallback proxy already implemented in `score_fuji.fuji_fallback_proxy`. H-M1 reuses cohort CSV and extends with run timestamp pipeline.

---

## File Organization

- `h-m1/code/`
  - `config.py` — all constants + path resolver
  - `run_experiment.py` — CLI entry point
  - `src/`
    - `__init__.py`
    - `ingest.py` — OpenML run timestamp fetching + H-E1 merge
    - `findable.py` — Findable sub-score extraction from H-E1 proxy scores
    - `survival_prep.py` — survival DataFrame construction (TTFR, event, covariates)
    - `matching.py` — propensity score matching
    - `km_analysis.py` — Kaplan-Meier baseline + matched analysis
    - `cox_analysis.py` — Cox PH regression + PH assumption checks
    - `ablation.py` — ablation runner (A, B, C)
    - `sensitivity.py` — sensitivity analysis (SA-1, SA-2, SA-3)
    - `visualize.py` — all 6 required figures
    - `serialize.py` — JSON + CSV results serialization
  - `tests/`
    - `test_ingest.py`
    - `test_findable.py`
    - `test_survival_prep.py`
    - `test_matching.py`
    - `test_km_analysis.py`
    - `test_cox_analysis.py`
    - `test_ablation.py`
    - `test_sensitivity.py`
    - `test_visualize.py`
    - `test_serialize.py`

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| build_cohort | `sys.path` insert pattern — copy cohort CSV directly | `h-e1/code/src/collect_openml.py` |
| fuji_fallback_proxy | `sys.path` insert pattern — reuse via CSV load | `h-e1/code/src/score_fuji.py` |
| H-E1 FAIR scores CSV | Load from `h-e1/code/results/fair_scores.csv` | columns: `did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, status` |

**Verified from**: `h-e1/code/` actual implementation.
**Reuse strategy**: H-M1 loads `h-e1/code/results/fair_scores.csv` directly (no re-scoring). OpenML cohort did list sourced from same CSV.

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: none

```python
# Constants
H_E1_SCORES_CSV: str          # path to h-e1/code/results/fair_scores.csv
OPENML_UPLOAD_DATE_MIN: str   # "2018-01-01"
MIN_RUN_COUNT: int             # 10
OBSERVATION_WINDOW_DAYS: int  # 730 (2 years)
CALIPER_FACTOR: float          # 0.2
CALIPER_RELAXED_FACTOR: float  # 0.3
MIN_MATCHED_PAIRS: int         # 100
LOG_RANK_ALPHA: float          # 0.05
COX_HR_GATE: float             # 1.2
SMD_THRESHOLD: float           # 0.1
SEED: int                      # 42
RESULTS_DIR: str               # "results"
FIGURES_DIR: str               # "figures"

# F-UJI Findable sub-criteria weights
F1_PID_WEIGHT: float           # 0.25
F2_METADATA_WEIGHT: float      # 0.50
F3_SEARCH_WEIGHT: float        # 0.25

def parse_args() -> argparse.Namespace: ...
def resolve_paths(args) -> dict: ...
```

---

### DataIngestor (`src/ingest.py`)

**Dependencies**: config, pandas, openml, requests

```python
def load_he1_scores(scores_csv: str) -> pd.DataFrame:
    """Load H-E1 FAIR proxy scores CSV.
    Returns: DataFrame[did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, status]
    """
    ...

def fetch_run_timestamps(
    dataset_ids: list[int],
    cache_dir: str,
    retry_max: int = 3,
) -> pd.DataFrame:
    """Fetch first_run_timestamp and run_count per dataset via OpenML runs API.
    Returns: DataFrame[did, first_run_timestamp, run_count]
    """
    ...

def fetch_dataset_metadata(
    dataset_ids: list[int],
) -> pd.DataFrame:
    """Fetch upload_date, task_type per dataset_id from OpenML REST API.
    Returns: DataFrame[did, upload_date, task_type, NumberOfInstances]
    """
    ...

def build_merged_cohort(
    he1_scores: pd.DataFrame,
    run_data: pd.DataFrame,
    metadata: pd.DataFrame,
    min_run_count: int,
) -> pd.DataFrame:
    """Merge H-E1 scores + run timestamps + metadata; apply min_run_count filter.
    Returns: DataFrame[did, fair_aggregate, fair_F, fair_A, fair_I, fair_R,
                       upload_date, first_run_timestamp, run_count, task_type,
                       NumberOfInstances]
    """
    ...
```

---

### FindableExtractor (`src/findable.py`)

**Dependencies**: config, pandas, numpy

```python
def compute_f1_pid(cohort: pd.DataFrame) -> pd.Series:
    """Proxy: 1.0 if dataset has persistent DOI/URL indicator; else 0.0.
    Returns: Series[float] indexed by cohort.index
    """
    ...

def compute_f2_metadata(cohort: pd.DataFrame) -> pd.Series:
    """Proxy: proportion of non-null metadata fields (title, desc, tags, creator, license).
    Returns: Series[float] in [0, 1]
    """
    ...

def compute_f3_search_indexed(cohort: pd.DataFrame) -> pd.Series:
    """Proxy: 1.0 if dataset is tagged/categorized; 0.0 otherwise.
    Returns: Series[float]
    """
    ...

def compute_findable_score(
    cohort: pd.DataFrame,
    f1_weight: float,
    f2_weight: float,
    f3_weight: float,
) -> pd.DataFrame:
    """Compute findable_score composite and binary high_findable treatment.
    Returns: cohort + columns [F1_PID, F2_metadata, F3_search_indexed,
                               findable_score, high_findable]
    """
    ...

def compute_accessible_score(cohort: pd.DataFrame) -> pd.Series:
    """Proxy: accessible_score = 0.5*A1_open_license + 0.5*A2_standard_format.
    Used by Ablation B.
    Returns: Series[float]
    """
    ...
```

---

### SurvivalPreparer (`src/survival_prep.py`)

**Dependencies**: config, pandas, numpy

```python
def compute_time_to_first_run(
    cohort: pd.DataFrame,
    observation_window_days: int,
) -> pd.DataFrame:
    """Compute time_to_first_run (days) and event flag.
    - time_to_first_run = (first_run_timestamp - upload_date).days
    - event = 1 if first run observed; 0 if right-censored
    - duration = min(time_to_first_run, observation_window_days)
    Returns: cohort + columns [time_to_first_run, event]
    """
    ...

def encode_covariates(cohort: pd.DataFrame) -> pd.DataFrame:
    """Encode matching covariates:
    - creation_year_quartile: year(upload_date) → Q1-Q4 of 2018-2025
    - task_type: categorical label encoding
    - size_decile: NumberOfInstances → decile 1-10
    Returns: cohort + columns [creation_year_quartile, task_type_encoded, size_decile]
    """
    ...

def build_survival_df(
    cohort: pd.DataFrame,
    observation_window_days: int,
) -> pd.DataFrame:
    """Full survival DataFrame builder: calls compute_time_to_first_run + encode_covariates.
    Returns: DataFrame ready for propensity matching and KM/Cox analysis
    """
    ...

def validate_preconditions(survival_df: pd.DataFrame, cfg) -> dict:
    """Check mechanism_exists, mechanism_isolatable (pre-match), baseline_measurable.
    Returns: dict[str, bool | float]
    """
    ...
```

---

### PropensityMatcher (`src/matching.py`)

**Dependencies**: survival_prep, sklearn, pandas, numpy

```python
def fit_propensity_model(
    survival_df: pd.DataFrame,
    covariate_cols: list[str],
    treatment_col: str,
    seed: int,
) -> tuple:
    """Fit LogisticRegression propensity model.
    Returns: (fitted_model, propensity_scores: np.ndarray)
    """
    ...

def nearest_neighbor_match(
    survival_df: pd.DataFrame,
    ps_scores: np.ndarray,
    treatment_col: str,
    caliper: float,
    ratio: int = 1,
) -> pd.DataFrame:
    """1:N nearest-neighbor matching with caliper constraint.
    Returns: matched_df with pair_id column; len = 2 * n_matched_pairs
    """
    ...

def compute_smd(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    covariate_cols: list[str],
    treatment_col: str,
) -> pd.DataFrame:
    """Compute Standardized Mean Difference before and after matching.
    Returns: DataFrame[covariate, smd_before, smd_after]
    """
    ...

def run_matching(
    survival_df: pd.DataFrame,
    cfg,
    caliper_factor: float = None,
    ratio: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Full matching pipeline: fit PS → match → compute SMD → validate balance.
    Returns: (matched_df, smd_df, matching_meta: dict)
    """
    ...
```

---

### KaplanMeierAnalyzer (`src/km_analysis.py`)

**Dependencies**: matching, lifelines, pandas

```python
def run_km_unadjusted(
    survival_df: pd.DataFrame,
    treatment_col: str = "high_findable",
) -> dict:
    """Unadjusted KM analysis (baseline — no propensity matching).
    Returns: dict[baseline_log_rank_p, baseline_cox_hr (unadj),
                  median_ttfr_high_unadj, median_ttfr_low_unadj,
                  kmf_high, kmf_low]
    """
    ...

def run_km_matched(
    matched_df: pd.DataFrame,
    treatment_col: str = "high_findable",
) -> dict:
    """Matched KM analysis (proposed).
    Returns: dict[log_rank_p, median_ttfr_high, median_ttfr_low,
                  kmf_high, kmf_low, results_obj]
    """
    ...
```

---

### CoxPHAnalyzer (`src/cox_analysis.py`)

**Dependencies**: km_analysis, lifelines, pandas, numpy

```python
def fit_cox(
    matched_df: pd.DataFrame,
    formula: str,
    duration_col: str = "time_to_first_run",
    event_col: str = "event",
) -> tuple:
    """Fit CoxPHFitter with given formula.
    Returns: (cph_model, cox_hr: float, cox_ci_lower: float, cox_ci_upper: float)
    """
    ...

def check_ph_assumption(
    cph_model,
    matched_df: pd.DataFrame,
    p_threshold: float = 0.05,
) -> dict:
    """Run Schoenfeld residuals test (SA-2).
    Returns: dict[ph_violated: bool, schoenfeld_p: float, recommendation: str]
    """
    ...

def run_cox_primary(
    matched_df: pd.DataFrame,
    predictor_col: str = "findable_score",
) -> dict:
    """Primary Cox PH regression on matched data.
    Returns: dict[cox_hr, cox_ci_lower, cox_ci_upper, cox_p, ph_check]
    """
    ...
```

---

### AblationRunner (`src/ablation.py`)

**Dependencies**: matching, km_analysis, cox_analysis, findable, pandas

```python
def run_ablation_a(
    survival_df: pd.DataFrame,
    cfg,
) -> dict:
    """Ablation A: fair_proxy_score >= 0.5 binary split instead of median findable split.
    Returns: dict[log_rank_p, cox_hr, n_matched_pairs, label='ablation_a']
    """
    ...

def run_ablation_b(
    survival_df: pd.DataFrame,
    cfg,
) -> dict:
    """Ablation B: accessible_score as alternative IV (A1_open_license + A2_standard_format).
    Returns: dict[log_rank_p, cox_hr, n_matched_pairs, label='ablation_b']
    """
    ...

def run_ablation_c(
    survival_df: pd.DataFrame,
    cfg,
) -> dict:
    """Ablation C: relaxed caliper (0.3*SD) + ratio=5 matching if n_matched < 100.
    Returns: dict[log_rank_p, cox_hr, n_matched_pairs, smd_max, label='ablation_c']
    """
    ...

def run_all_ablations(
    survival_df: pd.DataFrame,
    cfg,
) -> dict:
    """Run A, B, C; return combined dict keyed by label.
    Returns: dict[str, dict]
    """
    ...
```

---

### SensitivityAnalyzer (`src/sensitivity.py`)

**Dependencies**: matching, km_analysis, cox_analysis, pandas

```python
def run_sa1_fuji_threshold(
    survival_df: pd.DataFrame,
    cfg,
) -> dict:
    """SA-1: F-UJI aggregate >= 0.5 threshold split (mirrors Ablation A).
    Returns: dict[log_rank_p, cox_hr, label='sa1']
    """
    ...

def run_sa2_ph_check(
    matched_df: pd.DataFrame,
    cph_model,
    cfg,
) -> dict:
    """SA-2: Schoenfeld residuals PH assumption check.
    Returns: dict[ph_violated, schoenfeld_p, recommendation, label='sa2']
    """
    ...

def run_sa3_observation_windows(
    survival_df: pd.DataFrame,
    cfg,
    windows: list[int] = None,
) -> list[dict]:
    """SA-3: Re-run primary analysis with observation_window in [180, 365, 730] days.
    Returns: list of dicts[window_days, log_rank_p, cox_hr]
    """
    ...

def run_all_sensitivity(
    survival_df: pd.DataFrame,
    matched_df: pd.DataFrame,
    cph_model,
    cfg,
) -> dict:
    """Run SA-1, SA-2, SA-3; return combined dict.
    Returns: dict[str, dict | list]
    """
    ...
```

---

### Visualizer (`src/visualize.py`)

**Dependencies**: km_analysis, cox_analysis, matching, matplotlib, seaborn, lifelines

```python
def plot_km_curves(
    kmf_high, kmf_low,
    log_rank_p: float,
    median_high: float,
    median_low: float,
    figures_dir: str,
    label: str = "matched",
) -> str:
    """Figure 2: KM survival curves with 95% CI and median annotations.
    Returns: saved file path
    """
    ...

def plot_ps_distribution(
    ps_before: pd.Series,
    ps_after: pd.Series,
    figures_dir: str,
) -> str:
    """Figure 3: Propensity score histograms before/after matching.
    Returns: saved file path
    """
    ...

def plot_love_plot(
    smd_df: pd.DataFrame,
    figures_dir: str,
) -> str:
    """Figure 4: Love plot — SMD before vs. after matching per covariate.
    Returns: saved file path
    """
    ...

def plot_cox_forest(
    cox_hr: float,
    cox_ci_lower: float,
    cox_ci_upper: float,
    figures_dir: str,
) -> str:
    """Figure 5: Cox PH forest plot with HR + 95% CI.
    Returns: saved file path
    """
    ...

def plot_sensitivity_comparison(
    primary: dict,
    ablations: dict,
    figures_dir: str,
) -> str:
    """Figure 6: Bar chart comparing log-rank p and HR across primary + ablation analyses.
    Returns: saved file path
    """
    ...

def plot_gate_metrics(
    log_rank_p: float,
    cox_hr: float,
    figures_dir: str,
) -> str:
    """Figure 1: Gate metrics bar chart (p vs 0.05, HR vs 1.2).
    Returns: saved file path
    """
    ...

def generate_all_figures(
    results: dict,
    figures_dir: str,
) -> list[str]:
    """Dispatch all 6 figure generators.
    Returns: list of saved file paths
    """
    ...
```

---

### ResultSerializer (`src/serialize.py`)

**Dependencies**: pandas, json, os

```python
def build_results_dict(
    primary: dict,
    unadjusted: dict,
    matching_meta: dict,
    ablations: dict,
    sensitivity: dict,
) -> dict:
    """Assemble canonical results dict matching FR-9 schema.
    Returns: dict with all gate metrics and secondary metrics
    """
    ...

def save_results(
    results: dict,
    results_dir: str,
) -> dict:
    """Save results to JSON and CSV files.
    Returns: dict[json_path, csv_path]
    """
    ...

def save_gate_result(
    results: dict,
    results_dir: str,
    log_rank_alpha: float,
    cox_hr_gate: float,
) -> str:
    """Save gate_result.json with PASS/FAIL determination.
    Returns: saved file path
    """
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: all src modules, config

```python
def main() -> None:
    """CLI entry: parse args → load H-E1 scores → ingest runs → build survival DF
    → match → KM → Cox → ablations → sensitivity → figures → serialize.
    Exit code 0 = gate pass, 1 = gate fail.
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Config, file structure, requirements.txt, test scaffolding | 6 | 2+1+1+2 |
| A-2 | Data Ingest | Load H-E1 scores CSV, fetch OpenML run timestamps + metadata, merge, filter ≥10 runs | 14 | 3+3+4+4 |
| A-3 | Findable Extraction | F1_PID + F2_metadata + F3_search_indexed proxy computation, findable_score composite, high_findable binary treatment | 10 | 3+2+3+2 |
| A-4 | Survival Prep | time_to_first_run computation, right-censoring, covariate encoding (year_quartile, task_type, size_decile), precondition validation | 11 | 3+2+3+3 |
| A-5 | Propensity Matching | Logistic PS model, 1:1 NN matching with caliper, SMD computation, balance validation | 15 | 4+3+4+4 |
| A-6 | KM Analysis | Unadjusted baseline KM + log-rank, matched KM + log-rank (primary gate) | 12 | 3+3+3+3 |
| A-7 | Cox PH Regression | CoxPHFitter fit, HR extraction, Schoenfeld PH assumption check, CI computation | 13 | 3+3+4+3 |
| A-8 | Ablation Runner | Ablations A (FAIR threshold), B (accessible IV), C (relaxed caliper); full pipeline per ablation | 14 | 3+3+4+4 |
| A-9 | Sensitivity Analysis | SA-1 (F-UJI threshold), SA-2 (PH check), SA-3 (observation windows 180/365/730d) | 12 | 3+3+3+3 |
| A-10 | Visualization | All 6 required figures: gate metrics, KM curves, PS distribution, love plot, forest plot, sensitivity comparison | 13 | 3+2+4+4 |
| A-11 | Results Serialization | JSON + CSV output, gate_result.json with PASS/FAIL, canonical metrics schema | 9 | 2+2+3+2 |
| A-12 | Integration & Tests | run_experiment.py orchestration, unit tests (≥3 per module), smoke test end-to-end | 14 | 3+4+4+3 |

**Distribution**: VeryHigh(18-20): [] | High(14-17): [A-2, A-5, A-8, A-12] | Medium(9-13): [A-3, A-4, A-6, A-7, A-9, A-10, A-11] | Low(4-8): [A-1]
