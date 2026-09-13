# Configuration Design Document: h-m1 Score Convergence Detection

**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Date:** 2026-08-28  
**Subtask Budget:** 0 tasks (LIGHT tier)  
**Infrastructure Tier:** LIGHT (hardcoded config)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extends h-e1 data infrastructure  
**Config Files Found:** None - h-e1 uses hardcoded constants in config.py  
**Pattern Used:** Hardcoded dict (LIGHT tier standard)

---

## Applied Patterns

Applied: **Hardcoded Config Pattern** (Archon KB: LIGHT tier uses constants)

---

## Configuration Schema

### config.py (Hardcoded Constants)

```python
"""
Configuration for h-m1 convergence detection.
LIGHT tier: Hardcoded constants for rolling window analysis.
"""
from pathlib import Path

# Data Sources (Inherited from h-e1)
DATA_ROOT = Path(__file__).parent.parent / "h-e1" / "data"
PWC_DATA_DIR = DATA_ROOT / "pwc_leaderboards"

# Output Directories
OUTPUT_DIR = Path(__file__).parent / "results"
FIGURES_DIR = Path(__file__).parent / "figures"

# Benchmarks
BENCHMARKS = ["imagenet", "glue", "squad"]

# Rolling Window Parameters
WINDOW_MONTHS = 6
MIN_PERIODS = 3
TOP_K = 5

# Convergence Detection
CONVERGENCE_THRESHOLD = 0.005  # 0.5% std threshold

# Statistical Validation
SIGNIFICANCE_LEVEL = 0.05  # p-value threshold for Levene's test

# Success Criteria
MIN_CONVERGENCE_COUNT = 2  # 2/3 benchmarks must converge
ALIGNMENT_TOLERANCE_YEARS = 1  # ±1 year for expert consensus

# Expected Convergence Windows (Expert Consensus)
EXPECTED_CONVERGENCE = {
    "imagenet": (2017, 2020),
    "glue": (2020, 2022),
    "squad": None  # No prior expectation
}
```

---

## Inherited Configuration (Base Hypothesis)

### Data Schema (From h-e1 Actual Code)

The following data format is inherited from h-e1:

```python
# From: docs/youra_research/h-e1/src/data_validator.py (ACTUAL CODE)
# JSONL Schema per submission:
{
    "submission_date": "2020-01-15",  # ISO 8601
    "score": 78.3,
    "benchmark": "imagenet",
    "model_name": "ResNet-152"
}
```

### Data Validation Constants (From h-e1 Code)

```python
# From: h-e1/src/data_validator.py
class DataValidator:
    MIN_SAMPLE_SIZE = 100
    MIN_TIMESTAMP_COVERAGE = 0.8
    MIN_TEMPORAL_RANGE_YEARS = 4
```

**Verified from:** docs/youra_research/h-e1/src/data_validator.py (lines 9-11)

---

## Task Configurations

### M1-1: Data Loading

```python
CONFIG = {
    "data_dir": PWC_DATA_DIR,
    "benchmarks": BENCHMARKS,
    "required_fields": ["submission_date", "score", "benchmark"]
}
```

### M1-2: Rolling Window Statistics

```python
CONFIG = {
    "window_months": 6,
    "min_periods": 3,
    "top_k": 5,
    "groupby_freq": "M"  # Monthly aggregation
}
```

### M1-3: Convergence Detection

```python
CONFIG = {
    "threshold": 0.005,
    "return_first_only": True
}
```

### M1-4: Statistical Validation

```python
CONFIG = {
    "test": "levene",  # scipy.stats.levene
    "alpha": 0.05,
    "center": "median"  # Levene's test center parameter
}
```

### M1-5: Timeline Visualization

```python
CONFIG = {
    "output_dir": FIGURES_DIR,
    "dpi": 300,
    "figsize": (10, 6),
    "threshold_color": "red",
    "threshold_linestyle": "--"
}
```

### M1-6: Gate Metrics Comparison

```python
CONFIG = {
    "output_path": FIGURES_DIR / "gate_metrics.png",
    "metrics": ["convergence_count", "alignment_accuracy"],
    "target_convergence": MIN_CONVERGENCE_COUNT,
    "figsize": (8, 5)
}
```

### M1-7: Pipeline Orchestration

```python
CONFIG = {
    "output_path": OUTPUT_DIR / "convergence_results.json",
    "benchmarks": BENCHMARKS,
    "verbose": True
}
```

---

## Directory Setup

```python
# setup.py (create folders on first run)
from pathlib import Path

def create_directory_structure():
    """Create output directories if they don't exist."""
    directories = [
        Path(__file__).parent / "results",
        Path(__file__).parent / "figures"
    ]
    for dir_path in directories:
        dir_path.mkdir(exist_ok=True)
    print("✓ Directory structure created")

if __name__ == "__main__":
    create_directory_structure()
```

---

## Configuration Summary

| Category | Method | Rationale |
|----------|--------|-----------|
| Format | Hardcoded dict | LIGHT tier standard |
| Data Source | h-e1 symlink | Reuses validated data |
| Parameters | Fixed values | EXISTENCE hypothesis - no tuning |
| Logging | print() | No framework overhead |
| Subtasks | 0/0 used | LIGHT tier - no decomposition |

---

**Document Status:** READY FOR PHASE 4
