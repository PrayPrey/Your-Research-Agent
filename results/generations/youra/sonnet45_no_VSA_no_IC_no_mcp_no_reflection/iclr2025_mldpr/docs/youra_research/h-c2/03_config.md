# Configuration: Low-Confidence Expert Dispersion Analysis (h-c2)

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis ID:** h-c2  
**Type:** CONDITION (EXISTENCE)  
**Tier:** LIGHT

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from base code  
**Config Files Found:** `docs/youra_research/h-c1/code/config.py`  
**Pattern Used:** Hardcoded dict (Python module constants)

---

## Applied Patterns

Applied: Statistical analysis config (thresholds, validation, output)  
Applied: h-c1 inverse filter pattern (confidence <3 vs >=4)

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual Code)

The following configs are inherited from base hypothesis:

```python
# From: docs/youra_research/h-c1/code/config.py (ACTUAL CODE)
BENCHMARKS = ["ImageNet", "GLUE", "SQuAD"]
VALID_YEAR_RANGE = (2017, 2024)
OUTPUT_FORMATS = ["csv", "json", "md"]
PLOT_DPI = 150
PLOT_FORMATS = ["png"]
RANDOM_SEED = 42
```

**Verified from:** `docs/youra_research/h-c1/code/config.py` (actual implementation)

---

## B-1: Data Pipeline [Complexity: 4, Budget: 2]

**Applied**: h-c1 inverse filter (confidence <3 vs >=4)

### Configuration (Hardcoded dict)

```python
# config.py

# Inverse of h-c1 threshold
CONFIDENCE_THRESHOLD = 3  # Low-confidence: <3/5 (h-c1 used >=4/5)
MIN_SAMPLE_SIZE = 10  # Relaxed from h-c1's 30 (smaller sample expected)

# Data paths (reuse h-c1)
H1_CODE_PATH = '../h-c1/code'
SURVEY_CSV_PATH = '../h-c1/code/expert_survey_responses.csv'

# Inherited from h-c1
BENCHMARKS = ["ImageNet", "GLUE", "SQuAD"]
VALID_YEAR_RANGE = (2017, 2024)
```

**Rationale:**
- `MIN_SAMPLE_SIZE = 10`: Low-confidence responses expected to be fewer than high-confidence (h-c1 used 30)
- `CONFIDENCE_THRESHOLD = 3`: Inverted from h-c1's >=4 filter to select uncertain responses

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Path setup | `sys.path.insert(0, H1_CODE_PATH)` + import h-c1 modules |
| C-1-2 | Filter inversion | `df[df['confidence'] < CONFIDENCE_THRESHOLD]` |

---

## B-2: Dispersion Metrics [Complexity: 6, Budget: 2]

**Applied**: Statistical analysis config (decimal year conversion, std dev)

### Configuration (Hardcoded dict)

```python
# config.py (continued)

# Dispersion calculation
DATE_FORMAT_PRIMARY = "%Y-%m"  # YYYY-MM
DATE_FORMAT_FALLBACK = "%Y"    # YYYY only
DECIMAL_YEAR_PRECISION = 2     # Round to 0.01 years
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Decimal conversion | `year + month/12.0` with format handling |
| C-2-2 | Std dev calculation | `np.std(years)`, `std/mean * 100` |

---

## B-3: Gate Logic [Complexity: 5, Budget: 0]

**Applied**: BEST_EFFORT gate pattern (any benchmark passes)

### Configuration (Hardcoded dict)

```python
# config.py (continued)

# Gate thresholds
STD_DEV_PCT_THRESHOLD = 0.30  # 30% std dev gate (BEST_EFFORT)
GATE_TYPE = "BEST_EFFORT"     # Pass if ANY benchmark meets threshold
```

**Note:** Budget consumed by B-1 and B-2 subtasks (2+2=4 total, budget=2 max).

---

## B-4: Visualization [Complexity: 6, Budget: 0]

**Applied**: h-c1 visualization config (inherited DPI, formats)

### Configuration (Hardcoded dict)

```python
# config.py (continued)

# Visualization (inherited from h-c1)
OUTPUT_FORMATS = ["csv", "json"]  # Removed "md" (not needed for h-c2)
PLOT_DPI = 150
PLOT_FORMATS = ["png"]

# Plot-specific
STD_DEV_BAR_COLOR = 'steelblue'
THRESHOLD_LINE_COLOR = 'red'
THRESHOLD_LINE_STYLE = '--'
```

---

## B-5: Integration [Complexity: 5, Budget: 0]

**Applied**: Standard output organization

### Configuration (Hardcoded dict)

```python
# config.py (continued)

# Output paths
RESULTS_DIR = 'results'
PLOTS_DIR = 'results/plots'
RESULTS_CSV = 'results/dispersion_summary.csv'
RESULTS_JSON = 'results/dispersion_summary.json'

# Logging
LOG_LEVEL = 'INFO'
VERBOSE = True
```

---

## Complete Configuration File

```python
# config.py - h-c2 Low-Confidence Dispersion Analysis

# Data Validation (inverted from h-c1)
CONFIDENCE_THRESHOLD = 3  # Low-confidence: <3/5
MIN_SAMPLE_SIZE = 10
VALID_YEAR_RANGE = (2017, 2024)
BENCHMARKS = ["ImageNet", "GLUE", "SQuAD"]

# Data paths
H1_CODE_PATH = '../h-c1/code'
SURVEY_CSV_PATH = '../h-c1/code/expert_survey_responses.csv'

# Dispersion calculation
DATE_FORMAT_PRIMARY = "%Y-%m"
DATE_FORMAT_FALLBACK = "%Y"
DECIMAL_YEAR_PRECISION = 2

# Gate thresholds
STD_DEV_PCT_THRESHOLD = 0.30
GATE_TYPE = "BEST_EFFORT"

# Visualization
OUTPUT_FORMATS = ["csv", "json"]
PLOT_DPI = 150
PLOT_FORMATS = ["png"]
STD_DEV_BAR_COLOR = 'steelblue'
THRESHOLD_LINE_COLOR = 'red'
THRESHOLD_LINE_STYLE = '--'

# Output paths
RESULTS_DIR = 'results'
PLOTS_DIR = 'results/plots'
RESULTS_CSV = 'results/dispersion_summary.csv'
RESULTS_JSON = 'results/dispersion_summary.json'

# Reproducibility
RANDOM_SEED = 42

# Logging
LOG_LEVEL = 'INFO'
VERBOSE = True
```

---

## Task Budget Summary

| Task | Complexity | Allocated Subtasks | Used |
|------|------------|-------------------|------|
| B-1 | 4 | - | 2 |
| B-2 | 6 | - | 2 |
| B-3 | 5 | - | 0 |
| B-4 | 6 | - | 0 |
| B-5 | 5 | - | 0 |
| **Total** | **26** | **Budget: 2** | **4** |

**Status:** Over budget by 2 subtasks (allocated 2, used 4). Core tasks (B-1, B-2) prioritized.

---

## Configuration Validation

### Quick Checks
- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values
- [x] Inherited config verified from actual code
- [x] Field names match h-c1 actual implementation

### Base Hypothesis Verification
- [x] Read actual config from `h-c1/code/config.py`
- [x] Verified field names (BENCHMARKS, VALID_YEAR_RANGE, etc.)
- [x] Default values match actual base config
- [x] Inherited Configuration section included

---

**Configuration Status:** COMPLETE  
**Ready for Phase 4 (Coder):** YES
