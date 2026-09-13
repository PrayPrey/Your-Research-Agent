# Architecture: h-m2
## Accessible FAIR Dimension → 12-Month Run Count (OpenML)

Applied: propensity-matched-observational-study pattern
Applied: non-parametric-count-outcome-analysis pattern
Applied: incremental-hypothesis-codebase-reuse pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260504_mldpr/h-m1/code/`
**Findings**: h-m1 uses ingest→prep→match→analyze→serialize→visualize pipeline. `run_matching()` hardcodes `treatment_col="high_findable"` — must be parameterized or overridden for h-m2. `build_results_dict()` is h-m1-specific schema; h-m2 needs its own serialize schema. `generate_all_figures()` dispatches KM/Cox figures — will be replaced with MWU/OLS figures.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_he1_scores | `from src.ingest import load_he1_scores` | `h-m1/code/src/ingest.py` |
| fetch_run_timestamps | `from src.ingest import fetch_run_timestamps` | `h-m1/code/src/ingest.py` |
| fetch_dataset_metadata | `from src.ingest import fetch_dataset_metadata` | `h-m1/code/src/ingest.py` |
| build_merged_cohort | `from src.ingest import build_merged_cohort` | `h-m1/code/src/ingest.py` |
| fit_propensity_model | `from src.matching import fit_propensity_model` | `h-m1/code/src/matching.py` |
| nearest_neighbor_match | `from src.matching import nearest_neighbor_match` | `h-m1/code/src/matching.py` |
| compute_smd | `from src.matching import compute_smd` | `h-m1/code/src/matching.py` |
| run_matching | `from src.matching import run_matching` | `h-m1/code/src/matching.py` |
| encode_covariates | `from src.survival_prep import encode_covariates` | `h-m1/code/src/survival_prep.py` |
| plot_ps_distribution | `from src.visualize import plot_ps_distribution` | `h-m1/code/src/visualize.py` |
| plot_love_plot | `from src.visualize import plot_love_plot` | `h-m1/code/src/visualize.py` |

**Verified from**: `h-m1/code/` (actual implementation)

**CRITICAL NOTE**: `run_matching()` in h-m1 hardcodes `treatment_col="high_findable"`. h-m2 must pass `treatment_col="high_accessible"` — requires wrapper or direct calls to `fit_propensity_model` + `nearest_neighbor_match` + `compute_smd`.

---

## File Structure

```
h-m2/code/
  src/
    ingest.py          # Symlink/copy from h-m1 (reused)
    matching.py        # Symlink/copy from h-m1 (reused)
    accessible_prep.py # NEW
    mwu_analysis.py    # NEW
    serialize.py       # NEW (h-m2 schema)
    visualize.py       # NEW (h-m2 figures)
  tests/
    test_accessible_prep.py
    test_mwu_analysis.py
    test_integration.py
  run_experiment.py
  config.py
```

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: stdlib only

```python
OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OBSERVATION_WINDOW_DAYS: int = 365
WINDOW_SHORT_DAYS: int = 182
CALIPER_FACTOR: float = 0.2
CALIPER_RELAXED_FACTOR: float = 0.8
MIN_MATCHED_PAIRS: int = 100
MIN_MATCHED_PAIRS_SMOKE: int = 30
SMD_THRESHOLD: float = 0.1
MWU_ALPHA: float = 0.05
ACCESSIBLE_BETA_GATE: float = 0.10
SEED: int = 42
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
CACHE_DIR: str = "results/cache"
H_E1_SCORES_CSV: str = "../h-e1/code/results/fair_scores.csv"
FAIR_SUB_CRITERIA_COLS: list = ["fair_F", "fair_A", "fair_I", "fair_R"]

def parse_args() -> argparse.Namespace: ...
def resolve_paths(args) -> dict: ...
```

---

### AccessiblePrep (`src/accessible_prep.py`)

**Dependencies**: ingest (h-m1), encode_covariates (h-m1 survival_prep)

```python
def compute_12m_run_counts(
    cohort: pd.DataFrame,
    run_timestamps: pd.DataFrame,
    window_days: int = 365,
) -> pd.DataFrame:
    """Add run_count_12m column. run_timestamps must have [did, upload_time]."""
    ...

def compute_accessible_score(
    cohort: pd.DataFrame,
) -> pd.DataFrame:
    """Extract fair_A column as accessible_score; compute median split → high_accessible (0/1)."""
    ...

def build_analysis_df(
    cohort: pd.DataFrame,
    run_timestamps: pd.DataFrame,
    window_days: int = 365,
) -> pd.DataFrame:
    """Full prep: compute_12m_run_counts → compute_accessible_score → encode_covariates.
    Returns DataFrame with: run_count_12m, accessible_score, high_accessible,
    creation_year_quartile, task_type_encoded, size_decile.
    """
    ...

def validate_preconditions(analysis_df: pd.DataFrame, cfg) -> dict:
    """Check mechanism_exists (CV fair_A > 0.1), mechanism_isolatable (n >= 2*min_pairs),
    baseline_measurable (n_with_runs >= 50).
    Returns dict of bool flags + numeric values.
    """
    ...
```

---

### MwuAnalysis (`src/mwu_analysis.py`)

**Dependencies**: scipy, statsmodels, sklearn

```python
def run_mwu_unadjusted(
    analysis_df: pd.DataFrame,
    dv_col: str = "run_count_12m",
    treatment_col: str = "high_accessible",
) -> dict:
    """Baseline MWU on unmatched groups. Returns {mwu_stat, p_value, n_high, n_low, effect_size_r}."""
    ...

def run_mwu_matched(
    matched_df: pd.DataFrame,
    dv_col: str = "run_count_12m",
    treatment_col: str = "high_accessible",
) -> dict:
    """Primary MWU on matched groups (alternative='greater').
    Returns {mwu_stat, p_value, n_high, n_low, high_mean, low_mean, effect_size_r}.
    """
    ...

def run_ols_standardized(
    df: pd.DataFrame,
    fair_cols: list,
    dv_col: str = "run_count_12m",
) -> dict:
    """OLS with log1p(DV) and StandardScaler predictors.
    Returns {betas: dict[col→float], pvalues: dict[col→float], r_squared: float,
    accessible_beta: float, accessible_pvalue: float}.
    """
    ...

def run_mechanism_check(results: dict) -> None:
    """Assert n_matched_pairs >= 30, smd_max_after < 0.1, high_mean >= 0.
    Print mechanism check log line.
    """
    ...
```

---

### Serialize (`src/serialize.py`)

**Dependencies**: stdlib, numpy, pandas

```python
def build_results_dict(
    primary_mwu: dict,
    unadjusted_mwu: dict,
    ols_results: dict,
    matching_meta: dict,
    ablations: dict,
) -> dict:
    """Assemble h-m2 canonical results schema."""
    ...

def save_results(results: dict, results_dir: str) -> dict:
    """Save results.json + results.csv. Returns {json_path, csv_path}."""
    ...

def save_gate_result(
    results: dict,
    results_dir: str,
    mwu_alpha: float = 0.05,
    beta_gate: float = 0.10,
) -> str:
    """Save gate_result.json. PRIMARY: p < mwu_alpha AND direction.
    SECONDARY: accessible_beta > beta_gate. Returns path.
    """
    ...
```

---

### Visualize (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, pandas, numpy; plot_ps_distribution + plot_love_plot imported from h-m1

```python
def plot_gate_metrics(
    mwu_p: float,
    accessible_beta: float,
    figures_dir: str,
) -> str:
    """fig1_gate_metrics.png — p-value vs 0.05 threshold + beta vs 0.10 threshold."""
    ...

def plot_boxplot_12m_counts(
    matched_df: pd.DataFrame,
    dv_col: str,
    treatment_col: str,
    figures_dir: str,
) -> str:
    """fig2_boxplot_12m_counts.png — box plot high vs low Accessible matched groups."""
    ...

def plot_ps_distribution(ps_before: pd.Series, ps_after: pd.Series, figures_dir: str) -> str:
    """fig3_ps_distribution.png — reused from h-m1 visualize logic."""
    ...

def plot_love_plot(smd_df: pd.DataFrame, figures_dir: str) -> str:
    """fig4_love_plot.png — reused from h-m1 visualize logic."""
    ...

def plot_ols_coefficients(
    betas: dict,
    pvalues: dict,
    figures_dir: str,
) -> str:
    """fig5_ols_coefficients.png — standardized beta forest plot for all F-UJI sub-criteria."""
    ...

def plot_window_sensitivity(
    p_6m: float,
    p_12m: float,
    figures_dir: str,
) -> str:
    """fig6_window_sensitivity.png — p-value comparison 6-month vs 12-month windows."""
    ...

def generate_all_figures(results: dict, figures_dir: str) -> list:
    """Dispatch all 6 figure generators. Returns list of saved paths."""
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: all src modules, config

```python
def run_ablation_a(analysis_df: pd.DataFrame, cfg) -> dict:
    """Ablation A: F-UJI aggregate threshold (>=0.5) vs median Accessible split."""
    ...

def run_ablation_b(cohort: pd.DataFrame, run_timestamps: pd.DataFrame, cfg) -> dict:
    """Ablation B: 6-month window vs 12-month window."""
    ...

def run_ablation_c(analysis_df: pd.DataFrame, cfg) -> dict:
    """Ablation C: relaxed caliper (0.8) vs strict caliper (0.2)."""
    ...

def main() -> None:
    """CLI entry: ingest → prep → match → analyze → ablations → visualize → serialize."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Config, requirements.txt, directory scaffold, h-m1 module symlinks/copies | 6 | 1+1+2+2 |
| A-2 | Data Ingestion Pipeline | Reuse h-m1 ingest.py; fetch run timestamps with 12-month window caching; build merged cohort | 10 | 2+3+3+2 |
| A-3 | AccessiblePrep Module | compute_12m_run_counts, compute_accessible_score (median split), build_analysis_df, validate_preconditions | 12 | 3+2+4+3 |
| A-4 | Matching Pipeline Integration | Adapt h-m1 run_matching for treatment_col="high_accessible"; wrapper to pass correct args; SMD validation | 11 | 2+3+3+3 |
| A-5 | MWU Analysis Module | run_mwu_unadjusted + run_mwu_matched (scipy) + run_ols_standardized (statsmodels+sklearn) + run_mechanism_check | 14 | 3+3+5+3 |
| A-6 | Ablation Experiments | Ablation A (aggregate threshold), B (6-month window), C (caliper sensitivity); integrate in run_experiment.py | 13 | 3+3+4+3 |
| A-7 | Visualization Module | 6 new figures (gate metrics, boxplot, PS distribution, love plot, OLS forest, window sensitivity) | 12 | 3+2+4+3 |
| A-8 | Serialize + Gate Result | h-m2 schema build_results_dict, save_results, save_gate_result (MWU p + direction + beta gates) | 9 | 2+2+3+2 |
| A-9 | Unit Tests | test_accessible_prep (≥10 tests), test_mwu_analysis (≥10 tests), test_integration smoke n=200 (≥5 tests) | 13 | 3+2+4+4 |
| A-10 | End-to-End Experiment Run | Smoke test (n=200 synthetic), production run (full cohort), gate evaluation, figures validation | 10 | 2+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-3, A-4, A-6, A-7, A-9, A-10], Low(4-8): [A-1, A-2, A-8]

---

## Data Flow

- `run_experiment.py` → `ingest.py`: load_he1_scores → fetch_run_timestamps → fetch_dataset_metadata → build_merged_cohort
- `run_experiment.py` → `accessible_prep.py`: build_analysis_df (adds run_count_12m, high_accessible, covariates)
- `run_experiment.py` → `matching.py`: fit_propensity_model + nearest_neighbor_match + compute_smd (with treatment_col="high_accessible")
- `run_experiment.py` → `mwu_analysis.py`: run_mwu_unadjusted → run_mwu_matched → run_ols_standardized → run_mechanism_check
- `run_experiment.py` → ablation functions → same mwu_analysis pipeline with variant configs
- `run_experiment.py` → `visualize.py`: generate_all_figures(results, figures_dir)
- `run_experiment.py` → `serialize.py`: build_results_dict → save_results → save_gate_result

---

## Matching Adaptation Note

h-m1 `run_matching()` hardcodes `treatment_col="high_findable"` (line 116 in matching.py). h-m2 must NOT call `run_matching()` directly. Instead call the three underlying functions:

```python
model, ps_scores = fit_propensity_model(analysis_df, covariate_cols, "high_accessible", seed)
matched_df = nearest_neighbor_match(analysis_df, ps_scores, "high_accessible", caliper)
smd_df = compute_smd(analysis_df, matched_df, covariate_cols, "high_accessible")
```
