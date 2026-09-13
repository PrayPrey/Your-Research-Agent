# H-M2 Configuration

Applied: hardcoded-constants pattern (matching H-E1/H-M1 module-level constants style)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config constants verified from actual H-E1 and H-M1 code
**Config Files Found**: `h-e1/code/fitting.py`, `h-m1/code/run.py`
**Pattern Used**: module-level constants (no dataclass — matches existing codebase style)

---

## Inherited Configuration

### From H-E1 `fitting.py` (Actual Code)

```python
# Verified field names and defaults from h-e1/code/fitting.py

# Logistic curve_fit params (actual values in code):
LOGISTIC_P0     = [0.9, 0.5, None]   # None = float(np.median(t) * 0.3) at runtime
LOGISTIC_BOUNDS = ([0.8, 0.01, -20.0], [1.05, 5.0, 60.0])
LOGISTIC_MAXFEV = 10000              # actual value in fitting.py

# AIC formula: n * log(ss_res/n) + 2*k  (k=2 linear, k=3 logistic)
# Linear fit: np.polyfit(t, y, deg=1) — closed-form, no bounds
```

**Note**: H-E1 uses `maxfev=10000` (not 5000 as in task context). H-M2 uses 5000 per spec — this is a deliberate tighter budget for power-law fitting.

---

## H-M2 Constants

```python
# h-m2/code/config.py

# --- Data paths ---
DATA_DIR    = "../h-e1/code/data/"
FIGURES_DIR = "docs/youra_research/h-m2/figures"
RESULTS_JSON = "docs/youra_research/h-m2/results.json"

BENCHMARKS = {
    "glue":      DATA_DIR + "glue_timeseries_clean.csv",
    "superglue": DATA_DIR + "superglue_timeseries_clean.csv",
}

# --- Logistic fit (inherited from H-E1, adjusted bounds per spec) ---
LOGISTIC_P0     = [0.95, 0.5, 18.0]
LOGISTIC_BOUNDS = ([0.8, 0.1, 6.0], [1.0, 2.0, 36.0])
LOGISTIC_MAXFEV = 5000

# --- Power law fit: score = a * t^b ---
POWER_P0     = [0.5, 0.3]
POWER_BOUNDS = ([0.0, 0.0], [2.0, 1.0])
POWER_MAXFEV = 5000

# --- Linear fit: OLS via np.polyfit(t, y, deg=1), no bounds ---

# --- AIC gate thresholds (delta_AIC = AIC_logistic - AIC_linear) ---
AIC_PRIMARY_THRESHOLD   = -4   # strong preference for logistic
AIC_SECONDARY_THRESHOLD = -2   # moderate preference

# --- CSV columns (inherited from H-M1) ---
CSV_COL_MONTHS = "months"
CSV_COL_SCORE  = "monthly_max"
```

---

## Subtasks

Budget: 0 config-specific subtasks — all merged into epic tasks.
