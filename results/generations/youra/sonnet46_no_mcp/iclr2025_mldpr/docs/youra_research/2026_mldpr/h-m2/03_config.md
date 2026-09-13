# Config: H-M2
# Accessible FAIR Dimension → 12-Month Run Count (OpenML)

Applied: statistical-observational-study-config pattern
Applied: propensity-score-matched-count-outcome pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m1)
**Status**: Config classes verified from actual h-m1 code (`h-m1/code/config.py`)
**Config Files Found**: `h-m1/code/config.py` — flat constants module, no dataclass
**Pattern Used**: hardcoded constants (flat module) + config.yaml — same style as h-m1

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual H-M1 Code — Verified)

```python
# From: h-m1/code/config.py (ACTUAL CODE — verified field names)
OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OPENML_TASK_TYPES: list = ["supervised_classification", "supervised_regression"]
H_E1_SCORES_CSV: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "results", "fair_scores.csv")
MIN_RUN_COUNT: int = 10
OBSERVATION_WINDOW_DAYS: int = 730   # h-m1 uses 730; h-m2 changes to 365
CALIPER_FACTOR: float = 0.2
CALIPER_RELAXED_FACTOR: float = 0.3  # h-m2 overrides relaxed to 0.8 per PRD
MIN_MATCHED_PAIRS: int = 100         # h-m2 overrides to 500 (production)
SMD_THRESHOLD: float = 0.1
SEED: int = 42
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
CACHE_DIR: str = "results/cache"
```

**Verified from**: `h-m1/code/config.py` (actual implementation). Key overrides in h-m2:
- `OBSERVATION_WINDOW_DAYS`: 730 → 365 (12-month window)
- `CALIPER_RELAXED_FACTOR`: 0.3 → 0.8 (PRD smoke test caliper)
- `MIN_MATCHED_PAIRS`: 100 → 500 (production gate requirement)
- Removes: `LOG_RANK_ALPHA`, `COX_HR_GATE`, `SCHOENFELD_ALPHA`, `F*_WEIGHT` constants
- Adds: `MWU_ALPHA`, `ACCESSIBLE_BETA_GATE`, `WINDOW_SHORT_DAYS`, `FAIR_SUB_CRITERIA_COLS`

---

## A-2: Data Ingestion Pipeline [Complexity: 10, Budget: 2 subtasks]

Applied: yaml-config-flat-constants pattern

### Configuration

```python
# config.py — Data ingestion constants (h-m2)
import os
import argparse

# Inherited from h-m1 (verified field names)
OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OPENML_TASK_TYPES: list = ["supervised_classification", "supervised_regression"]
H_E1_SCORES_CSV: str = os.path.join(
    os.path.dirname(__file__), "..", "..", "h-e1", "code", "results", "fair_scores.csv"
)

# H-M2 window (12 months instead of h-m1's 24 months)
OBSERVATION_WINDOW_DAYS: int = 365
WINDOW_SHORT_DAYS: int = 182          # Ablation B: 6-month sensitivity window

MIN_RUN_COUNT: int = 10
CACHE_DIR: str = "results/cache"
FAIR_SUB_CRITERIA_COLS: list = ["fair_F", "fair_A", "fair_I", "fair_R"]
```

```yaml
# config.yaml — data section
data:
  h_e1_scores_csv: "../h-e1/code/results/fair_scores.csv"
  openml_upload_date_min: "2018-01-01"
  task_types:
    - "supervised_classification"
    - "supervised_regression"
  window_days: 365
  window_short_days: 182
  min_run_count: 10
  cache_dir: "results/cache"
  fair_sub_criteria_cols:
    - "fair_F"
    - "fair_A"
    - "fair_I"
    - "fair_R"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | IngestReuse: load_he1_scores + fetch_run_timestamps | Reuse h-m1 ingest.py; configure H_E1_SCORES_CSV path; fetch run timestamps with OBSERVATION_WINDOW_DAYS=365 and CACHE_DIR |
| C-2-2 | IngestReuse: build_merged_cohort | Call build_merged_cohort with MIN_RUN_COUNT=10 gate; validate FAIR_SUB_CRITERIA_COLS present; confirm ~5000 cohort size |

---

## A-7: Visualization Module [Complexity: 12, Budget: 2 subtasks]

Applied: matplotlib-seaborn-figure-config pattern

### Configuration

```python
# config.py — Visualization constants
FIGURES_DIR: str = "figures"

# Figure settings (used in src/visualize.py)
FIG_DPI: int = 150
FIG_SIZE_DEFAULT: tuple = (8, 5)
FIG_SIZE_FOREST: tuple = (8, 6)     # OLS coefficient forest plot
FIG_SIZE_BOXPLOT: tuple = (7, 5)
FIG_PALETTE: dict = {
    "high": "#2196F3",   # blue — high Accessible group
    "low": "#F44336",    # red — low Accessible group
}
FIG_ALPHA: float = 0.7
FIG_FORMAT: str = "png"
```

```yaml
# config.yaml — visualization section
visualization:
  figures_dir: "figures"
  dpi: 150
  fig_size_default: [8, 5]
  fig_size_forest: [8, 6]
  fig_size_boxplot: [7, 5]
  palette:
    high: "#2196F3"
    low: "#F44336"
  alpha: 0.7
  format: "png"
  figure_names:
    - "fig1_gate_metrics.png"
    - "fig2_boxplot_12m_counts.png"
    - "fig3_ps_distribution.png"
    - "fig4_love_plot.png"
    - "fig5_ols_coefficients.png"
    - "fig6_window_sensitivity.png"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | VizConfig: gate_metrics + boxplot figures | Configure fig1_gate_metrics (p-value vs 0.05, beta vs 0.10 threshold bars) and fig2_boxplot_12m_counts (high/low matched groups) using FIG_PALETTE and FIG_DPI |
| C-7-2 | VizConfig: OLS forest + window sensitivity figures | Configure fig5_ols_coefficients (FIG_SIZE_FOREST, standardized beta bars with error bars) and fig6_window_sensitivity (p_6m vs p_12m comparison); dispatch generate_all_figures |

---

## A-8: Serialize + Gate Result [Complexity: 9, Budget: 2 subtasks]

Applied: gate-result-yaml-schema pattern

### Configuration

```python
# config.py — Analysis thresholds and gate constants
MWU_ALPHA: float = 0.05
ACCESSIBLE_BETA_GATE: float = 0.10
SMD_THRESHOLD: float = 0.1          # Inherited from h-m1 (verified)
RESULTS_DIR: str = "results"
```

```yaml
# config.yaml — analysis + output sections
analysis:
  mwu_alternative: "greater"
  ols_log_transform: true
  standardize_predictors: true
  significance_level: 0.05
  accessible_beta_threshold: 0.10

output:
  results_dir: "results"
  figures_dir: "figures"
  results_file: "results/results.json"
  gate_result_file: "results/gate_result.json"
```

Gate result YAML schema (written by `save_gate_result`):

```yaml
# results/gate_result.json (schema)
hypothesis: "h-m2"
gate_type: "SHOULD_WORK"
gate_passed: true          # bool: primary_pass AND direction_pass
primary_pass: true         # bool: mwu_p < 0.05
direction_pass: true       # bool: high_mean_12m > low_mean_12m
secondary_pass: true       # bool: accessible_beta > 0.10
mwu_stat: 125432.0
p_value: 0.0031
high_mean_12m: 14.2
low_mean_12m: 8.7
accessible_beta: 0.147
n_matched_pairs: 512
smd_max_after: 0.063
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | SerializeSchema: build_results_dict | Define h-m2 canonical results schema with primary_mwu, unadjusted_mwu, ols_results, matching_meta, ablations keys; use RESULTS_DIR for save_results (json + csv) |
| C-8-2 | GateResult: save_gate_result | Apply MWU_ALPHA=0.05 and ACCESSIBLE_BETA_GATE=0.10 gates; write gate_result.json with gate_passed, gate_type='SHOULD_WORK', direction_pass, secondary_pass fields |

---

## A-10: End-to-End Experiment Run [Complexity: 10, Budget: 2 subtasks]

Applied: smoke-test-synthetic-cohort pattern

### Configuration

```python
# config.py — Matching + smoke test constants
CALIPER_FACTOR: float = 0.2             # Production caliper (inherited from h-m1 verified)
CALIPER_RELAXED_FACTOR: float = 0.8    # Smoke test caliper (overrides h-m1's 0.3)
MIN_MATCHED_PAIRS: int = 500            # Production requirement (overrides h-m1's 100)
MIN_MATCHED_PAIRS_SMOKE: int = 30       # Smoke test minimum
SEED: int = 42                          # Inherited from h-m1 (verified)
```

```yaml
# config.yaml — matching + smoke_test sections
matching:
  caliper_production: 0.2
  caliper_smoke: 0.8
  seed: 42
  min_matched_pairs_smoke: 30
  min_matched_pairs_production: 500
  smd_threshold: 0.1
  matching_covariates:
    - "creation_year_quartile"
    - "task_type_encoded"
    - "size_decile"

smoke_test:
  enabled: true
  n_synthetic: 200
  synthetic_seed: 42

ablations:
  A:
    name: "aggregate_threshold_vs_median_split"
    use_aggregate_threshold: true
    threshold: 0.5
  B:
    name: "window_sensitivity"
    window_days_short: 182
  C:
    name: "caliper_sensitivity"
    caliper_values:
      - 0.2
      - 0.8

hypothesis:
  id: "h-m2"
  type: "MECHANISM"
  gate: "SHOULD_WORK"
```

### Full `config.py` (copy-paste ready)

```python
"""H-M2 — Accessible FAIR Dimension → 12-Month Run Count config."""
import os
import argparse

# --- Inherited from h-m1 (verified field names from h-m1/code/config.py) ---
OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OPENML_TASK_TYPES: list = ["supervised_classification", "supervised_regression"]
H_E1_SCORES_CSV: str = os.path.join(
    os.path.dirname(__file__), "..", "..", "h-e1", "code", "results", "fair_scores.csv"
)
MIN_RUN_COUNT: int = 10
SMD_THRESHOLD: float = 0.1
SEED: int = 42
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
CACHE_DIR: str = "results/cache"

# --- H-M2 specific (overrides or new) ---
OBSERVATION_WINDOW_DAYS: int = 365      # 12-month window (h-m1 used 730)
WINDOW_SHORT_DAYS: int = 182            # Ablation B: 6-month window
CALIPER_FACTOR: float = 0.2            # Production caliper (same as h-m1)
CALIPER_RELAXED_FACTOR: float = 0.8    # Smoke test caliper (h-m1 was 0.3)
MIN_MATCHED_PAIRS: int = 500            # Production gate (h-m1 was 100)
MIN_MATCHED_PAIRS_SMOKE: int = 30
MWU_ALPHA: float = 0.05
ACCESSIBLE_BETA_GATE: float = 0.10
FAIR_SUB_CRITERIA_COLS: list = ["fair_F", "fair_A", "fair_I", "fair_R"]

# --- Visualization ---
FIG_DPI: int = 150
FIG_SIZE_DEFAULT: tuple = (8, 5)
FIG_SIZE_FOREST: tuple = (8, 6)
FIG_SIZE_BOXPLOT: tuple = (7, 5)
FIG_PALETTE: dict = {"high": "#2196F3", "low": "#F44336"}
FIG_ALPHA: float = 0.7


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-M2 Accessible FAIR Run Count Analysis")
    parser.add_argument("--h-e1-scores-csv", type=str, default=H_E1_SCORES_CSV)
    parser.add_argument("--observation-window-days", type=int, default=OBSERVATION_WINDOW_DAYS)
    parser.add_argument("--caliper-factor", type=float, default=CALIPER_FACTOR)
    parser.add_argument("--caliper-relaxed-factor", type=float, default=CALIPER_RELAXED_FACTOR)
    parser.add_argument("--min-matched-pairs", type=int, default=MIN_MATCHED_PAIRS)
    parser.add_argument("--mwu-alpha", type=float, default=MWU_ALPHA)
    parser.add_argument("--accessible-beta-gate", type=float, default=ACCESSIBLE_BETA_GATE)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--results-dir", type=str, default=RESULTS_DIR)
    parser.add_argument("--figures-dir", type=str, default=FIGURES_DIR)
    parser.add_argument("--cache-dir", type=str, default=CACHE_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Run smoke test only (n=200)")
    return parser.parse_args()


def resolve_paths(args) -> dict:
    return {
        "he1_scores_csv":   args.h_e1_scores_csv,
        "analysis_csv":     os.path.join(args.results_dir, "analysis_data.csv"),
        "matched_csv":      os.path.join(args.results_dir, "matched_data.csv"),
        "results_json":     os.path.join(args.results_dir, "results.json"),
        "results_csv":      os.path.join(args.results_dir, "results.csv"),
        "gate_json":        os.path.join(args.results_dir, "gate_result.json"),
        "figures_dir":      args.figures_dir,
        "cache_dir":        args.cache_dir,
    }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | SmokeTest: synthetic cohort n=200 | Run full pipeline with --dry-run flag; use CALIPER_RELAXED_FACTOR=0.8, MIN_MATCHED_PAIRS_SMOKE=30, synthetic_seed=42; assert no exceptions and gate_result.json written |
| C-10-2 | ProductionRun: full cohort + gate evaluation | Run with CALIPER_FACTOR=0.2, MIN_MATCHED_PAIRS=500; verify MWU p-value against MWU_ALPHA=0.05; validate 6 figure files exist in FIGURES_DIR |
