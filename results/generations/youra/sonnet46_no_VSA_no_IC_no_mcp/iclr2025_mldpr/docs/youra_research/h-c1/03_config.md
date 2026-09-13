# H-C1 Configuration

Applied: single-file constants dict pattern (flat script, no dataclass overhead)
Applied: h-m4 verified field names from actual run.py (logistic bounds, p0, bootstrap n)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config verified from actual h-m4 code (run.py read directly)
**Config Files Found**: `docs/youra_research/h-m4/code/run.py` — flat constants, no dataclass
**Pattern Used**: module-level constants dict

---

## Inherited Configuration (Base Hypothesis)

From `docs/youra_research/h-m4/code/run.py` (actual code, verified):

```python
# verbatim from h-m4/code/run.py
GROUND_TRUTH = {"glue": "2019-09", "superglue": "2021-06"}
LAUNCH_DATES  = {"glue": "2018-04", "superglue": "2019-05"}
DATA_DIR      = Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/data")

# H-M4 extract_params defaults (DO NOT reuse for H-C1 fitting — use FIT_CONFIG below)
# p0      = [0.92, 0.15, 12.0]
# bounds  = ([0.5, 0.01, -24], [1.05, 3.0, 72])
# maxfev  = 10000
# bootstrap n = 500, seed = 42
```

H-C1 uses a **separate** `fit_and_evaluate()` with tighter bounds (see C1-5a below).

---

## C1-7b: Experiment Constants [Complexity: 2, Budget: 1 subtask]

Applied: hardcoded dict for all top-level constants

```python
# ---------------------------------------------------------------------------
# H-C1 Experiment Constants
# ---------------------------------------------------------------------------

# Benchmark discovery filters
DISCOVERY = {
    "min_entries": 30,
    "max_entries": 49,
    "min_year":    2019,
}

# Logistic fitting (H-C1 tighter bounds per experiment brief)
FIT_CONFIG = {
    "p0":     [0.92, 0.15, 18.0],   # Non-standard: t0 init=18 (mid of [6,48] range)
    "bounds": ([0.8, 0.1, 6], [1.0, 2.0, 48]),
    "maxfev": 5000,
}

# K boundary hit detection (from fit_and_evaluate plausibility logic)
K_BOUNDARY_UPPER = 0.999   # K >= this → boundary hit

# Plausibility checks (must ALL pass when not boundary hit)
PLAUSIBILITY = {
    "r_min":   0.05,
    "t0_min":  6,
    "t0_max":  48,
}

# Ablation variant definitions
ABLATION_VARIANTS = {
    "strict":    {"r2_fail_threshold": 0.5},
    "loose":     {"r2_fail_threshold": 0.8},
    "split40":   {"subgroups": [(30, 39), (40, 49)]},
    "no_bounds": {"bounds": None},
}
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C1-7b-1 | Top-level constants | DISCOVERY, FIT_CONFIG, ABLATION_VARIANTS dicts |

---

## C1-5a: Gate Config [Complexity: 2, Budget: 1 subtask]

Applied: hardcoded dict for gate thresholds

```python
# ---------------------------------------------------------------------------
# H-C1 Gate Decision Thresholds
# ---------------------------------------------------------------------------

GATE = {
    # Primary pass criteria (all must hold)
    "convergence_rate_threshold":  0.70,   # small group convergence_rate >= 0.70
    "mean_r2_threshold":           0.70,   # small group mean_r2 >= 0.70
    "plausibility_rate_threshold": 0.70,   # small group plausibility_rate >= 0.70

    # Boundary hit cap (small group k_boundary_hit_rate must be BELOW this)
    "k_boundary_hit_threshold":    0.30,   # k_boundary_hit_rate < 0.30  (strict <, not <=)
}

# Comparison operators:
#   convergence_rate      : small >= GATE["convergence_rate_threshold"]
#   mean_r2               : small >= GATE["mean_r2_threshold"]
#   plausibility_rate     : small >= GATE["plausibility_rate_threshold"]
#   k_boundary_hit_rate   : small <  GATE["k_boundary_hit_threshold"]   ← strict less-than
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C1-5a-1 | Gate thresholds | GATE dict with comparison operator notes |

---

## C1-7a: Visualization Config [Complexity: 2, Budget: 1 subtask]

Applied: hardcoded dict for figure settings

```python
# ---------------------------------------------------------------------------
# H-C1 Visualization Config
# ---------------------------------------------------------------------------

VIZ = {
    "dpi": 120,   # matches h-m4 convention

    # Figure sizes (width, height) in inches
    "figsize_bar":      (9, 5),    # group comparison bar chart (3 metrics side-by-side)
    "figsize_hist":     (9, 5),    # R2 histogram overlay
    "figsize_curves":   (14, 4),   # per-benchmark fitted curves (1 row, n_benchmarks cols)
    "figsize_ablation": (10, 5),   # ablation summary bar chart

    # Color scheme: small group vs control group
    "color_small":   "steelblue",
    "color_control": "darkorange",
    "alpha":         0.80,

    # File names (saved to h-c1/figures/)
    "files": {
        "group_comparison": "group_comparison.png",
        "r2_distribution":  "r2_distribution.png",
        "fitted_curves":    "fitted_curves.png",
        "ablation_summary": "ablation_summary.png",
    },
}
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C1-7a-1 | Visualization settings | VIZ dict: figsize, dpi, colors, filenames |
