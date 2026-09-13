---
hypothesis_id: H-M1
document_type: config
phase: "Phase 3"
date: "2026-08-25"
---

# Config: H-M1 — Temporal Structure Analysis

Applied: inline-constants-dict (statistical pipeline, no tunable hyperparameters)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no existing code/ dir to analyze)
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict / module-level constants in run.py

---

## C-E2-1: Data Loading Configuration [Complexity: 7, Budget: 1 subtask]

### Inline Constants (run.py)

```python
# --- Column spec ---
CSV_COL_MONTHS     = "months"        # dtype: int64, months since benchmark release
CSV_COL_SCORE      = "monthly_max"   # dtype: float64, normalized composite score [0, 1]

# --- Validation thresholds ---
MIN_MONTHS_SPAN = 24     # minimum (max - min) months in loaded series
MIN_OBS         = 20     # minimum number of monthly rows
MIN_SCORE_STD   = 0.001  # minimum std of scores; below this = constant / degenerate series

# --- Error message templates ---
ERR_FILE_NOT_FOUND = (
    "H-E1 CSV not found at {path}. Re-run H-E1 data pipeline to regenerate it."
)
ERR_COL_MISSING = (
    "Required column '{col}' missing in {path}. Expected columns: months (int64), monthly_max (float64)."
)
ERR_TOO_FEW_OBS = (
    "Only {n} monthly observations in {path} (need >= {min_obs}). "
    "Re-run H-E1 with a wider date range."
)
ERR_SHORT_SPAN = (
    "Time span is {span} months in {path} (need >= {min_span}). "
    "Re-run H-E1 with a wider date range."
)
ERR_LOW_VARIANCE = (
    "Score std={std:.5f} in {path} is below {min_std} — series is effectively constant. "
    "Check H-E1 normalization step."
)
```

### load_timeseries() Contract

```python
def load_timeseries(csv_path: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns (times, scores) sorted ascending by months.
    times:  np.ndarray, int64, shape (N,)
    scores: np.ndarray, float64, shape (N,)

    Raises:
        FileNotFoundError  — if csv_path does not exist
        ValueError         — if required columns missing, too few obs,
                             short span, or degenerate variance
    Exit code caller should use: 2 (data error)
    """
```

### CLI Overrides for CSV Paths

Yes — argparse in main() provides `--glue-csv` and `--superglue-csv` to override defaults.
`load_timeseries()` itself takes a plain `str` path; CLI resolution happens in `main()`.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E2-1 | Data loading config | Column names, dtypes, validation thresholds, error templates, CLI path override strategy |

---

## C-E7-1: Experiment Runner Configuration and CLI [Complexity: 8, Budget: 1 subtask]

### Inline Constants (run.py)

```python
BENCHMARKS = {
    "glue":      "data/glue_timeseries_clean.csv",
    "superglue": "data/superglue_timeseries_clean.csv",
}
FIGURES_DIR  = "docs/youra_research/h-m1/figures"
RESULTS_JSON = "docs/youra_research/h-m1/results.json"

RHO_MONO_THRESHOLD  = 0.8
RHO_DECEL_THRESHOLD = -0.3

# Null baseline (FR-13)
BASELINE_RHO_MONO  = 0.0
BASELINE_RHO_DECEL = 0.0
```

### argparse Argument Definitions

```python
import argparse

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="H-M1: Temporal structure test for GLUE/SuperGLUE leaderboards."
    )
    p.add_argument(
        "--glue-csv",
        default=BENCHMARKS["glue"],
        help="Path to GLUE timeseries CSV (default: %(default)s)",
    )
    p.add_argument(
        "--superglue-csv",
        default=BENCHMARKS["superglue"],
        help="Path to SuperGLUE timeseries CSV (default: %(default)s)",
    )
    p.add_argument(
        "--out-dir",
        default="docs/youra_research/h-m1",
        help="Root output directory for results.json (default: %(default)s)",
    )
    p.add_argument(
        "--figures-dir",
        default=FIGURES_DIR,
        help="Directory for figure PNGs (default: %(default)s)",
    )
    return p.parse_args()
```

### Exit Code Mapping

| Code | Meaning | Condition |
|------|---------|-----------|
| 0 | PASS or PARTIAL | At least one benchmark passes both gate thresholds |
| 1 | FAIL | Neither benchmark passes; downstream hypotheses blocked |
| 2 | Data error | FileNotFoundError or ValueError from load_timeseries() |

### Results JSON Schema

```python
# Written by save_results_json(); exact field names:
{
    "overall_pass": bool,           # True if BOTH benchmarks pass
    "overall_verdict": str,         # "PASS" | "PARTIAL" | "FAIL"
    "benchmarks": {
        "<benchmark_id>": {         # "glue" or "superglue"
            "n_months": int,        # number of monthly observations
            "rho_monotonic": float, # spearmanr(times, scores)
            "rho_decel": float,     # spearmanr(gain_times, gains)
            "pre_post_ratio": float,# pre_gain_mean / post_gain_mean; np.inf if post <= 0
            "pass": bool,           # rho_monotonic > 0.8 AND rho_decel < -0.3
            "baseline_rho_monotonic": 0.0,  # null model reference (FR-13)
            "baseline_rho_decel": 0.0       # null model reference (FR-13)
        }
    }
}
```

### requirements.txt

```
numpy>=1.21
pandas>=1.3
scipy>=1.7
matplotlib>=3.4
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E7-1 | Runner config & CLI | argparse defs, defaults, exit codes, results JSON schema, requirements.txt |
