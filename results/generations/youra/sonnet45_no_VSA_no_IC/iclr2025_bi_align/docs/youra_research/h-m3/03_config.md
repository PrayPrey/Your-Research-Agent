# Configuration Specification: Early Detection Cost Reduction

**Hypothesis ID:** h-m3  
**Date:** 2026-08-20  
**Phase:** 3 - Implementation Planning

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Validation infrastructure exists (h-m1, h-m2)  
**Config Files Found:** src/validation/constants.py (verified)  
**Pattern Used:** Hardcoded dict (validation experiment, no ML training)

---

## Inherited Configuration (h-m2 Validation Infrastructure)

### Validation Constants (Verified from Actual Code)

```python
# From: src/validation/constants.py (ACTUAL CODE)

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

EXISTING_BENCHMARKS = [
    "GLUE",
    "SuperGLUE",
    "SQuAD",
    "COCO",
    "ImageNet",
]

ALLOWED_TYPES = ["standard", "custom", "programmatic-api"]
```

---

## h-m3 Experiment Configuration

**Applied:** Standard Python dict pattern (PoC validation experiment)

### Corpus Generation

```python
# experiments/h_m3_corpus_generator.py

CORPUS_CONFIG = {
    "total_hypotheses": 100,
    "seed": 42,
    "distribution": {
        "valid": 80,
        "violated": 20
    },
    "violations": {
        "C1": 5,  # Synthetic dataset requirement
        "C2": 5,  # Human evaluation requirement
        "C3": 5,  # Non-standard dataset reference
        "C4": 5   # New benchmark creation
    },
    "output_path": "tests/placeholder_hypotheses/corpus_100.json"
}
```

### Violation Injection Rules

```python
# experiments/h_m3_corpus_generator.py

VIOLATION_PATTERNS = {
    "C1": {
        "field": "phase2_output.dataset.type",
        "value": "synthetic",
        "expected_failure": "Phase 4"
    },
    "C2": {
        "field": "phase2_output.evaluation.requires_human",
        "value": True,
        "expected_failure": "Phase 4"
    },
    "C3": {
        "field": "phase2_output.dataset.name",
        "value": "custom-imagenet-variant",
        "expected_failure": "Phase 5"
    },
    "C4": {
        "field": "phase2_output.experiment.creates_benchmark",
        "value": True,
        "expected_failure": "Phase 5"
    }
}
```

### Validation Conditions

```python
# experiments/h_m3_early_detection.py

CONDITIONS = {
    "A": {
        "name": "schema_only",
        "schema_enabled": True,
        "pattern_enabled": False,
        "contract_enabled": False,
        "log_path": "results/h_m3/condition_a_log.json"
    },
    "B": {
        "name": "contract_based",
        "schema_enabled": True,
        "pattern_enabled": True,
        "contract_enabled": True,
        "log_path": "results/h_m3/condition_b_log.json"
    }
}
```

### Pipeline Execution

```python
# experiments/h_m3_pipeline_runner.py

PIPELINE_CONFIG = {
    "phases": ["phase2", "phase3", "phase4", "phase5"],
    "timeout_per_hypothesis": 30,  # seconds
    "failure_trace_dir": "results/h_m3/phase45_failures",
    "validation_boundaries": [
        "phase2_to_phase3",
        "phase3_to_phase4",
        "phase4_to_phase5"
    ]
}
```

### Success Criteria

```python
# experiments/h_m3_early_detection.py

SUCCESS_CRITERIA = {
    "primary": {
        "name": "failure_reduction",
        "threshold": 80,  # percentage
        "formula": "(Failure_A - Failure_B) / Failure_A * 100"
    },
    "secondary": {
        "boundary_detection": {
            "threshold": 90,  # percentage
            "formula": "Detected_at_boundary / 20 * 100"
        },
        "false_positive": {
            "threshold": 0,  # percentage
            "formula": "Valid_rejected / 80 * 100"
        }
    },
    "gate_matrix": {
        "pass": {"reduction": 80, "detection": 90},
        "pivot": {"reduction": 40, "detection": 90},
        "route_to_0": {"reduction": 20}
    }
}
```

### Output Paths

```python
# experiments/h_m3_early_detection.py

OUTPUT_CONFIG = {
    "corpus": "tests/placeholder_hypotheses/corpus_100.json",
    "condition_a_log": "results/h_m3/condition_a_log.json",
    "condition_b_log": "results/h_m3/condition_b_log.json",
    "failure_dir": "results/h_m3/phase45_failures",
    "validation_report": "docs/youra_research/h-m3/04_validation.md",
    "raw_metrics": "results/h_m3/metrics.json"
}
```

---

## Data Schemas

### Corpus Entry Schema

```python
# experiments/h_m3_corpus_generator.py

CORPUS_ENTRY = {
    "hypothesis_id": str,          # h-test-001 to h-test-100
    "statement": str,              # Placeholder hypothesis text
    "phase2_output": {
        "dataset": {
            "type": str,           # standard | synthetic | custom
            "name": str            # Dataset name
        },
        "evaluation": {
            "requires_human": bool
        },
        "experiment": {
            "creates_benchmark": bool
        }
    },
    "injected_violation": {
        "constraint": str,         # C1 | C2 | C3 | C4 | none
        "location": str,           # phase2 | phase3
        "ground_truth": str        # violates | valid
    }
}
```

### Failure Log Schema

```python
# experiments/utils/failure_tracker.py

FAILURE_LOG = {
    "hypothesis_id": str,
    "phase": int,                  # 4 or 5
    "constraint_violated": str,    # C1 | C2 | C3 | C4
    "failure_message": str,
    "ground_truth": str,
    "detected_at_boundary": bool,
    "trace": dict
}
```

### Detection Result Schema

```python
# experiments/utils/validation_tracker.py

DETECTION_RESULT = {
    "hypothesis_id": str,
    "condition": str,              # A | B
    "boundary": str,               # phase2_to_phase3 | phase3_to_phase4 | phase4_to_phase5
    "detected": bool,
    "layer": str,                  # null | schema | pattern | contract
    "constraint_type": str         # C1 | C2 | C3 | C4 | none
}
```

---

## Performance Constraints

```python
# experiments/h_m3_early_detection.py

PERFORMANCE_CONFIG = {
    "corpus_generation_timeout": 300,      # 5 minutes
    "per_condition_timeout": 1800,         # 30 minutes
    "total_experiment_timeout": 7200,      # 2 hours
    "log_verbosity": "INFO"
}
```

---

## Reproducibility Settings

```python
# experiments/h_m3_corpus_generator.py

REPRODUCIBILITY = {
    "random_seed": 42,
    "corpus_version": "1.0",
    "validation_framework_version": "h-m2",
    "ground_truth_labels": True
}
```

---

## Notes

**EXISTENCE Hypothesis:** Single fixed configuration. No hyperparameter tuning, no ablations.

**Minimal PoC Config:**
- Fixed corpus size (100 hypotheses)
- Fixed violation distribution (80/20 split)
- Fixed seed (42) for reproducibility
- Two conditions (schema-only vs contract-based)

**Reuses h-m2 Infrastructure:**
- Validation constants from src/validation/constants.py
- Three-layer validation framework (schema/pattern/contract)
- Detection tracking patterns
