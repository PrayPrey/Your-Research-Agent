# Configuration: Contract-Based Phase Transition Validation

**Hypothesis:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New config design - no base hypothesis or existing codebase  
**Config Files Found:** None - new config  
**Pattern Used:** Hardcoded dict (EXISTENCE hypothesis - fixed values only)

---

## Configuration Schema

### 1. Pydantic ConfigDict Settings

Applied: Pydantic strict mode pattern

```python
CONFIG = {
    "strict": True,
    "extra": "forbid",
    "validate_assignment": True,
    "validate_default": True,
}
```

**Rationale:**
- `extra: forbid` - Critical for adversarial test suite to reject unknown fields
- `validate_assignment` - Ensures post-init mutations also validated

---

### 2. Contractme Policy Settings

```python
CONTRACTME_CONFIG = {
    "policy": "raise",  # Fail-fast on contract violations
}
```

Usage:
```python
from contractme import set_policy
set_policy(CONTRACTME_CONFIG["policy"])
```

---

### 3. Test Suite Configuration

```python
TEST_SUITE_CONFIG = {
    "total_cases": 20,
    "valid_cases": 5,
    "schema_violations": 5,
    "pattern_violations": 5,
    "contract_violations": 5,
    "storage_path": "tests/phase_boundary_validation/test_cases.yaml",
}
```

---

### 4. Constants Definitions

#### 4.1 Standard Datasets

```python
STANDARD_DATASETS = [
    "MNIST",
    "CIFAR-10",
    "CIFAR-100",
    "ImageNet",
    "COCO",
    "VOC2012",
    "WikiText",
    "SQuAD",
    "GLUE",
]
```

#### 4.2 Allowed Dataset Types

```python
ALLOWED_TYPES = ["standard", "custom", "programmatic-api"]
```

#### 4.3 Existing Benchmarks

```python
EXISTING_BENCHMARKS = [
    "GLUE",
    "SuperGLUE",
    "SQuAD",
    "COCO",
    "ImageNet",
]
```

---

### 5. Constraint Pattern Configuration

#### 5.1 C1: No Synthetic Data

```python
C1_PATTERN_CONFIG = {
    "constraint_id": "C1",
    "regex_pattern": r"synthetic|simulated|generated",
    "regex_flags": "re.IGNORECASE",
    "field": "dataset_type",
    "error_message": "C1 violation: synthetic data forbidden",
}
```

#### 5.2 C2: No Human Evaluation

```python
C2_PATTERN_CONFIG = {
    "constraint_id": "C2",
    "keywords": ["human", "manual", "annotator", "labeler"],
    "field": "evaluation_method",
    "error_message": "C2 violation: human evaluation forbidden",
}
```

#### 5.3 C3: Real Standard Datasets Only

```python
C3_CONTRACT_CONFIG = {
    "constraint_id": "C3",
    "cross_field_rule": "dataset_type == 'standard' implies dataset_name in STANDARD_DATASETS",
    "fields": ["dataset_type", "dataset_name"],
    "error_message": "C3 violation: unknown standard dataset",
}
```

#### 5.4 C4: No New Benchmarks

```python
C4_CONTRACT_CONFIG = {
    "constraint_id": "C4",
    "state_rule": "benchmark_name in EXISTING_BENCHMARKS",
    "field": "benchmark_name",
    "error_message": "C4 violation: new benchmark forbidden",
}
```

---

### 6. Metrics Thresholds

```python
METRICS_CONFIG = {
    "primary": {
        "detection_rate_improvement": 50,  # Percentage
        "comparison": ">=",
    },
    "secondary": {
        "false_positive_rate": 0.10,
        "execution_overhead_ms": 100,
        "contract_loc_per_boundary": 50,
    },
    "failure_threshold": 20,  # Abort if improvement < 20%
}
```

---

### 7. Test Case YAML Schema

```python
TEST_CASE_SCHEMA = {
    "required_fields": [
        "id",
        "name",
        "violation_type",
        "constraint_violated",
        "phase2a_output",
        "expected_detection",
    ],
    "field_types": {
        "id": "str",
        "name": "str",
        "violation_type": "Literal['schema', 'pattern', 'contract', 'none']",
        "constraint_violated": "Literal['C1', 'C2', 'C3', 'C4', 'none']",
        "phase2a_output": "dict",
        "expected_detection": "dict",
    },
    "expected_detection_schema": {
        "schema": "bool",
        "pattern": "bool",
        "contract": "bool",
    },
}
```

Example YAML structure:
```yaml
- id: tc-01
  name: "Valid Phase 2A output"
  violation_type: none
  constraint_violated: none
  phase2a_output:
    research_question: "Can contracts detect violations?"
    detailed_question: "Extended question..."
    dataset_type: "standard"
    dataset_name: "MNIST"
    evaluation_method: "automated metrics"
    hypotheses: [{id: "h1", statement: "..."}]
  expected_detection:
    schema: true
    pattern: true
    contract: true
```

---

### 8. Phase2AOutput Field Requirements

```python
PHASE2A_SCHEMA = {
    "research_question": {"type": "str", "min_length": 10},
    "detailed_question": {"type": "str"},
    "reference_papers": {"type": "List[dict]"},
    "hypotheses": {"type": "List[dict]", "min_length": 1},
    "causal_mechanism": {"type": "dict"},
    "predictions": {"type": "List[dict]"},
    "dataset_type": {"type": "Literal", "values": ALLOWED_TYPES},
    "dataset_name": {"type": "str"},
    "model_approach": {"type": "str"},
    "evaluation_method": {"type": "str"},
}
```

---

### 9. File Paths Configuration

```python
FILE_PATHS = {
    "test_cases": "tests/phase_boundary_validation/test_cases.yaml",
    "conftest": "tests/phase_boundary_validation/conftest.py",
    "schemas": "src/validation/schemas.py",
    "patterns": "src/validation/patterns.py",
    "contracts": "src/validation/contracts.py",
    "constants": "src/validation/constants.py",
    "experiment_runner": "experiments/h_e1_contract_validation.py",
}
```

---

### 10. Validation Results Output Schema

```python
RESULTS_SCHEMA = {
    "detection_rates": {
        "schema_only": "float",
        "schema_pattern": "float",
        "full_contract": "float",
    },
    "improvement_percentage": "float",
    "false_positive_rate": "float",
    "execution_overhead_ms": "float",
    "contract_loc": "int",
    "layer_breakdown": {
        "schema_detected": "int",
        "pattern_detected": "int",
        "contract_detected": "int",
    },
}
```

---

## Complete Configuration Module

Copy-paste ready:

```python
"""Configuration for h-e1 contract validation experiment"""
import re
from typing import List, Literal

# Pydantic ConfigDict
PYDANTIC_CONFIG = {
    "strict": True,
    "extra": "forbid",
    "validate_assignment": True,
    "validate_default": True,
}

# Contractme Policy
CONTRACTME_POLICY = "raise"

# Test Suite
TEST_SUITE = {
    "total": 20,
    "valid": 5,
    "schema_violations": 5,
    "pattern_violations": 5,
    "contract_violations": 5,
}

# Constants
STANDARD_DATASETS = [
    "MNIST",
    "CIFAR-10",
    "CIFAR-100",
    "ImageNet",
    "COCO",
    "VOC2012",
    "WikiText",
    "SQuAD",
    "GLUE",
]

ALLOWED_TYPES = ["standard", "custom", "programmatic-api"]

EXISTING_BENCHMARKS = [
    "GLUE",
    "SuperGLUE",
    "SQuAD",
    "COCO",
    "ImageNet",
]

# Constraint Patterns
C1_PATTERN = r"synthetic|simulated|generated"
C1_FLAGS = re.IGNORECASE

C2_KEYWORDS = ["human", "manual", "annotator", "labeler"]

# Metrics Thresholds
DETECTION_IMPROVEMENT_THRESHOLD = 50  # %
FALSE_POSITIVE_THRESHOLD = 0.10
EXECUTION_OVERHEAD_THRESHOLD = 100  # ms
CONTRACT_LOC_THRESHOLD = 50
FAILURE_THRESHOLD = 20  # %

# File Paths
TEST_CASES_PATH = "tests/phase_boundary_validation/test_cases.yaml"
SCHEMAS_PATH = "src/validation/schemas.py"
PATTERNS_PATH = "src/validation/patterns.py"
CONTRACTS_PATH = "src/validation/contracts.py"
CONSTANTS_PATH = "src/validation/constants.py"
```

---

## Validation

**Self-Check:**
- [x] Single format (hardcoded dict - EXISTENCE PoC)
- [x] No ASCII diagrams
- [x] KB search applied: Pydantic strict mode
- [x] Codebase Analysis section included
- [x] All threshold values from experiment_spec.yaml
- [x] Copy-paste ready Python code
- [x] Length < 400 lines
