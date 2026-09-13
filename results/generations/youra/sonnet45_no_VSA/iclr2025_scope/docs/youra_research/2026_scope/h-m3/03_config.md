# Configuration Design: H-M3 Composition-Level Contract Validation

**Hypothesis ID:** h-m3  
**Document Type:** Configuration Specification  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from h-m1 actual code  
**Config Files Found**: 
- `/workspace/TEST_scope/docs/youra_research/h-m1/code/contracts/validator.py`
- `/workspace/TEST_scope/docs/youra_research/h-m1/code/run_experiment.py`

**Pattern Used**: No config dataclass in h-m1 (uses hardcoded values in experiment script)

**Note**: h-m1 uses hardcoded experiment parameters directly in `run_experiment.py`. h-m3 follows same pattern for PoC simplicity.

---

## 1. Configuration Overview

**Applied**: PyTorch PoC pattern (hardcoded dict for minimal configuration)

This is a SHOULD_WORK (PoC) hypothesis testing composition-level contract validation. Configuration uses a single hardcoded dictionary to minimize overhead.

**Design Principle**: Minimal config to test "does it work?" - no hyperparameter tuning or ablations.

---

## 2. Inherited Configuration (Base Hypothesis)

### From h-m1 Actual Code

The following patterns are inherited from h-m1 implementation:

```python
# From: h-m1/code/contracts/validator.py (ACTUAL CODE)
# Exception hierarchy (reused for composition validation)
class ContractViolationError(Exception): pass
class ShapeViolation(ContractViolationError): pass
class DeviceViolation(ContractViolationError): pass
class DtypeViolation(ContractViolationError): pass

# Decorator pattern (extended to multi-tensor composition)
def validate_structural(
    input_shapes: Dict[str, Tuple[int, ...]] = None,
    output_shape: Tuple[int, ...] = None,
    device: str = None,
    dtype: torch.dtype = None
): ...

# Import-time validation pattern (adapted for composition)
def validate_at_import(model_class): ...
```

**Verified from**: `/workspace/TEST_scope/docs/youra_research/h-m1/code/` (actual implementation)

---

## 3. Task Configurations

### A-1: Composition Validator [Complexity: 14, Budget: 1 subtask]

**Applied**: PyTorch decorator validation pattern

```python
# composition_validator.py
VALIDATOR_CONFIG = {
    "device_consistency": True,
    "dtype_consistency": True,
    "layout_consistency": True,
    "probe_execution": False,  # h-m3 validates properties only, no probe execution
    "error_verbosity": "detailed"
}
```

**Subtasks [1/1 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Core decorator implementation | Implement @validate_composition with device/dtype/layout checks |

---

### A-2: Test Case Generation [Complexity: 12, Budget: 1 subtask]

**Applied**: Real defect patterns from PyTorch/HF issues

```python
# test_cases.py
TEST_SUITE_CONFIG = {
    "total_defects": 15,  # Minimal for PoC (10-20 range from PRD)
    "device_mismatch": 5,
    "dtype_mismatch": 3,
    "layout_mismatch": 2,
    "composition": 5,
    "control_tests": 5,  # False positive validation
    "seed": 42
}

# Source defect IDs (real PyTorch/HF issues)
DEFECT_SOURCES = {
    "device": ["PyTorch#166117", "PyTorch#168010", "PyTorch#159133", "HF-Diffusers#3313"],
    "dtype": ["PyTorch-MixedPrecision", "PyTorch-Autocast"],
    "layout": ["PyTorch-Sparse", "PyTorch-Strided"],
    "composition": ["HF-Transformers-Device", "HF-Diffusers-Generator"]
}
```

**Subtasks [1/1 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Defect corpus creation | Generate 15 test cases from documented PyTorch/HF issues |

---

### A-3: Baseline Experiments [Complexity: 9, Budget: 0 subtasks]

**Applied**: Standard PyTorch defaults

```python
# run_experiment.py - baseline execution
BASELINE_CONFIG = {
    "mode": "no_contracts",
    "timeout_per_test": 10,  # PRD requirement
    "measure_detection": True,
    "measure_timing": True
}
```

**Note**: No subtasks allocated (epic fits within A-3 main task).

---

### A-4: Contract Validation [Complexity: 11, Budget: 1 subtask]

**Applied**: h-m1 validation pattern (import-time detection)

```python
# run_experiment.py - proposed execution
PROPOSED_CONFIG = {
    "mode": "with_contracts",
    "timeout_per_test": 10,
    "detection_stage_tracking": True,  # import vs runtime
    "measure_overhead": True
}
```

**Subtasks [1/1 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Contract execution harness | Run 15 tests with composition validation, track detection stage |

---

### A-5: Metrics Calculation [Complexity: 8, Budget: 0 subtasks]

**Applied**: Standard detection rate formula

```python
# evaluate.py
METRICS_CONFIG = {
    "detection_rate_threshold": 0.60,  # SHOULD_WORK gate
    "false_positive_threshold": 0.05,  # PRD requirement
    "output_format": "json"
}

# Formulas (hardcoded, no configuration needed)
# detection_rate = (detected / total_defects) * 100
# fp_rate = (false_positives / control_tests) * 100
```

**Note**: No subtasks allocated (simple calculation logic).

---

### A-6: Visualization [Complexity: 9, Budget: 1 subtask]

**Applied**: matplotlib bar chart pattern

```python
# evaluate.py - visualization
VISUALIZATION_CONFIG = {
    "figure_format": "png",
    "output_dir": "figures/",
    "dpi": 300,
    "mandatory_figures": ["detection_rate.png"],  # Baseline vs proposed with 60% threshold
    "optional_figures": []  # None for PoC
}

# Chart settings
CHART_CONFIG = {
    "title": "Detection Rate: Baseline vs Composition Contracts",
    "threshold_line": 0.60,  # SHOULD_WORK gate
    "colors": {"baseline": "#FF6B6B", "proposed": "#4ECDC4"},
    "figsize": (10, 6)
}
```

**Subtasks [1/1 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Detection rate chart | Generate bar chart comparing baseline vs proposed with 60% threshold line |

---

## 4. Environment Configuration

**Applied**: PyTorch reproducibility pattern (from PyTorch randomness docs)

```python
# run_experiment.py - environment setup
ENVIRONMENT_CONFIG = {
    "seed": 42,
    "torch_seed": 42,
    "numpy_seed": 42,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "cuda_deterministic": False,  # PoC - performance over determinism
    "pytorch_version": ">=1.12.0",
    "python_version": ">=3.8"
}
```

---

## 5. Experiment Results Schema

**Applied**: JSON results pattern from h-m1

```python
# run_experiment.py output
RESULTS_SCHEMA = {
    "experiment_id": "h-m3-poc",
    "timestamp": "ISO-8601",
    "test_results": [
        {
            "test_id": "str",
            "category": "device_mismatch | dtype_mismatch | layout_mismatch | composition",
            "baseline_detected": bool,
            "baseline_stage": "none | runtime",
            "proposed_detected": bool,
            "proposed_stage": "none | import | setup",
            "detection_time": float,
            "error_message": "str"
        }
    ],
    "summary": {
        "total_tests": int,
        "baseline_detection_rate": float,
        "proposed_detection_rate": float,
        "false_positive_rate": float,
        "avg_detection_time": float
    }
}
```

---

## 6. Configuration Loading

### Single-File Configuration Pattern

```python
# config.py (minimal)
import torch

CONFIG = {
    # Validator
    "device_consistency": True,
    "dtype_consistency": True,
    "layout_consistency": True,
    
    # Test suite
    "total_defects": 15,
    "control_tests": 5,
    "seed": 42,
    
    # Execution
    "timeout_per_test": 10,
    "detection_rate_threshold": 0.60,
    "false_positive_threshold": 0.05,
    
    # Environment
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    
    # Output
    "results_path": "experiment_results.json",
    "figures_dir": "figures/"
}
```

**Usage in experiment scripts**:

```python
from config import CONFIG

# In test_cases.py
total_defects = CONFIG["total_defects"]
seed = CONFIG["seed"]

# In run_experiment.py
timeout = CONFIG["timeout_per_test"]
device = CONFIG["device"]

# In evaluate.py
threshold = CONFIG["detection_rate_threshold"]
output_dir = CONFIG["figures_dir"]
```

---

## 7. Default Values Rationale

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `total_defects` | 15 | Minimal PoC size (within PRD 10-20 range) |
| `detection_rate_threshold` | 0.60 | SHOULD_WORK gate from PRD |
| `timeout_per_test` | 10 | PRD NFR-1 requirement |
| `seed` | 42 | Standard reproducibility seed |
| `control_tests` | 5 | Sufficient for FP rate <5% validation |
| `error_verbosity` | "detailed" | Research context requires diagnostics |

---

## 8. Subtask Budget Summary

**Total Budget**: 4 subtasks  
**Allocated**: 4 subtasks

| Task | Complexity | Subtasks Used |
|------|-----------|---------------|
| A-1: Composition Validator | 14 | 1 |
| A-2: Test Case Generation | 12 | 1 |
| A-3: Baseline Experiments | 9 | 0 |
| A-4: Contract Validation | 11 | 1 |
| A-5: Metrics Calculation | 8 | 0 |
| A-6: Visualization | 9 | 1 |

**Total**: 4/4 subtasks used

---

## 9. Integration with PRD Requirements

| PRD Requirement | Configuration Parameter | Default Value |
|-----------------|-------------------------|---------------|
| FR-1: @validate_composition decorator | `device_consistency`, `dtype_consistency`, `layout_consistency` | All True |
| FR-5: 10-20 defect test cases | `total_defects` | 15 |
| FR-7: Detection rate ≥60% | `detection_rate_threshold` | 0.60 |
| FR-8: Mandatory detection rate chart | `mandatory_figures` | ["detection_rate.png"] |
| NFR-1: Execution time ≤10s | `timeout_per_test` | 10 |
| NFR-2: PyTorch ≥1.12.0 | `pytorch_version` | ">=1.12.0" |

---

## 10. Summary

**Configuration Format**: Hardcoded dict (following h-m1 PoC pattern)

**Total Parameters**: 15 configuration options in single dict

**Reproducibility**: Fixed seed (42) for test case generation

**Next Steps**:
- Implement configuration in `code/config.py`
- Use CONFIG dict in all experiment scripts
- Validate subtask allocation matches budget (4/4)

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Phase:** Phase 4 - Code Implementation  
**Configuration File Location:** `docs/youra_research/h-m3/code/config.py`
