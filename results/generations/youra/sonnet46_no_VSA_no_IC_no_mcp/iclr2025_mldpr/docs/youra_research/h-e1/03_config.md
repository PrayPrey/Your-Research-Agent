---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
phase: "Phase 3"
date: "2026-08-25"
---

# Config: H-E1 — Logistic Growth Fit on Papers With Code

Applied: scipy-curve_fit-bounded-logistic (standard bounded 3-param logistic fitting pattern)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze. Serena skipped.
**Config Files Found**: None — new config
**Pattern Used**: hardcoded dict (inline constants in run.py per architecture)

---

## A-E2: Data Retrieval Config [Complexity: 8, Budget: 1 subtask]

Applied: exponential-backoff-retry (standard API resilience pattern)

```python
# Inline constants in run.py

BENCHMARKS = {
    "glue":       {"release_date": "2019-02-01"},
    "super-glue": {"release_date": "2019-05-01"},
}

# API retry settings
MAX_RETRIES = 3        # valid: 1–10
BACKOFF_BASE = 2.0     # seconds; exponential: base^attempt; valid: 1.0–5.0
BACKOFF_MAX = 30.0     # seconds cap; valid: 10.0–120.0
```

| Name | Type | Default | Valid Range | Description |
|------|------|---------|-------------|-------------|
| MAX_RETRIES | int | 3 | 1–10 | Retry attempts on API failure |
| BACKOFF_BASE | float | 2.0 | 1.0–5.0 | Exponential backoff base (seconds) |
| BACKOFF_MAX | float | 30.0 | 10.0–120.0 | Backoff ceiling (seconds) |
| BENCHMARKS | dict | see above | fixed | benchmark_id → release_date mapping |

### Subtasks [1/1 used]

| ID | Subtask | Parent Epic | Description |
|----|---------|-------------|-------------|
| C-E2-1 | API retry config | E2 | Wire MAX_RETRIES, BACKOFF_BASE, BACKOFF_MAX into fetch_benchmark(); verify exponential sleep = min(BACKOFF_BASE**attempt, BACKOFF_MAX) |

---

## A-E6: Evaluation & Output Config [Complexity: 7, Budget: 1 subtask]

Applied: json-results-dump (standard experiment results serialization pattern)

```python
# Inline constants in run.py

# Gate threshold
R2_THRESHOLD = 0.9     # valid: 0.0–1.0; MUST_WORK gate

# Preprocessing
MIN_DATE = "2019-01-01"   # ISO date string
MIN_ENTRIES = 50           # valid: 1–1000; eligibility criterion post-dedup

# curve_fit parameters
CURVE_FIT_P0_TEMPLATE = [0.9, 0.5, None]   # None = median(t) filled at runtime
CURVE_FIT_BOUNDS = ([0.8, 0.01, 0.0], [1.05, 5.0, 60.0])
# K: [0.8, 1.05], r: [0.01, 5.0], t0: [0.0, 60.0] months
CURVE_FIT_MAXFEV = 10000   # valid: 1000–100000

# Output paths
FIGURES_DIR = "docs/youra_research/h-e1/figures"
RESULTS_JSON = "docs/youra_research/h-e1/results.json"

# Visualization
FIG_SIZE = (10, 6)     # inches (width, height)
FIG_DPI = 150          # valid: 72–300
COLOR_DATA = "#1f77b4"     # matplotlib default blue
COLOR_FIT = "#d62728"      # matplotlib default red
COLOR_LINEAR = "#7f7f7f"   # gray for linear baseline
THRESHOLD_LINE_COLOR = "#2ca02c"  # green for R²=0.9 line
```

| Name | Type | Default | Valid Range | Description |
|------|------|---------|-------------|-------------|
| R2_THRESHOLD | float | 0.9 | 0.0–1.0 | Gate: logistic fit must exceed this R² |
| MIN_DATE | str | "2019-01-01" | ISO date | Drop entries before this date |
| MIN_ENTRIES | int | 50 | 1–1000 | Minimum post-dedup entries for eligibility |
| CURVE_FIT_P0_TEMPLATE | list | [0.9, 0.5, None] | — | Initial guess; None replaced by median(t) |
| CURVE_FIT_BOUNDS | tuple | ([0.8,0.01,0.0],[1.05,5.0,60.0]) | — | K, r, t0 search bounds |
| CURVE_FIT_MAXFEV | int | 10000 | 1000–100000 | Max function evaluations for curve_fit |
| FIGURES_DIR | str | see above | valid path | Output directory for all figures |
| RESULTS_JSON | str | see above | valid path | Output path for results JSON |
| FIG_SIZE | tuple | (10, 6) | inches | Matplotlib figure size |
| FIG_DPI | int | 150 | 72–300 | Figure resolution |

### Subtasks [1/1 used]

| ID | Subtask | Parent Epic | Description |
|----|---------|-------------|-------------|
| C-E6-1 | Results output config | E6 | Wire FIGURES_DIR, RESULTS_JSON, R2_THRESHOLD into evaluate() and main(); ensure figures dir is created at runtime with os.makedirs(exist_ok=True) |
