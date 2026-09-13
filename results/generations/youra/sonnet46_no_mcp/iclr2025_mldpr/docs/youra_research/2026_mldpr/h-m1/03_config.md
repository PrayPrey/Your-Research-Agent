# Config: H-M1
# Findable FAIR Sub-Criteria → Time-to-First-Run Survival Analysis

**Applied**: Statistical observational study config pattern
**Applied**: Propensity-score-matched survival analysis hyperparameters pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (h-e1/code/config.py)
**Config Files Found**: `h-e1/code/config.py` — flat constants module, no dataclass
**Pattern Used**: hardcoded constants (flat module), same style for H-M1

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual H-E1 Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE - verified)
OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OPENML_TASK_TYPES: list = ["supervised_classification", "supervised_regression"]
FUJI_API_BASE: str = "http://localhost:1071"
FUJI_CONCURRENCY: int = 10
FUJI_RETRY_MAX: int = 3
FUJI_RETRY_BASE_S: float = 2.0
FAIR_THRESHOLD: float = 0.5
FAIR_N_SUBCRITERIA: int = 17
CV_GATE: float = 0.15
GROUP_SIZE_GATE: int = 500
SEED: int = 1                  # ← verified: H-E1 uses 1 (not 42)
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
CACHE_DIR: str = "results/fuji_cache"
```

**Verified from**: `h-e1/code/config.py` (actual implementation).
**Note**: H-E1 uses `SEED = 1`, not 42. H-M1 inherits SEED=42 as a new default per PRD.

---

## Experiment Configuration

### `config.py` (H-M1)

```python
"""
H-M1 — Findable FAIR Sub-Criteria → Time-to-First-Run Survival Analysis
Flat constants module (same style as H-E1).
"""
import os
import argparse

# --- Inherited from H-E1 (reused as-is) ---
OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OPENML_TASK_TYPES: list = ["supervised_classification", "supervised_regression"]

# --- H-E1 Output Reference ---
H_E1_SCORES_CSV: str = os.path.join(
    os.path.dirname(__file__), "..", "..", "h-e1", "code", "results", "fair_scores.csv"
)

# --- Cohort Filtering ---
MIN_RUN_COUNT: int = 10              # Minimum ML runs for dataset to enter cohort
OBSERVATION_WINDOW_DAYS: int = 730   # 2-year follow-up window

# --- Findable Sub-Score Weights ---
F1_PID_WEIGHT: float = 0.25          # F1: persistent identifier weight
F2_METADATA_WEIGHT: float = 0.50     # F2: rich metadata weight
F3_SEARCH_WEIGHT: float = 0.25       # F3: search-indexed weight

# --- Propensity Score Matching ---
CALIPER_FACTOR: float = 0.2          # Primary caliper = 0.2 * std(logit PS)
CALIPER_RELAXED_FACTOR: float = 0.3  # Relaxed caliper (fallback)
MIN_MATCHED_PAIRS: int = 100         # Minimum pairs; abort if below
SMD_THRESHOLD: float = 0.1           # Standardized mean difference balance gate

# --- Survival Analysis ---
LOG_RANK_ALPHA: float = 0.05         # Log-rank test significance level
COX_HR_GATE: float = 1.2             # Minimum HR magnitude to claim effect
SCHOENFELD_ALPHA: float = 0.05       # PH assumption Schoenfeld residuals alpha

# --- Reproducibility ---
SEED: int = 42

# --- I/O Paths ---
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-M1 Survival Analysis")
    parser.add_argument("--h-e1-scores-csv", type=str, default=H_E1_SCORES_CSV)
    parser.add_argument("--min-run-count", type=int, default=MIN_RUN_COUNT)
    parser.add_argument("--observation-window-days", type=int, default=OBSERVATION_WINDOW_DAYS)
    parser.add_argument("--caliper-factor", type=float, default=CALIPER_FACTOR)
    parser.add_argument("--caliper-relaxed-factor", type=float, default=CALIPER_RELAXED_FACTOR)
    parser.add_argument("--min-matched-pairs", type=int, default=MIN_MATCHED_PAIRS)
    parser.add_argument("--log-rank-alpha", type=float, default=LOG_RANK_ALPHA)
    parser.add_argument("--cox-hr-gate", type=float, default=COX_HR_GATE)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--results-dir", type=str, default=RESULTS_DIR)
    parser.add_argument("--figures-dir", type=str, default=FIGURES_DIR)
    return parser.parse_args()


def resolve_paths(args) -> dict:
    return {
        "survival_csv":     os.path.join(args.results_dir, "survival_data.csv"),
        "km_json":          os.path.join(args.results_dir, "km_results.json"),
        "cox_json":         os.path.join(args.results_dir, "cox_results.json"),
        "gate_json":        os.path.join(args.results_dir, "gate_result.json"),
        "figures_dir":      args.figures_dir,
    }
```

---

## YAML Schema

### `experiment_config.yaml`

```yaml
# H-M1 experiment configuration
hypothesis: h-m1
description: "Findable FAIR Sub-Criteria → Time-to-First-Run Survival Analysis"

data:
  h_e1_scores_csv: "../h-e1/code/results/fair_scores.csv"
  openml_upload_date_min: "2018-01-01"
  min_run_count: 10
  observation_window_days: 730

findable_weights:
  f1_pid: 0.25
  f2_metadata: 0.50
  f3_search: 0.25

matching:
  caliper_factor: 0.2
  caliper_relaxed_factor: 0.3
  min_matched_pairs: 100
  smd_threshold: 0.1

survival:
  log_rank_alpha: 0.05
  cox_hr_gate: 1.2
  schoenfeld_alpha: 0.05

reproducibility:
  seed: 42

output:
  results_dir: "results"
  figures_dir: "figures"
```

---

## Hyperparameter Reference Table

| Constant | Value | Source |
|----------|-------|--------|
| `OPENML_UPLOAD_DATE_MIN` | `"2018-01-01"` | Inherited H-E1 |
| `MIN_RUN_COUNT` | `10` | PRD gate |
| `OBSERVATION_WINDOW_DAYS` | `730` | PRD (2-year window) |
| `F1_PID_WEIGHT` | `0.25` | Architecture |
| `F2_METADATA_WEIGHT` | `0.50` | Architecture |
| `F3_SEARCH_WEIGHT` | `0.25` | Architecture |
| `CALIPER_FACTOR` | `0.2` | Standard PSM practice |
| `CALIPER_RELAXED_FACTOR` | `0.3` | Architecture |
| `MIN_MATCHED_PAIRS` | `100` | Architecture |
| `SMD_THRESHOLD` | `0.1` | Standard balance criterion |
| `LOG_RANK_ALPHA` | `0.05` | Standard significance |
| `COX_HR_GATE` | `1.2` | Architecture gate |
| `SCHOENFELD_ALPHA` | `0.05` | PH assumption test |
| `SEED` | `42` | PRD (H-M1 new default) |

---

## Subtasks

Budget: 6 subtasks across A-3, A-4, A-6, A-7.

| ID | Epic | Subtask | Description |
|----|------|---------|-------------|
| C-3-1 | A-3 | FindableExtractor: F1+F2 | Compute F1_pid and F2_metadata scores from H-E1 CSV columns `fair_F`; apply weights `F1_PID_WEIGHT`, `F2_METADATA_WEIGHT` |
| C-3-2 | A-3 | FindableExtractor: F3+composite | Compute F3_search_indexed flag; combine F1+F2+F3 into weighted Findable composite; output `findable_score` column |
| C-4-1 | A-4 | SurvivalPreparer: TTFR + censoring | Fetch first-run timestamps per dataset from OpenML runs API; compute TTFR in days; apply `OBSERVATION_WINDOW_DAYS` right-censoring |
| C-4-2 | A-4 | SurvivalPreparer: covariate encoding | Encode covariates (n_features, n_rows, task_type, upload_year); validate `MIN_RUN_COUNT` gate; output survival DataFrame |
| C-6-1 | A-6 | KaplanMeierAnalyzer: unadjusted KM | Run unadjusted KM on high vs low Findable groups; log-rank test at `LOG_RANK_ALPHA`; output KM curves + p-value |
| C-7-1 | A-7 | CoxPHAnalyzer: CoxPH + PH check | Fit `CoxPHFitter` on matched pairs with covariates; verify HR >= `COX_HR_GATE`; run Schoenfeld residuals test at `SCHOENFELD_ALPHA` |
