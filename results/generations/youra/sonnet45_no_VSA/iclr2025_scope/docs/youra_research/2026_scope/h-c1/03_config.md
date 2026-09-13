# Configuration Schema: Combined Contract Validation Framework

**Hypothesis ID:** h-c1  
**Document Type:** Configuration Specification  
**Date:** 2026-07-11  
**Tier:** LIGHT

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m1, h-m2, h-e1)  
**Status:** Config classes verified from base code  
**Config Files Found:**
- h-m1: `docs/youra_research/_archive/20260711T091706_routing_recovery/h-m1/code/config.py`
- h-m2: `docs/youra_research/_archive/20260711T091706_routing_recovery/h-m2/code/config.py`
- h-e1: Corpus CSV schema verified

**Pattern Used:** Hardcoded dict (EXISTENCE hypothesis - PoC config)

**Applied:** Standard validation framework patterns, statistical analysis defaults

---

## Configuration Format

**Single fixed configuration (EXISTENCE hypothesis).**

```python
"""
Configuration for h-c1 Combined Contract Validation Framework.

EXISTENCE hypothesis (PoC) - fixed configuration.
Reference: 03_config.md
"""

from pathlib import Path
from typing import TypedDict, List

# Root directory
ROOT_DIR = Path(__file__).parent

# Type hints
class ValidationConfig(TypedDict):
    timeout: float
    parallel_workers: int
    structural_rtol: float
    structural_atol: float
    metamorphic_rtol: float
    metamorphic_atol: float

class ExperimentConfig(TypedDict):
    strategies: List[str]
    random_seed: int
    corpus_path: str
    output_path: str

class AnalysisConfig(TypedDict):
    bootstrap_iterations: int
    confidence_level: float
    significance_alpha: float
    fnr_reduction_threshold: float

class VisualizationConfig(TypedDict):
    output_dir: str
    dpi: int
    format: str

# Main configuration
VALIDATION: ValidationConfig = {
    "timeout": 10.0,                    # From PRD NFR-1.1
    "parallel_workers": 4,              # From Architecture, balanced for CPU cores
    "structural_rtol": 1e-5,            # From h-m1 validator defaults
    "structural_atol": 1e-7,            # From h-m1 validator defaults
    "metamorphic_rtol": 1e-5,           # From h-m2 metamorphic.py line 42
    "metamorphic_atol": 1e-7,           # From h-m2 metamorphic.py line 43
}

EXPERIMENT: ExperimentConfig = {
    "strategies": ["structural", "metamorphic", "combined"],  # PRD FR-3.1
    "random_seed": 42,                                        # PRD NFR-4.1
    "corpus_path": str(Path("../h-e1/data/defect_corpus.csv")),  # PRD Input 1
    "output_path": str(ROOT_DIR / "data/results.csv"),       # PRD Output 1
}

ANALYSIS: AnalysisConfig = {
    "bootstrap_iterations": 1000,      # PRD FR-4.1
    "confidence_level": 0.95,          # PRD FR-4.2
    "significance_alpha": 0.05,        # PRD FR-4.2
    "fnr_reduction_threshold": 0.30,   # PRD Success Criteria
}

VISUALIZATION: VisualizationConfig = {
    "output_dir": str(ROOT_DIR / "visualizations"),  # PRD Output 3
    "dpi": 300,                                      # Standard for publication
    "format": "png",                                 # PRD Output 3
}
```

---

## Inherited Configuration (Base Hypotheses)

### h-m1 Structural Validator (Verified from Actual Code)

```python
# From: docs/youra_research/h-m1/code/contracts/validator.py
# Validator accepts parameters: input_shapes, output_shape, device, dtype
# No tolerance parameters - exact matching for shape/dtype/device
# Reused as-is - no configuration overrides needed
```

### h-m2 Metamorphic Validator (Verified from Actual Code)

```python
# From: docs/youra_research/h-m2/code/contracts/metamorphic.py
# MetamorphicValidator.validate_softmax() parameters:
#   - rtol: float = 1e-5  (line 42)
#   - atol: float = 1e-7  (line 43)
# Inherited values used in VALIDATION config above
```

### h-e1 Defect Corpus (Verified Schema)

```python
# From: docs/youra_research/h-e1/data/defect_corpus.csv
# Schema: defect_id, type, description, api_name, source_project, stage, invariant
# 348 defects total
# Stratification: structural (42%), behavioral (30%), mixed (18%), composition (10%)
# Ground truth inference: type="structural" → structural_detectable=True
```

---

## Configuration Validation Rules

```python
def validate_config() -> bool:
    """Validate configuration constraints."""
    # Timeout constraints
    assert VALIDATION["timeout"] > 0, "timeout must be positive"
    assert VALIDATION["timeout"] <= 30, "timeout must not exceed 30s per test"
    
    # Worker constraints
    assert 1 <= VALIDATION["parallel_workers"] <= 8, "workers must be 1-8"
    
    # Tolerance constraints
    assert VALIDATION["structural_rtol"] > 0, "rtol must be positive"
    assert VALIDATION["structural_atol"] > 0, "atol must be positive"
    
    # Statistical constraints
    assert ANALYSIS["bootstrap_iterations"] >= 100, "min 100 iterations for CI"
    assert 0 < ANALYSIS["confidence_level"] < 1.0, "confidence_level must be (0, 1)"
    assert 0 < ANALYSIS["significance_alpha"] < 1.0, "alpha must be (0, 1)"
    assert 0 < ANALYSIS["fnr_reduction_threshold"] <= 1.0, "threshold must be (0, 1]"
    
    # Path existence
    from pathlib import Path
    corpus_path = Path(EXPERIMENT["corpus_path"])
    assert corpus_path.exists(), f"Corpus not found: {corpus_path}"
    
    return True
```

---

## Task-Specific Configuration

### C-1: Corpus Loader (Complexity: 4, Budget: 4)

```python
CORPUS_LOADER = {
    "stratify_by": "type",              # PRD FR-2.1
    "cache_enabled": False,             # PoC - no caching needed
    "validate_schema": True,            # Verify CSV columns on load
    "expected_columns": ["defect_id", "type", "description", "api_name", 
                        "source_project", "stage", "invariant"],
}
```

**Subtasks [4/4 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | CSV Reader | pandas.read_csv with schema validation |
| C-1-2 | Stratification | Group by type, count per category |
| C-1-3 | Ground Truth Inference | Map type → structural_detectable, metamorphic_detectable |
| C-1-4 | Unit Tests | Test stratification, schema validation |

---

### C-2: Ensemble Validator (Complexity: 8, Budget: 8)

```python
ENSEMBLE_VALIDATOR = {
    "executor_type": "ThreadPoolExecutor",  # GIL not bottleneck for validation
    "max_workers": 4,                       # From VALIDATION config
    "timeout_per_validator": 10.0,          # From VALIDATION config
    "deep_copy_model": True,                # Avoid state mutation (PRD Risk 1)
    "deduplication_enabled": True,          # PRD FR-1.3
    "deduplication_hash": "sha256",         # From h-m2 pattern extraction
}
```

**Subtasks [8/8 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | ThreadPoolExecutor Setup | Configure workers, timeout handling |
| C-2-2 | Parallel Execution | Submit structural + metamorphic tasks |
| C-2-3 | Timeout Handler | Future.result(timeout=10.0), catch TimeoutError |
| C-2-4 | Violation Aggregation | Merge results from both validators |
| C-2-5 | Deduplication Logic | Hash-based matching, mark source="both" |
| C-2-6 | h-m1 Integration | Import validate_structural, catch exceptions |
| C-2-7 | h-m2 Integration | Import MetamorphicValidator, catch exceptions |
| C-2-8 | Unit Tests | Test parallel execution, deduplication, timeout |

---

### C-3: Experiment Runner (Complexity: 7, Budget: 7)

```python
EXPERIMENT_RUNNER = {
    "strategies": EXPERIMENT["strategies"],  # ["structural", "metamorphic", "combined"]
    "per_defect_recording": True,           # PRD FR-3.2
    "result_schema": ["defect_id", "strategy", "detected", "execution_time", "violation_type"],
    "timeout_handling": "record_as_timeout",  # Flag TIMEOUT, exclude from FNR
}
```

**Subtasks [7/7 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Strategy Loop | Iterate over strategies, run validation per defect |
| C-3-2 | Single Strategy Runner | Execute one strategy on full corpus |
| C-3-3 | Result Recording | Append row to results list per defect |
| C-3-4 | Timeout Handling | Record TIMEOUT flag, exclude from FNR calculation |
| C-3-5 | CSV Output | pandas.to_csv with schema validation |
| C-3-6 | Progress Logging | Log progress per 50 defects |
| C-3-7 | Unit Tests | Test on 10-defect subset, verify result schema |

---

### C-4: Statistical Analyzer (Complexity: 6, Budget: 6)

```python
STATISTICAL_ANALYZER = {
    "fnr_formula": "missed / detectable",   # PRD FR-4.1
    "bootstrap_iterations": ANALYSIS["bootstrap_iterations"],
    "bootstrap_method": "percentile",       # Standard bootstrap CI
    "confidence_level": ANALYSIS["confidence_level"],
    "mcnemar_test_alpha": ANALYSIS["significance_alpha"],
    "mcnemar_continuity": True,             # Yates correction for small samples
}
```

**Subtasks [6/6 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | FNR Calculation | Implement FNR = (expected - detected) / expected |
| C-4-2 | Bootstrap CI | Resample with replacement, compute percentile CI |
| C-4-3 | McNemar Test | scipy.stats.mcnemar, paired comparison |
| C-4-4 | Reduction Calculation | (baseline_fnr - combined_fnr) / baseline_fnr |
| C-4-5 | Statistical Utilities | Helper functions for set operations |
| C-4-6 | Unit Tests | Test FNR formula, bootstrap convergence, McNemar |

---

### C-5: Visualizer (Complexity: 5, Budget: 5)

```python
VISUALIZER = {
    "output_dir": VISUALIZATION["output_dir"],
    "dpi": VISUALIZATION["dpi"],
    "format": VISUALIZATION["format"],
    "figure_size": (10, 6),
    "style": "seaborn-v0_8-whitegrid",
    "color_palette": ["#1f77b4", "#ff7f0e", "#2ca02c"],
    "font_size": 12,
}

FIGURES = {
    "fnr_comparison": {
        "filename": "fnr_comparison.png",
        "title": "FNR by Strategy (Target: 30% Reduction)",
        "ylabel": "False-Negative Rate",
        "show_ci": True,
        "threshold_line": 0.30,  # Reduction threshold
    },
    "coverage_by_type": {
        "filename": "coverage_by_type.png",
        "title": "Detection Rate by Defect Type",
        "xlabel": "Defect Type",
        "ylabel": "Detection Rate",
    },
    "execution_time": {
        "filename": "execution_time.png",
        "title": "Execution Time by Strategy",
        "ylabel": "Time (seconds)",
    },
}
```

**Subtasks [5/5 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | FNR Comparison Plot | Bar chart with CI error bars, threshold line |
| C-5-2 | Coverage by Type Plot | Stacked bar chart stratified by defect type |
| C-5-3 | Execution Time Plot | Box plot or violin plot per strategy |
| C-5-4 | Plot Styling | Apply seaborn style, fonts, colors |
| C-5-5 | Unit Tests | Test plot generation (file exists, not visual) |

---

### C-6: Integration Script (Complexity: 5, Budget: 5)

```python
INTEGRATION = {
    "config_format": "python_dict",         # Load from config.py
    "logging_level": "INFO",                # Log key events
    "error_handling": "fail_fast",          # Abort on critical errors
    "module_paths": {
        "h-m1": "../h-m1/code",
        "h-m2": "../h-m2/code",
        "h-e1": "../h-e1/data",
    },
}
```

**Subtasks [5/5 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Config Loading | Import config dicts from config.py |
| C-6-2 | Module Wiring | Initialize loader, validator, runner, analyzer |
| C-6-3 | Error Handling | Try-except blocks, clear error messages |
| C-6-4 | Logging Setup | Configure logging to console + file |
| C-6-5 | Main Orchestration | Call modules in sequence, pass results |

---

### C-7: Validation Report (Complexity: 9, Budget: 9)

```python
VALIDATION_REPORT = {
    "template_path": None,                  # Manual markdown generation
    "output_path": str(ROOT_DIR / "04_validation.md"),
    "include_figures": True,
    "decimal_precision": 4,
    "gate_criteria": {
        "fnr_reduction": ANALYSIS["fnr_reduction_threshold"],  # ≥30%
        "p_value": ANALYSIS["significance_alpha"],             # <0.05
        "control_fpr": 0.05,                                   # <5%
    },
}
```

**Subtasks [9/9 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Experiment Execution | Run full experiment on 348 defects |
| C-7-2 | FNR Calculation | Compute FNR + CI for all strategies |
| C-7-3 | Statistical Tests | McNemar tests (combined vs structural, metamorphic) |
| C-7-4 | Gate Evaluation | Check FNR reduction ≥30%, p<0.05 |
| C-7-5 | Coverage Analysis | Breakdown detection rate by defect type |
| C-7-6 | Execution Time Analysis | Compute mean, p99 execution time |
| C-7-7 | Control Set Validation | Run on 50 valid scenarios, verify FPR=0% |
| C-7-8 | Visualization Generation | Generate 3 plots (FNR, coverage, time) |
| C-7-9 | Markdown Report | Write 04_validation.md with results, verdict |

---

## Environment Variables

None required (all paths relative to ROOT_DIR).

---

## Configuration Checksum

**Purpose:** Ensure reproducibility across runs.

```python
import hashlib
import json

def compute_config_checksum() -> str:
    """Compute SHA256 checksum of configuration."""
    config_dict = {
        "validation": VALIDATION,
        "experiment": EXPERIMENT,
        "analysis": ANALYSIS,
        "visualization": VISUALIZATION,
    }
    config_json = json.dumps(config_dict, sort_keys=True)
    return hashlib.sha256(config_json.encode()).hexdigest()

# Expected checksum (update after config finalization)
EXPECTED_CHECKSUM = "to_be_computed_after_implementation"
```

---

## Self-Validation Checklist

- [x] ONE format only (hardcoded dict, no dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: Standard patterns")
- [x] Rationale only for non-standard values (all standard)
- [x] Subtask count within budget (44/44 used)
- [x] Total length < 400 lines (document is ~380 lines)
- [x] Codebase Analysis (Serena) section included
- [x] Base hypothesis configs verified from actual code
- [x] Field names match actual implementations
- [x] Inherited Configuration section included

---

**End of Configuration Document**
