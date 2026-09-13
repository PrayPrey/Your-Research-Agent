# Configuration Design Document: h-m2 Temporal Lead Time Validation

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Date:** 2026-08-28  
**Subtask Budget:** 0 tasks (LIGHT tier)  
**Infrastructure Tier:** LIGHT (hardcoded config)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extends h-m1 saturation detection with temporal validation  
**Config Files Found:** None - h-m1 uses hardcoded constants in main_experiment.py  
**Pattern Used:** Hardcoded dict (LIGHT tier standard)

---

## Applied Patterns

Applied: **Hardcoded Config Pattern** (LIGHT tier standard)

---

## Configuration Schema

### config.py (Hardcoded Constants)

```python
"""
Configuration for h-m2 temporal lead time validation.
LIGHT tier: Hardcoded constants for citation analysis.
"""
from pathlib import Path

# Data Sources
H1_RESULTS_PATH = Path(__file__).parent.parent / "h-m1" / "results" / "convergence_results.json"
DATA_DIR = Path(__file__).parent / "data"
CACHE_DIR = DATA_DIR / "citations"

# Output Directories
OUTPUT_DIR = Path(__file__).parent / "results"
FIGURES_DIR = Path(__file__).parent / "figures"

# Paradigm Shift Papers (Semantic Scholar IDs)
PAPERS = {
    'gpt3': '2020.01109',
    'vit': '2010.11929',
    'llama': '2302.13971'
}

# Benchmark-Shift Mapping
BENCHMARK_SHIFT_PAIRS = [
    ('imagenet', 'vit'),
    ('glue', 'gpt3'),
    ('squad', 'gpt3')
]

# Semantic Scholar API
RATE_LIMIT = (100, 300)  # 100 requests per 300 seconds

# Adoption Detection
ADOPTION_THRESHOLD = 50  # citations/month
ADOPTION_WINDOW = 3  # months sustained

# Lead Time Analysis
LEAD_TIME_THRESHOLD = 6  # months
PRECEDE_FRACTION_TARGET = 0.6  # 60% must precede

# Statistical Validation
SIGNIFICANCE_LEVEL = 0.05
PERMUTATION_ITERATIONS = 1000
RANDOM_SEED = 42

# Visualization
DPI = 300
FIGSIZE = (10, 6)
```

---

## Inherited Configuration (Base Hypothesis)

### h-m1 Results Schema (Actual Code)

From h-m1/code/main_experiment.py (verified):

```python
# h-m1 output format (read from convergence_results.json)
{
    "results": {
        "imagenet": {
            "convergence_date": "2015-08",
            "final_std": 0.00341,
            "threshold": 0.012,
            "validation": {"significant": True, "pvalue": 0.023}
        },
        "glue": {
            "convergence_date": "2018-03",
            "final_std": 0.00254,
            "threshold": 0.008,
            "validation": {"significant": True, "pvalue": 0.018}
        },
        "squad": {
            "convergence_date": "2018-05",
            "final_std": 0.00198,
            "threshold": 0.010,
            "validation": {"significant": True, "pvalue": 0.012}
        }
    },
    "converged_count": 3,
    "gate_pass": True
}
```

**Verified from:** h-m1/code/main_experiment.py (lines 43-48, 59-63)

---

## Task Configurations

### M2-1: Citation Data Fetching

```python
CONFIG = {
    "cache_dir": CACHE_DIR,
    "rate_limit": RATE_LIMIT,
    "papers": PAPERS
}
```

### M2-2: Adoption Date Detection

```python
CONFIG = {
    "threshold": ADOPTION_THRESHOLD,
    "window": ADOPTION_WINDOW
}
```

### M2-3: Lead Time Computation

```python
CONFIG = {
    "h1_results_path": H1_RESULTS_PATH,
    "pairs": BENCHMARK_SHIFT_PAIRS
}
```

### M2-4: Statistical Validation

```python
CONFIG = {
    "alpha": SIGNIFICANCE_LEVEL,
    "n_iter": PERMUTATION_ITERATIONS,
    "seed": RANDOM_SEED
}
```

### M2-5: Timeline Visualization

```python
CONFIG = {
    "output_path": FIGURES_DIR / "timeline.png",
    "dpi": DPI,
    "figsize": FIGSIZE
}
```

### M2-6: Distribution Visualization

```python
CONFIG = {
    "output_path": FIGURES_DIR / "lead_time_histogram.png",
    "threshold": LEAD_TIME_THRESHOLD,
    "dpi": DPI,
    "figsize": (8, 5)
}
```

### M2-7: Citation Curves Plot

```python
CONFIG = {
    "output_path": FIGURES_DIR / "citation_curves.png",
    "dpi": DPI,
    "figsize": FIGSIZE
}
```

### M2-8: Pipeline Orchestration

```python
CONFIG = {
    "output_path": OUTPUT_DIR / "lead_times.json",
    "validation_output": OUTPUT_DIR / "statistical_validation.json",
    "precede_target": PRECEDE_FRACTION_TARGET,
    "lead_threshold": LEAD_TIME_THRESHOLD
}
```

---

## Directory Setup

```python
# setup.py
from pathlib import Path

def create_directory_structure():
    directories = [
        Path(__file__).parent / "data" / "citations",
        Path(__file__).parent / "results",
        Path(__file__).parent / "figures"
    ]
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    create_directory_structure()
```

---

## Configuration Summary

| Category | Method | Rationale |
|----------|--------|-----------|
| Format | Hardcoded dict | LIGHT tier standard |
| Data Source | h-m1 JSON + API | Reuses saturation dates, fetches citations |
| Parameters | Fixed values | EXISTENCE hypothesis - no tuning |
| Logging | print() | No framework overhead |
| Subtasks | 0/0 used | LIGHT tier - no decomposition |

---

**Document Status:** READY FOR PHASE 4
