# Configuration Schema: H-M-integrated

**Hypothesis ID:** H-M-integrated
**Type:** MECHANISM (PoC)
**Date:** 2026-03-18
**Author:** Phase 3 Configuration Agent
**Infrastructure:** LIGHT tier (hardcoded constants)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from H-E1 base code
**Config Files Found:** h-e1/code/config.py
**Pattern Used:** Hardcoded dict (LIGHT tier requirement, consistent with H-E1)

---

## Knowledge Base Patterns Applied

Applied: Hardcoded dict pattern for LIGHT tier statistical analysis

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited or referenced from base hypothesis:

```python
# From: h-e1/code/config.py (ACTUAL CODE)

# Visualization Configuration (reusable)
VIZ_CONFIG = {
    "output_dir": "./figures",
    "dpi": 300,
    "format": "png",
    "figsize": (10, 8),
    "colors": {
        "execution": "#0173B2",
        "preference": "#DE8F05",
        "baseline": "#029E73"
    }
}

# Experiment Configuration (reusable)
EXPERIMENT_CONFIG = {
    "output_dir": "./results",
    "log_level": "INFO",
    "set_all_seeds": True,
    "seeds": {
        "random": 42,
        "numpy": 42,
        "torch": 42
    }
}
```

**Verified from**: h-e1/code/config.py (actual implementation)

---

## Configuration Format

LIGHT tier infrastructure requires hardcoded configuration. Using Python dictionary constants for copy-paste simplicity.

---

## A-2: Data Loading [Complexity: 6, Budget: 2 subtasks]

**Applied**: Standard pandas CSV loading

### Configuration (Hardcoded Dict)

```python
# config.py - Data Configuration
DATA_CONFIG = {
    "h_e1_results_path": "../h-e1/results/signatures.csv",
    "dimensions": ["correctness", "cyclomatic", "ast_depth", "runtime_ms", "memory_kb"],
    "required_columns": [
        "model_name",
        "alignment_type",
        "correctness",
        "cyclomatic",
        "ast_depth",
        "runtime_ms",
        "memory_kb"
    ],
    "alignment_types": ["execution", "preference", "baseline"]
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-2-1 | CSV schema validation | Verify H-E1 results have all required columns |
| A-2-2 | Alignment type grouping | Parse and group models by alignment_type |

---

## A-3: Percentile Ranking [Complexity: 8, Budget: 3 subtasks]

**Applied**: scipy.stats percentileofscore pattern

### Configuration (Hardcoded Dict)

```python
# config.py - Ranking Configuration
RANKING_CONFIG = {
    "percentile_method": "rank",  # scipy.stats.percentileofscore kind
    "dimensions": ["correctness", "cyclomatic", "ast_depth", "runtime_ms", "memory_kb"],
    "lower_is_better": {
        "correctness": False,  # Higher correctness = better
        "cyclomatic": True,    # Lower complexity = better
        "ast_depth": True,
        "runtime_ms": True,    # Lower runtime = better
        "memory_kb": True
    }
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-3-1 | Per-dimension ranking | Compute percentile ranks for each dimension |
| A-3-2 | Rank aggregation | Combine ranks across dimensions per model |
| A-3-3 | Direction adjustment | Invert ranks for "lower is better" metrics |

---

## A-4: Variance Analysis [Complexity: 9, Budget: 3 subtasks]

**Applied**: Standard numpy variance computation

### Configuration (Hardcoded Dict)

```python
# config.py - Variance Configuration
VARIANCE_CONFIG = {
    "grouping_key": "alignment_type",
    "compute_intra_variance": True,
    "compute_inter_distance": True,
    "distance_metric": "euclidean"
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-4-1 | Group by alignment method | Split data into execution/preference/baseline groups |
| A-4-2 | Intra-cluster variance | Compute within-method score variance |
| A-4-3 | Inter-cluster distance | Compute between-method mean distances |

---

## A-5: Statistical Tests [Complexity: 13, Budget: 4 subtasks]

**Applied**: scipy.stats hypothesis testing pattern

### Configuration (Hardcoded Dict)

```python
# config.py - Statistical Test Configuration
STATISTICAL_CONFIG = {
    # M1: Execution dominance
    "m1_threshold": 15.0,
    "m1_dimension": "correctness",
    "m1_comparison": "less_equal",  # mean_rank <= 15.0

    # M2: Preference balance
    "m2_threshold": 30.0,
    "m2_dimensions": ["correctness", "cyclomatic", "ast_depth", "runtime_ms", "memory_kb"],
    "m2_comparison": "less_equal",  # mean_rank <= 30.0

    # M3: Clustering consistency
    "m3_test": "mannwhitneyu",
    "m3_pvalue_threshold": 0.05,
    "m3_alternative": "two-sided"
}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-5-1 | M1 test implementation | Test execution models' correctness dominance |
| A-5-2 | M2 test implementation | Test preference models' balanced performance |
| A-5-3 | M3 test implementation | Mann-Whitney U test for clustering |
| A-5-4 | Test result aggregation | Collect all test results and p-values |

---

## A-6: Gate Validation [Complexity: 7, Budget: 2 subtasks]

**Applied**: Boolean AND gate logic

### Configuration (Hardcoded Dict)

```python
# config.py - Gate Configuration
GATE_CONFIG = {
    "type": "MUST_WORK",
    "condition": "M1_AND_M2",
    "m1_required": True,
    "m2_required": True,
    "m3_optional": True,
    "halt_on_failure": True
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-6-1 | Primary gate evaluation | Check M1 AND M2 pass condition |
| A-6-2 | Failure diagnostics | Log detailed failure reasons for routing |

---

## A-7: Visualization [Complexity: 11, Budget: 3 subtasks]

**Applied**: Inherited matplotlib config from H-E1

### Configuration (Hardcoded Dict)

```python
# config.py - Visualization Configuration (extended from H-E1)
VIZ_CONFIG = {
    "output_dir": "./figures",
    "dpi": 300,
    "format": "png",
    "figsize": (10, 8),
    "colors": {
        "execution": "#0173B2",
        "preference": "#DE8F05",
        "baseline": "#029E73"
    },
    "figures": [
        "dimension_rankings",
        "m1_validation",
        "m2_validation",
        "m3_variance",
        "gate_metrics"
    ]
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-7-1 | Dimension rankings plot | Bar chart of percentile ranks by model/dimension |
| A-7-2 | M1/M2 validation plots | Horizontal bars with threshold lines |
| A-7-3 | M3 variance plot | Box plots showing within/between-method variance |

---

## A-8: Analysis Orchestration [Complexity: 10, Budget: 3 subtasks]

**Applied**: Sequential pipeline pattern

### Configuration (Hardcoded Dict)

```python
# config.py - Experiment Configuration (extended from H-E1)
EXPERIMENT_CONFIG = {
    "output_dir": "./results",
    "log_level": "INFO",
    "set_all_seeds": True,
    "seeds": {
        "random": 42,
        "numpy": 42
    },

    # Analysis pipeline stages
    "pipeline_stages": [
        "load_data",
        "compute_rankings",
        "compute_variance",
        "run_statistical_tests",
        "validate_gate",
        "generate_visualizations",
        "save_results"
    ],

    # Output files
    "outputs": {
        "results": "./results/mechanism_tests.csv",
        "gate_validation": "./results/gate_validation.json",
        "report": "./results/analysis_report.txt"
    }
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-8-1 | Pipeline orchestration | Sequential execution of all analysis stages |
| A-8-2 | Results aggregation | Collect M1/M2/M3 results and gate status |
| A-8-3 | Report generation | Generate summary report with all metrics |

---

## Complete Configuration Module

**File:** `code/config.py`

```python
"""
Configuration for H-M-integrated Mechanistic Analysis
LIGHT tier: Hardcoded constants for statistical analysis
"""

# Data Configuration
DATA_CONFIG = {
    "h_e1_results_path": "../h-e1/results/signatures.csv",
    "dimensions": ["correctness", "cyclomatic", "ast_depth", "runtime_ms", "memory_kb"],
    "required_columns": [
        "model_name",
        "alignment_type",
        "correctness",
        "cyclomatic",
        "ast_depth",
        "runtime_ms",
        "memory_kb"
    ],
    "alignment_types": ["execution", "preference", "baseline"]
}

# Ranking Configuration
RANKING_CONFIG = {
    "percentile_method": "rank",
    "dimensions": ["correctness", "cyclomatic", "ast_depth", "runtime_ms", "memory_kb"],
    "lower_is_better": {
        "correctness": False,
        "cyclomatic": True,
        "ast_depth": True,
        "runtime_ms": True,
        "memory_kb": True
    }
}

# Variance Configuration
VARIANCE_CONFIG = {
    "grouping_key": "alignment_type",
    "compute_intra_variance": True,
    "compute_inter_distance": True,
    "distance_metric": "euclidean"
}

# Statistical Test Configuration
STATISTICAL_CONFIG = {
    # M1: Execution dominance
    "m1_threshold": 15.0,
    "m1_dimension": "correctness",
    "m1_comparison": "less_equal",

    # M2: Preference balance
    "m2_threshold": 30.0,
    "m2_dimensions": ["correctness", "cyclomatic", "ast_depth", "runtime_ms", "memory_kb"],
    "m2_comparison": "less_equal",

    # M3: Clustering consistency
    "m3_test": "mannwhitneyu",
    "m3_pvalue_threshold": 0.05,
    "m3_alternative": "two-sided"
}

# Gate Configuration
GATE_CONFIG = {
    "type": "MUST_WORK",
    "condition": "M1_AND_M2",
    "m1_required": True,
    "m2_required": True,
    "m3_optional": True,
    "halt_on_failure": True
}

# Visualization Configuration (inherited from H-E1)
VIZ_CONFIG = {
    "output_dir": "./figures",
    "dpi": 300,
    "format": "png",
    "figsize": (10, 8),
    "colors": {
        "execution": "#0173B2",
        "preference": "#DE8F05",
        "baseline": "#029E73"
    },
    "figures": [
        "dimension_rankings",
        "m1_validation",
        "m2_validation",
        "m3_variance",
        "gate_metrics"
    ]
}

# Experiment Configuration (inherited from H-E1)
EXPERIMENT_CONFIG = {
    "output_dir": "./results",
    "log_level": "INFO",
    "set_all_seeds": True,
    "seeds": {
        "random": 42,
        "numpy": 42
    },

    # Analysis pipeline stages
    "pipeline_stages": [
        "load_data",
        "compute_rankings",
        "compute_variance",
        "run_statistical_tests",
        "validate_gate",
        "generate_visualizations",
        "save_results"
    ],

    # Output files
    "outputs": {
        "results": "./results/mechanism_tests.csv",
        "gate_validation": "./results/gate_validation.json",
        "report": "./results/analysis_report.txt"
    }
}
```

---

## Usage Pattern

Phase 4 Coder will import these configs directly:

```python
from config import (
    DATA_CONFIG,
    RANKING_CONFIG,
    VARIANCE_CONFIG,
    STATISTICAL_CONFIG,
    GATE_CONFIG,
    VIZ_CONFIG,
    EXPERIMENT_CONFIG
)

# Example usage in modules
def load_h_e1_results():
    path = DATA_CONFIG["h_e1_results_path"]
    df = pd.read_csv(path)
    return df

def run_m1_test(ranks):
    threshold = STATISTICAL_CONFIG["m1_threshold"]
    dimension = STATISTICAL_CONFIG["m1_dimension"]
    # Test logic
    pass
```

---

## Non-Standard Value Rationale

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `m1_threshold` | 15.0 | Hypothesis requirement: top 15% correctness rank |
| `m2_threshold` | 30.0 | Hypothesis requirement: top 30% balanced performance |
| `m3_pvalue_threshold` | 0.05 | Standard statistical significance level |

All other parameters use standard library defaults from scipy.stats and numpy.

---

## Reproducibility Settings

All stochastic components use fixed seed=42:
- Random sampling (Python `random`)
- NumPy operations

No GPU required (statistical analysis only).

---

## Self-Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] KB search logged (1 line)
- [x] Codebase Analysis section included
- [x] Base hypothesis config verified from actual code
- [x] Inherited Configuration section included
- [x] Rationale only for non-standard values
- [x] Subtask budget within limits (18/18 used)
- [x] Total length < 400 lines
- [x] Complete config module provided
- [x] Copy-paste ready Python code

---

**End of Configuration Document**

*Ready for Phase 4 Implementation (code/config.py)*
