# Logic: H-M1
# Findable FAIR Sub-Criteria → Time-to-First-Run Survival Analysis

**Applied**: Propensity-score-matched survival analysis pipeline pattern
**Applied**: Observational study causal inference pattern (PS matching + KM + Cox)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code (h-e1/code/)
**Analyzed Path**: `docs/youra_research/20260504_mldpr/h-e1/code/`
**Relevant Symbols**:
- `build_cohort(cfg) -> pd.DataFrame` — in `src/collect_openml.py`; accepts cfg object with `OPENML_UPLOAD_DATE_MIN`, `OPENML_TASK_TYPES`, `max_datasets` attributes
- `fuji_fallback_proxy(cohort: pd.DataFrame) -> pd.DataFrame` — in `src/score_fuji.py`; returns columns `did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, sub_criteria, status`
- `score_cohort(cohort: pd.DataFrame, cfg) -> pd.DataFrame` — in `src/score_fuji.py`
- H-E1 results CSV: `h-e1/code/results/fair_scores.csv`; columns: `did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, status`
- H-E1 cfg uses flat constants (not a class) + `parse_args()` + `resolve_paths(args)`

---

## External Dependencies API

### API Signatures (From Actual Code)

```python
# From: h-e1/code/src/collect_openml.py (ACTUAL CODE)
def build_cohort(cfg) -> pd.DataFrame:
    """Returns DataFrame[did, name, upload_date, NumberOfInstances,
    NumberOfFeatures, MajorityClassPercentage, landing_page_url]"""
    ...

# From: h-e1/code/src/score_fuji.py (ACTUAL CODE)
def fuji_fallback_proxy(cohort: pd.DataFrame) -> pd.DataFrame:
    """Returns DataFrame[did, fair_aggregate, fair_F, fair_A, fair_I, fair_R,
    sub_criteria, status='fallback']"""
    ...

def score_cohort(cohort: pd.DataFrame, cfg) -> pd.DataFrame:
    """cfg must have: FUJI_API_BASE, FUJI_CONCURRENCY, FUJI_RETRY_MAX,
    FUJI_RETRY_BASE_S, cache_dir, use_fallback"""
    ...
```

**Verified from**: `h-e1/code/src/collect_openml.py` and `h-e1/code/src/score_fuji.py`
**Reuse strategy**: H-M1 loads `h-e1/code/results/fair_scores.csv` directly — no re-scoring.
CSV columns confirmed: `did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, status`

---

## A-2: Data Ingest [Complexity: 14, Budget: 3 subtasks]

### API Signatures

```python
# src/ingest.py

def load_he1_scores(scores_csv: str) -> pd.DataFrame:
    """Load H-E1 FAIR proxy scores from CSV.
    Returns: DataFrame[did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, status]
    Raises: FileNotFoundError if CSV missing
    """
    ...

def fetch_run_timestamps(
    dataset_ids: list[int],
    cache_dir: str,
    retry_max: int = 3,
) -> pd.DataFrame:
    """Fetch first run timestamp and run_count per dataset via OpenML runs API.
    Caches per-dataset JSON to cache_dir/{did}_runs.json.
    Returns: DataFrame[did, first_run_timestamp: pd.Timestamp | NaT, run_count: int]
    """
    ...

def fetch_dataset_metadata(
    dataset_ids: list[int],
) -> pd.DataFrame:
    """Fetch upload_date, task_type, NumberOfInstances per dataset from OpenML REST API.
    Endpoint: GET /api/v1/json/data/{did}
    Returns: DataFrame[did, upload_date: pd.Timestamp, task_type: str,
                       NumberOfInstances: float]
    """
    ...

def build_merged_cohort(
    he1_scores: pd.DataFrame,
    run_data: pd.DataFrame,
    metadata: pd.DataFrame,
    min_run_count: int,
) -> pd.DataFrame:
    """Merge H-E1 scores + run timestamps + metadata; apply min_run_count filter.
    Join key: did (inner join on he1_scores x metadata, left join for run_data)
    Returns: DataFrame[did, fair_aggregate, fair_F, fair_A, fair_I, fair_R,
                       upload_date, first_run_timestamp, run_count, task_type,
                       NumberOfInstances]
    """
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description | Epic |
|----|---------|-------------|------|
| L-2-1 | load_he1_scores | Read CSV, validate columns, cast did to int | A-2 |
| L-2-2 | fetch_run_timestamps | OpenML runs API loop with per-did cache and retry backoff; extract min timestamp | A-2 |
| L-2-3 | fetch_dataset_metadata + build_merged_cohort | REST API per-did metadata fetch; three-way merge + min_run_count filter | A-2 |

### Pseudo-code (fetch_run_timestamps)

```
for did in dataset_ids:
    if cache hit: load; continue
    runs = openml.runs.list_runs(dataset_id=did, output_format="dataframe")
    first_ts = runs["upload_time"].min() if len(runs) > 0 else NaT
    run_count = len(runs)
    cache to cache_dir/{did}_runs.json
return DataFrame([did, first_run_timestamp, run_count])
```

---

## A-5: Propensity Matching [Complexity: 15, Budget: 3 subtasks]

### API Signatures

```python
# src/matching.py

def fit_propensity_model(
    survival_df: pd.DataFrame,
    covariate_cols: list[str],
    treatment_col: str,
    seed: int,
) -> tuple[Any, np.ndarray]:
    """Fit LogisticRegression(max_iter=500, random_state=seed) on covariate_cols.
    survival_df columns needed: covariate_cols + [treatment_col]
    Returns: (fitted_model, propensity_scores: np.ndarray shape [N])
    """
    ...

def nearest_neighbor_match(
    survival_df: pd.DataFrame,
    ps_scores: np.ndarray,
    treatment_col: str,
    caliper: float,
    ratio: int = 1,
) -> pd.DataFrame:
    """1:ratio nearest-neighbor matching with caliper on logit(ps_scores).
    Algorithm: for each treated unit find ratio closest controls within caliper.
    Returns: matched_df with pair_id column; len = (ratio+1) * n_matched_pairs
    """
    ...

def compute_smd(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    covariate_cols: list[str],
    treatment_col: str,
) -> pd.DataFrame:
    """Compute Standardized Mean Difference for each covariate before and after matching.
    SMD = (mean_treated - mean_control) / sqrt((var_treated + var_control) / 2)
    Returns: DataFrame[covariate, smd_before, smd_after]
    """
    ...

def run_matching(
    survival_df: pd.DataFrame,
    cfg,
    caliper_factor: float = None,
    ratio: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Full matching pipeline:
    1. fit_propensity_model on [creation_year_quartile, task_type_encoded, size_decile]
    2. caliper = (caliper_factor or cfg.CALIPER_FACTOR) * SD(logit(ps))
    3. nearest_neighbor_match
    4. compute_smd
    5. validate: smd_max < cfg.SMD_THRESHOLD and n_pairs >= cfg.MIN_MATCHED_PAIRS
    Returns: (matched_df, smd_df, matching_meta: dict[n_matched_pairs, smd_max,
              caliper_used, ps_sd, balance_ok])
    """
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description | Epic |
|----|---------|-------------|------|
| L-5-1 | fit_propensity_model | LogisticRegression fit; return model + ps array | A-5 |
| L-5-2 | nearest_neighbor_match | logit transform; NearestNeighbors on controls; caliper filter; pair_id assignment | A-5 |
| L-5-3 | compute_smd + run_matching | SMD calculation; full pipeline orchestration with balance validation | A-5 |

### Pseudo-code (nearest_neighbor_match)

```
logit_ps = log(ps / (1 - ps))
treated_idx = survival_df[treatment_col == 1].index
control_idx = survival_df[treatment_col == 0].index

nn = NearestNeighbors(n_neighbors=ratio).fit(logit_ps[control_idx].reshape(-1,1))
distances, indices = nn.kneighbors(logit_ps[treated_idx].reshape(-1,1))

matched_pairs = []
used_controls = set()
for i, (t_idx, dists, ctrl_idxs) in enumerate(zip(treated_idx, distances, indices)):
    for d, c_pos in zip(dists, ctrl_idxs):
        c_idx = control_idx[c_pos]
        if d <= caliper and c_idx not in used_controls:
            matched_pairs.append((i, t_idx, c_idx))
            used_controls.add(c_idx)
            break

matched_df = concat treated[matched] + control[matched]; assign pair_id
```

---

## A-8: Ablation Runner [Complexity: 14, Budget: 3 subtasks]

### API Signatures

```python
# src/ablation.py

def run_ablation_a(
    survival_df: pd.DataFrame,
    cfg,
) -> dict:
    """Ablation A: replace median Findable split with fair_proxy_score >= 0.5 binary.
    treatment = (fair_aggregate >= 0.5).astype(int)
    Re-runs: fit PS → match → KM log-rank → Cox HR
    Returns: dict[log_rank_p, cox_hr, n_matched_pairs, smd_max, label='ablation_a']
    """
    ...

def run_ablation_b(
    survival_df: pd.DataFrame,
    cfg,
) -> dict:
    """Ablation B: substitute accessible_score as IV.
    accessible_score from findable.compute_accessible_score(survival_df)
    high_accessible = (accessible_score > median).astype(int)
    Re-runs full pipeline with accessible_score as predictor in Cox.
    Returns: dict[log_rank_p, cox_hr, n_matched_pairs, smd_max, label='ablation_b']
    """
    ...

def run_ablation_c(
    survival_df: pd.DataFrame,
    cfg,
) -> dict:
    """Ablation C: relaxed caliper=0.3*SD + ratio=5 matching.
    Triggered always (documents robustness, not just fallback).
    Returns: dict[log_rank_p, cox_hr, n_matched_pairs, smd_max, label='ablation_c']
    """
    ...

def run_all_ablations(
    survival_df: pd.DataFrame,
    cfg,
) -> dict[str, dict]:
    """Run A, B, C sequentially; return {label: result_dict}.
    Returns: {'ablation_a': dict, 'ablation_b': dict, 'ablation_c': dict}
    """
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description | Epic |
|----|---------|-------------|------|
| L-8-1 | run_ablation_a | FAIR aggregate threshold split; reuse run_matching + run_km_matched + run_cox_primary | A-8 |
| L-8-2 | run_ablation_b | Accessible IV substitution; compute_accessible_score; reuse full pipeline | A-8 |
| L-8-3 | run_ablation_c + run_all_ablations | Relaxed caliper; orchestration of all three ablations | A-8 |

### Pseudo-code (run_ablation_a)

```
df = survival_df.copy()
df["treatment"] = (df["fair_aggregate"] >= 0.5).astype(int)
matched_df, smd_df, meta = run_matching(df, cfg, treatment_col="treatment")
km_result = run_km_matched(matched_df, treatment_col="treatment")
cox_result = run_cox_primary(matched_df, predictor_col="fair_aggregate")
return {log_rank_p, cox_hr, n_matched_pairs=meta["n_matched_pairs"],
        smd_max=meta["smd_max"], label="ablation_a"}
```

---

## A-12: Integration & Tests [Complexity: 14, Budget: 3 subtasks]

### API Signatures

```python
# run_experiment.py

def main() -> None:
    """CLI entry point. Pipeline:
    1. parse_args() + resolve_paths()
    2. load_he1_scores(paths["he1_scores_csv"])
    3. fetch_run_timestamps(dids, cache_dir)
    4. fetch_dataset_metadata(dids)
    5. build_merged_cohort(he1_scores, run_data, metadata, cfg.MIN_RUN_COUNT)
    6. compute_findable_score(cohort, F1/F2/F3 weights) → survival_df
    7. build_survival_df(cohort, cfg.OBSERVATION_WINDOW_DAYS)
    8. validate_preconditions(survival_df, cfg)
    9. run_km_unadjusted(survival_df) → unadjusted baseline
    10. run_matching(survival_df, cfg) → matched_df, smd_df, matching_meta
    11. run_km_matched(matched_df) → km_results (PRIMARY GATE)
    12. run_cox_primary(matched_df) → cox_results (SECONDARY GATE)
    13. run_all_ablations(survival_df, cfg)
    14. run_all_sensitivity(survival_df, matched_df, cph_model, cfg)
    15. generate_all_figures(results, paths["figures_dir"])
    16. save_results(results, paths["results_dir"])
    17. save_gate_result(results, ...) → exit(0 if PASS else 1)
    """
    ...

# tests/ — one representative signature per module test
# tests/test_ingest.py
def test_load_he1_scores_valid_csv() -> None: ...
def test_fetch_run_timestamps_cache_hit() -> None: ...
def test_build_merged_cohort_min_run_filter() -> None: ...

# tests/test_matching.py
def test_fit_propensity_model_returns_probabilities() -> None: ...
def test_nearest_neighbor_match_respects_caliper() -> None: ...
def test_compute_smd_reduces_after_matching() -> None: ...

# tests/test_ablation.py
def test_run_ablation_a_returns_required_keys() -> None: ...
def test_run_ablation_b_uses_accessible_score() -> None: ...
def test_run_all_ablations_returns_three_labels() -> None: ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description | Epic |
|----|---------|-------------|------|
| L-12-1 | main() orchestration | Wire all src modules in correct order; exit code logic based on gate metrics | A-12 |
| L-12-2 | Unit tests (ingest + matching) | test_ingest.py (3 tests), test_matching.py (3 tests) with mocked OpenML API | A-12 |
| L-12-3 | Unit tests (ablation + smoke test) | test_ablation.py (3 tests); smoke_test.py end-to-end with cached fixture data | A-12 |

### Pseudo-code (main gate evaluation)

```
gate_pass = (km_results["log_rank_p"] < cfg.LOG_RANK_ALPHA and
             km_results["median_ttfr_high"] < km_results["median_ttfr_low"])
secondary_pass = cox_results["cox_hr"] > cfg.COX_HR_GATE
save_gate_result(results, paths["results_dir"], cfg.LOG_RANK_ALPHA, cfg.COX_HR_GATE)
sys.exit(0 if gate_pass else 1)
```

---

## Remaining Modules API (Medium Complexity — No Subtask Budget)

### config.py

```python
H_E1_SCORES_CSV: str = "../h-e1/code/results/fair_scores.csv"
OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
MIN_RUN_COUNT: int = 10
OBSERVATION_WINDOW_DAYS: int = 730
CALIPER_FACTOR: float = 0.2
CALIPER_RELAXED_FACTOR: float = 0.3
MIN_MATCHED_PAIRS: int = 100
LOG_RANK_ALPHA: float = 0.05
COX_HR_GATE: float = 1.2
SMD_THRESHOLD: float = 0.1
SEED: int = 42
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
F1_PID_WEIGHT: float = 0.25
F2_METADATA_WEIGHT: float = 0.50
F3_SEARCH_WEIGHT: float = 0.25

def parse_args() -> argparse.Namespace: ...
def resolve_paths(args) -> dict: ...
```

### src/findable.py

```python
def compute_f1_pid(cohort: pd.DataFrame) -> pd.Series: ...
    # Returns Series[float] 0.0 or 1.0 indexed by cohort.index

def compute_f2_metadata(cohort: pd.DataFrame) -> pd.Series: ...
    # proportion of non-null: title, description, tags, creator, license

def compute_f3_search_indexed(cohort: pd.DataFrame) -> pd.Series: ...
    # 1.0 if has tags/categories else 0.0

def compute_findable_score(
    cohort: pd.DataFrame,
    f1_weight: float,
    f2_weight: float,
    f3_weight: float,
) -> pd.DataFrame: ...
    # Adds: F1_PID, F2_metadata, F3_search_indexed, findable_score, high_findable
    # high_findable = (findable_score > median).astype(int)

def compute_accessible_score(cohort: pd.DataFrame) -> pd.Series: ...
    # 0.5 * A1_open_license + 0.5 * A2_standard_format proxies
```

### src/survival_prep.py

```python
def compute_time_to_first_run(cohort: pd.DataFrame, observation_window_days: int) -> pd.DataFrame: ...
    # Adds: time_to_first_run (days, capped at window), event (0/1)

def encode_covariates(cohort: pd.DataFrame) -> pd.DataFrame: ...
    # Adds: creation_year_quartile (int 1-4), task_type_encoded (int), size_decile (int 1-10)

def build_survival_df(cohort: pd.DataFrame, observation_window_days: int) -> pd.DataFrame: ...
    # Calls compute_time_to_first_run + encode_covariates; returns full survival DataFrame

def validate_preconditions(survival_df: pd.DataFrame, cfg) -> dict: ...
    # Returns dict[mechanism_exists: bool, mechanism_isolatable: bool,
    #              baseline_measurable: bool, n_with_runs: int]
```

### src/km_analysis.py

```python
def run_km_unadjusted(
    survival_df: pd.DataFrame,
    treatment_col: str = "high_findable",
) -> dict: ...
    # Returns dict[baseline_log_rank_p, baseline_cox_hr, median_ttfr_high_unadj,
    #              median_ttfr_low_unadj, kmf_high, kmf_low]

def run_km_matched(
    matched_df: pd.DataFrame,
    treatment_col: str = "high_findable",
) -> dict: ...
    # Returns dict[log_rank_p, median_ttfr_high, median_ttfr_low, kmf_high, kmf_low]
```

### src/cox_analysis.py

```python
def fit_cox(
    matched_df: pd.DataFrame,
    formula: str,
    duration_col: str = "time_to_first_run",
    event_col: str = "event",
) -> tuple[Any, float, float, float]: ...
    # Returns (cph_model, cox_hr, cox_ci_lower, cox_ci_upper)

def check_ph_assumption(cph_model, matched_df: pd.DataFrame, p_threshold: float = 0.05) -> dict: ...
    # Returns dict[ph_violated: bool, schoenfeld_p: float, recommendation: str]

def run_cox_primary(
    matched_df: pd.DataFrame,
    predictor_col: str = "findable_score",
) -> dict: ...
    # Returns dict[cox_hr, cox_ci_lower, cox_ci_upper, cox_p, ph_check]
```

### src/sensitivity.py

```python
def run_sa1_fuji_threshold(survival_df: pd.DataFrame, cfg) -> dict: ...
def run_sa2_ph_check(matched_df: pd.DataFrame, cph_model, cfg) -> dict: ...
def run_sa3_observation_windows(
    survival_df: pd.DataFrame, cfg, windows: list[int] = None
) -> list[dict]: ...
    # windows default = [180, 365, 730]; each dict[window_days, log_rank_p, cox_hr]
def run_all_sensitivity(survival_df, matched_df, cph_model, cfg) -> dict: ...
```

### src/visualize.py

```python
def plot_gate_metrics(log_rank_p: float, cox_hr: float, figures_dir: str) -> str: ...
def plot_km_curves(kmf_high, kmf_low, log_rank_p: float, median_high: float,
                   median_low: float, figures_dir: str, label: str = "matched") -> str: ...
def plot_ps_distribution(ps_before: pd.Series, ps_after: pd.Series, figures_dir: str) -> str: ...
def plot_love_plot(smd_df: pd.DataFrame, figures_dir: str) -> str: ...
def plot_cox_forest(cox_hr: float, cox_ci_lower: float, cox_ci_upper: float, figures_dir: str) -> str: ...
def plot_sensitivity_comparison(primary: dict, ablations: dict, figures_dir: str) -> str: ...
def generate_all_figures(results: dict, figures_dir: str) -> list[str]: ...
```

### src/serialize.py

```python
def build_results_dict(primary: dict, unadjusted: dict, matching_meta: dict,
                       ablations: dict, sensitivity: dict) -> dict: ...
    # Canonical schema per FR-9: log_rank_p, cox_hr, median_ttfr_high/low,
    # n_matched_pairs, smd_max, n_cohort_filtered, baseline_log_rank_p, baseline_cox_hr

def save_results(results: dict, results_dir: str) -> dict: ...
    # Returns dict[json_path, csv_path]

def save_gate_result(results: dict, results_dir: str,
                     log_rank_alpha: float, cox_hr_gate: float) -> str: ...
    # Returns path to gate_result.json; includes PASS/FAIL determination
```

---

## Data Shapes Reference

| Variable | Type | Key Columns |
|----------|------|-------------|
| he1_scores | DataFrame[N~5000] | did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, status |
| run_data | DataFrame[N~5000] | did, first_run_timestamp, run_count |
| metadata | DataFrame[N~5000] | did, upload_date, task_type, NumberOfInstances |
| cohort (post-merge, post-filter) | DataFrame[N~500-1500] | all above merged |
| survival_df | DataFrame[N~500-1500] | + findable_score, high_findable, time_to_first_run, event, covariates |
| matched_df | DataFrame[2*n_pairs] | survival_df columns + pair_id |
| smd_df | DataFrame[3 rows] | covariate, smd_before, smd_after |
