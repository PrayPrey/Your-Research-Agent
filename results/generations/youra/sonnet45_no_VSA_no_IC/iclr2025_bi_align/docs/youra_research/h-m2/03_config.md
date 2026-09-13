# Configuration Specification: Multi-Layer Validation Detection

**Hypothesis ID:** h-m2  
**Date:** 2026-08-20  
**Phase:** 3 - Implementation Planning

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Extending h-m1 validation infrastructure  
**Config Files Found:** src/validation/constants.py (verified)  
**Pattern Used:** Hardcoded dict (reuse h-m1 constants)

**Applied:** Standard Python constants pattern (validation experiment, no ML training)

---

## Inherited Configuration (Base Hypothesis h-m1)

### Validation Constants (Verified from Actual Code)

```python
# From: src/validation/constants.py (ACTUAL CODE)

# C3: Standard dataset membership constraint
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

# C4: Benchmark state validation constraint
EXISTING_BENCHMARKS = [
    "GLUE",
    "SuperGLUE",
    "SQuAD",
    "COCO",
    "ImageNet",
]

# Dataset type enum
ALLOWED_TYPES = ["standard", "custom", "programmatic-api"]
```

**Note:** Field names match actual implementation in src/validation/constants.py.

---

## h-m2 Experiment Configuration

### Test Suite Parameters

```python
# tests/h_m2/test_suite_config.py

TEST_SUITE = {
    "total_cases": 30,
    "distribution": {
        "valid": 5,           # Should pass all layers
        "schema": 10,         # Fail at schema layer
        "pattern": 10,        # Pass schema, fail pattern
        "contract": 5         # Pass schema+pattern, fail contract
    },
    "constraint_coverage": {
        "C1": 3,  # Pattern violations (synthetic keywords)
        "C2": 3,  # Pattern violations (human eval keywords)
        "C3": 2,  # Contract violations (cross-field)
        "C4": 3   # Contract violations (state-based)
    }
}
```

### Layer Toggle Configuration

```python
# experiments/h_m2_multilayer_validation.py

VALIDATION_CONDITIONS = {
    "baseline": {
        "schema_enabled": True,
        "pattern_enabled": False,
        "contract_enabled": False,
        "expected_detection_rate": 0.40  # 10/25 violations
    },
    "three_layer": {
        "schema_enabled": True,
        "pattern_enabled": True,
        "contract_enabled": True,
        "expected_detection_rate": 1.0   # 25/25 violations
    }
}
```

### Metrics Thresholds

```python
# experiments/h_m2_multilayer_validation.py

SUCCESS_CRITERIA = {
    "primary": {
        "name": "Detection Gap",
        "threshold": 40,  # percentage points
        "formula": "three_layer_rate - schema_only_rate",
        "gate": "MUST_MEET"
    },
    "secondary": {
        "pattern_layer_c1_c2": {
            "threshold": 80,  # percent
            "formula": "(C1_detected + C2_detected) / (C1_total + C2_total) * 100",
            "gate": "NICE_TO_HAVE"
        },
        "contract_layer_c3_c4": {
            "threshold": 100,  # percent
            "formula": "(C3_detected + C4_detected) / (C3_total + C4_total) * 100",
            "gate": "NICE_TO_HAVE"
        },
        "false_positive_rate": {
            "threshold": 0,  # percent
            "formula": "rejected_valid / total_valid * 100",
            "gate": "NICE_TO_HAVE"
        }
    }
}
```

### Output Paths

```python
# experiments/h_m2_multilayer_validation.py

OUTPUT_CONFIG = {
    "test_suite_file": "tests/h_m2/test_cases_h_m2.yaml",
    "results_report": "docs/youra_research/h-m2/04_validation.md",
    "raw_results_json": "docs/youra_research/h-m2/results_h_m2.json"
}
```

---

## Test Case Schema (Extended from h-m1)

### YAML Structure

```yaml
# tests/h_m2/test_cases_h_m2.yaml

test_cases:
  - id: str                     # tc-{nn}
    name: str                   # Descriptive name
    violation_type: str         # schema | pattern | contract | none
    constraint_violated: str    # C1 | C2 | C3 | C4 | none
    phase2a_output:
      research_question: str
      hypotheses: List[dict]
      dataset_type: str         # standard | custom | programmatic-api
      dataset_name: str
      evaluation_method: str
      benchmark_name: str
      # ... other Phase 2A fields
    expected_detection:
      schema: bool              # Should schema layer detect?
      pattern: bool             # Should pattern layer detect?
      contract: bool            # Should contract layer detect?
```

### Validation Rules

```python
# experiments/utils/h_m2_validator.py

VALIDATION_RULES = {
    "test_suite": {
        "total_cases": lambda x: x == 30,
        "valid_cases": lambda x: x == 5,
        "violation_cases": lambda x: x == 25,
        "distribution": lambda d: (
            d["schema"] == 10 and 
            d["pattern"] == 10 and 
            d["contract"] == 5
        )
    },
    "constraint_coverage": {
        "C1_min": 2,
        "C2_min": 2,
        "C3_min": 2,
        "C4_min": 2
    },
    "expected_detection_labels": {
        "schema_violation": {
            "schema": False,
            "pattern": False,
            "contract": False
        },
        "pattern_violation": {
            "schema": True,
            "pattern": False,
            "contract": False
        },
        "contract_violation": {
            "schema": True,
            "pattern": True,
            "contract": False
        },
        "valid_case": {
            "schema": True,
            "pattern": True,
            "contract": True
        }
    }
}
```

---

## Constraint Pattern Definitions (Inherited from h-m1)

### Pattern Layer Keywords

```python
# From: src/validation/patterns.py (referenced, no changes)

C1_SYNTHETIC_KEYWORDS = [
    "synthetic",
    "simulated",
    "generated",
    "artificial"
]

C2_HUMAN_EVAL_KEYWORDS = [
    "human",
    "manual",
    "annotator",
    "rater"
]
```

### Contract Layer Whitelists

```python
# From: src/validation/constants.py (referenced, no changes)

# C3 enforcement: dataset_type == "standard" → dataset_name in STANDARD_DATASETS
# C4 enforcement: "benchmark" in evaluation_method → benchmark_name in EXISTING_BENCHMARKS
```

---

## Detection Tracking Schema

```python
# experiments/utils/h_m2_validator.py

DETECTION_RESULT = {
    "test_case_id": str,
    "condition": str,  # "baseline" | "three_layer"
    "detected": bool,
    "layer": str,      # null | "schema" | "pattern" | "contract"
    "expected": {
        "schema": bool,
        "pattern": bool,
        "contract": bool
    },
    "actual": {
        "schema": bool,
        "pattern": bool,
        "contract": bool
    },
    "match": bool      # actual == expected
}
```

---

## Validation Report Schema

```python
# Expected structure of docs/youra_research/h-m2/04_validation.md

VALIDATION_REPORT = {
    "experiment_id": "h-m2-multilayer-detection",
    "test_suite": {
        "total_cases": int,
        "distribution": dict,
        "constraint_coverage": dict
    },
    "detection_rates": {
        "baseline": {
            "overall": float,          # schema_only_rate
            "by_violation_type": {
                "schema": float,
                "pattern": float,
                "contract": float
            }
        },
        "three_layer": {
            "overall": float,          # three_layer_rate
            "by_layer": {
                "schema": float,
                "pattern": float,
                "contract": float
            }
        },
        "gap": float                   # three_layer - baseline (pp)
    },
    "constraint_analysis": {
        "C1": {"detected": int, "total": int, "rate": float},
        "C2": {"detected": int, "total": int, "rate": float},
        "C3": {"detected": int, "total": int, "rate": float},
        "C4": {"detected": int, "total": int, "rate": float}
    },
    "false_positives": {
        "rejected": int,
        "total_valid": int,
        "rate": float
    },
    "gate_verdict": str,  # PASS | PARTIAL | FAIL
    "criteria_met": {
        "primary_gap_gte_40pp": bool,
        "pattern_layer_gte_80": bool,
        "contract_layer_100": bool,
        "false_positive_0": bool
    }
}
```

---

## Dependencies (Inherited from h-m1)

```python
# pyproject.toml or requirements.txt

dependencies = [
    "pydantic>=2.0",      # Schema layer
    "icontract>=2.0",     # Contract layer
    "pytest>=7.0",        # Test framework
    "pyyaml>=6.0"         # Test case loading
]

python_version = ">=3.11"
```

---

## File Structure

```python
PROJECT_STRUCTURE = {
    "src/validation/": [
        "constants.py",       # Inherited from h-m1 (no changes)
        "schemas.py",         # Inherited from h-m1 (no changes)
        "patterns.py",        # Inherited from h-m1 (no changes)
        "contracts.py"        # Inherited from h-m1 (no changes)
    ],
    "tests/h_m2/": [
        "test_cases_h_m2.yaml"  # NEW: 30-case adversarial suite
    ],
    "experiments/": [
        "h_m2_multilayer_validation.py",  # NEW: Main experiment runner
        "utils/h_m2_validator.py"         # NEW: Detection tracker
    ],
    "docs/youra_research/h-m2/": [
        "04_validation.md",    # NEW: Results report
        "results_h_m2.json"    # NEW: Raw detection results
    ]
}
```

---

## Notes

**EXISTENCE Hypothesis:** Single fixed configuration (no hyperparameter tuning, no ablations).

**Minimal Extension:** Reuses all h-m1 validation infrastructure. Only adds:
- Extended test suite (20 → 30 cases)
- Layer-specific detection tracking
- Baseline vs three-layer comparison

**No Training:** Pure validation experiment (deterministic, no randomness).
