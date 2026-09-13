# Configuration Specification: Contract Expressiveness Validation

**Hypothesis ID:** h-m1  
**Date:** 2026-08-20  
**Phase:** 3 - Implementation Planning

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** green-field - new config design  
**Config Files Found:** None - validation experiment (no existing config)  
**Pattern Used:** Hardcoded dict (validation constants)

**Applied:** Standard Python constants pattern (no ML training)

---

## Validation Constants

### Constraint Definitions

```python
# src/validation/constants.py

# C3: Standard dataset membership constraint
STANDARD_DATASETS = {
    "CIFAR-10",
    "MNIST", 
    "ImageNet",
    "COCO"
}

# C4: Benchmark state validation constraint
EXISTING_BENCHMARKS = {
    "GLUE",
    "SuperGLUE",
    "SQuAD"
}

# C1: Synthetic data keyword pattern (lowercase for case-insensitive matching)
SYNTHETIC_KEYWORDS = ["synthetic"]

# C2: Human evaluation keyword blacklist (lowercase for case-insensitive matching)
HUMAN_EVAL_KEYWORDS = ["human", "manual", "annotator"]
```

---

## Coverage Thresholds

```python
# tests/h_m1/run_coverage_test.py

THRESHOLDS = {
    "contract_coverage_min": 1.0,      # 100% (4/4 constraints)
    "schema_coverage_max": 0.5,         # <50% (<2/4 constraints)
    "expressiveness_gap_min": 0.75,    # ≥75 percentage points
    "implementation_loc_max": 50        # Contract layer complexity limit
}

TOTAL_CONSTRAINTS = 4  # C1, C2, C3, C4
```

---

## Test Case Schema

### YAML Structure

```yaml
# tests/h_m1/test_cases.yaml

test_cases:
  - id: str                     # TC-M1-XX
    description: str             # Constraint violation name
    constraint_violated: str     # C1 | C2 | C3 | C4 | null
    input:
      research_question: str
      hypotheses: List[dict]
      dataset_type: str
      dataset_name: str
      evaluation_method: str
      benchmark_name: str
    expected:
      schema_detects: bool
      contract_detects: bool
```

### Test Cases (5 total)

```yaml
test_cases:
  - id: TC-M1-01
    description: "C1 Synthetic Data Detection"
    constraint_violated: C1
    input:
      research_question: "Evaluate synthetic dataset performance"
      hypotheses: [{"id": "h1", "description": "test"}]
      dataset_type: "standard"
      dataset_name: "SyntheticDataset2024"
      evaluation_method: "automatic"
      benchmark_name: "GLUE"
    expected:
      schema_detects: false
      contract_detects: true

  - id: TC-M1-02
    description: "C2 Human Evaluation Detection"
    constraint_violated: C2
    input:
      research_question: "Test human evaluation pipeline"
      hypotheses: [{"id": "h1", "description": "test"}]
      dataset_type: "standard"
      dataset_name: "CIFAR-10"
      evaluation_method: "human annotators rate outputs"
      benchmark_name: "GLUE"
    expected:
      schema_detects: false
      contract_detects: true

  - id: TC-M1-03
    description: "C3 Cross-Field Constraint"
    constraint_violated: C3
    input:
      research_question: "Validate unknown dataset handling"
      hypotheses: [{"id": "h1", "description": "test"}]
      dataset_type: "standard"
      dataset_name: "UnknownDataset2024"
      evaluation_method: "automatic"
      benchmark_name: "GLUE"
    expected:
      schema_detects: false
      contract_detects: true

  - id: TC-M1-04
    description: "C4 State-Based Validation"
    constraint_violated: C4
    input:
      research_question: "Benchmark new evaluation method"
      hypotheses: [{"id": "h1", "description": "test"}]
      dataset_type: "standard"
      dataset_name: "CIFAR-10"
      evaluation_method: "automatic"
      benchmark_name: "NewBenchmark2024"
    expected:
      schema_detects: false
      contract_detects: true

  - id: TC-M1-05
    description: "Valid Input (No Violations)"
    constraint_violated: null
    input:
      research_question: "Standard pipeline validation test"
      hypotheses: [{"id": "h1", "description": "test"}]
      dataset_type: "standard"
      dataset_name: "CIFAR-10"
      evaluation_method: "automatic accuracy measurement"
      benchmark_name: "GLUE"
    expected:
      schema_detects: false
      contract_detects: false
```

---

## Dependencies

```python
# pyproject.toml or requirements.txt

dependencies = [
    "pydantic>=2.0",      # Schema-only baseline
    "icontract>=2.0",     # Contract-based validation
    "pytest>=7.0",        # Test framework
    "pyyaml>=6.0"         # Test case loading
]

python_version = ">=3.11"  # Required for Pydantic V2 features
```

---

## Validation Metrics Configuration

```python
# tests/h_m1/run_coverage_test.py

METRICS = {
    "primary": {
        "name": "Constraint Coverage",
        "formula": "(detected / total_constraints) * 100",
        "unit": "percentage"
    },
    "secondary": {
        "expressiveness_gap": {
            "formula": "contract_coverage - schema_coverage",
            "unit": "percentage_points"
        },
        "implementation_complexity": {
            "measure": "Lines of contract code",
            "unit": "LOC"
        }
    }
}
```

---

## File Structure

```python
# Expected directory layout (for reference)

PROJECT_STRUCTURE = {
    "src/validation/": [
        "__init__.py",
        "constants.py",      # STANDARD_DATASETS, EXISTING_BENCHMARKS, keyword lists
        "schemas.py",        # Schema-only baseline (Pydantic)
        "contracts.py"       # Contract-based implementation (icontract)
    ],
    "tests/h_m1/": [
        "__init__.py",
        "test_cases.yaml",   # 5 validation test cases
        "run_coverage_test.py"  # Coverage experiment
    ]
}
```

---

## Validation Report Schema

```python
# Expected structure of 04_validation.md

VALIDATION_REPORT_SCHEMA = {
    "experiment_id": "h-m1-contract-expressiveness",
    "results": {
        "schema_coverage": float,       # 0.0-1.0
        "contract_coverage": float,     # 0.0-1.0
        "expressiveness_gap": float,    # Percentage points
        "implementation_loc": int
    },
    "per_constraint_breakdown": {
        "C1": {"schema": bool, "contract": bool},
        "C2": {"schema": bool, "contract": bool},
        "C3": {"schema": bool, "contract": bool},
        "C4": {"schema": bool, "contract": bool}
    },
    "gate_status": "PASS | FAIL",
    "success_criteria_met": {
        "contract_coverage_100": bool,
        "schema_coverage_lt_50": bool,
        "gap_gte_75": bool
    }
}
```

---

## Notes

**No Hyperparameters:** This is a validation framework experiment, not model training. All values are deterministic constants.

**No Subtask Decomposition:** Configuration is minimal and hardcoded. No per-task budgets required.

**EXISTENCE Hypothesis:** Single fixed configuration (no variations, no tuning, no ablations).
