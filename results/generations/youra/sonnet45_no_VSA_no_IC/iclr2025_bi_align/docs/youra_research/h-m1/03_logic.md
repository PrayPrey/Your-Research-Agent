# Logic Design: Contract Expressiveness Validation (h-m1)

**Hypothesis ID:** h-m1  
**Date:** 2026-08-20  
**Agent:** Logic Agent

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase  
**Status**: API signatures verified from existing code  
**Analyzed Path**: src/validation/  
**Relevant Symbols**: Phase2AOutput, Phase2AOutputWithPatterns, Phase2AOutputWithContracts

---

## KB Patterns Applied

**Applied**: Standard Pydantic BaseModel + icontract @ensure decorators for postconditions

---

## L-1: Schema-Only Baseline (Complexity: 2, Budget: 8)

### API Signatures

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class Phase2AOutputSchemaOnly(BaseModel):
    """Schema-only validation: types + structure."""
    model_config = ConfigDict(strict=True, extra='forbid')
    
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str  # Cannot check keyword patterns (C1)
    evaluation_method: str  # Cannot blacklist keywords (C2)
    benchmark_name: str  # Cannot reference external state (C4)
```

### Constraints NOT Expressible

- C1: Keyword pattern (no "synthetic")
- C2: Keyword blacklist (no "human")
- C3: Cross-field logic (IF standard THEN in STANDARD_DATASETS)
- C4: State-based (benchmark_name in EXISTING_BENCHMARKS)

### Subtasks [6/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Define model | BaseModel with 4 fields |
| L-1-2 | Add type annotations | Literal enum for dataset_type |
| L-1-3 | Document gaps | Inline comments for C1-C4 |

---

## L-2: Contract-Based Implementation (Complexity: 3, Budget: 12)

### API Signatures

```python
from pydantic import BaseModel, Field, ConfigDict
from icontract import require, ensure, ViolationError
from typing import Literal

STANDARD_DATASETS = {"CIFAR-10", "MNIST", "ImageNet", "COCO"}
EXISTING_BENCHMARKS = {"GLUE", "SuperGLUE", "SQuAD"}

class Phase2AOutputWithContracts(BaseModel):
    """Contract-based validation: schema + behavior."""
    model_config = ConfigDict(strict=True, extra='forbid')
    
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str
    evaluation_method: str
    benchmark_name: str
    
    @require(
        lambda self: "synthetic" not in self.dataset_name.lower(),
        "C1 violation: synthetic keyword forbidden"
    )
    @require(
        lambda self: not any(kw in self.evaluation_method.lower() 
                           for kw in ["human", "manual", "annotator"]),
        "C2 violation: human evaluation forbidden"
    )
    @ensure(
        lambda self: self.dataset_type != "standard" or 
                     self.dataset_name in STANDARD_DATASETS,
        "C3 violation: unknown standard dataset"
    )
    @ensure(
        lambda self: self.benchmark_name in EXISTING_BENCHMARKS or
                     self.benchmark_name == "N/A",
        "C4 violation: new benchmark not allowed"
    )
    def model_post_init(self, __context) -> None:
        """Trigger contract validation."""
        pass
```

### Pseudo-code

```
1. On model construction:
   - Pydantic validates schema (types, required fields)
   - model_post_init triggered
2. @require decorators check before model_post_init:
   - C1: "synthetic" not in dataset_name.lower()
   - C2: no human-eval keywords in evaluation_method
3. @ensure decorators check after model_post_init:
   - C3: IF dataset_type == "standard" THEN dataset_name in STANDARD_DATASETS
   - C4: benchmark_name in EXISTING_BENCHMARKS or == "N/A"
4. On violation: raise ViolationError with constraint ID
```

### Subtasks [10/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Define constants | STANDARD_DATASETS, EXISTING_BENCHMARKS |
| L-2-2 | Add schema | Same as L-1 |
| L-2-3 | Add C1 contract | @require for synthetic keyword |
| L-2-4 | Add C2 contract | @require for human eval |
| L-2-5 | Add C3 contract | @ensure for cross-field |
| L-2-6 | Add C4 contract | @ensure for state-based |
| L-2-7 | Hook model_post_init | Trigger contract checks |

---

## L-3: Coverage Experiment (Complexity: 2, Budget: 10)

### API Signatures

```python
from typing import Dict, List
from pathlib import Path
import yaml

def run_coverage_test(test_cases_path: Path) -> Dict[str, float]:
    """Run constraint coverage comparison.
    
    Returns: {"schema_coverage": 0.0, "contract_coverage": 1.0, "gap": 1.0}
    """
    ...

def validate_with_schema(test_input: Dict) -> bool:
    """Test schema-only validator. Returns: True if violation caught."""
    ...

def validate_with_contracts(test_input: Dict) -> bool:
    """Test contract-based validator. Returns: True if violation caught."""
    ...
```

### Pseudo-code

```
1. Load test_cases.yaml (5 cases: TC-M1-01 to TC-M1-05)
2. FOR each test case WITH constraint_violated != null:
   a. Try schema-only:
      - Phase2AOutputSchemaOnly(**test_input)
      - Catch ValidationError → schema_detected += 1
   b. Try contract-based:
      - Phase2AOutputWithContracts(**test_input)
      - Catch ViolationError → contract_detected += 1
3. Calculate:
   - schema_coverage = schema_detected / 4
   - contract_coverage = contract_detected / 4
   - gap = contract_coverage - schema_coverage
4. Assert:
   - contract_coverage >= 1.0
   - schema_coverage < 0.5
   - gap >= 0.75
```

### Coverage Formula

```
Coverage = (Constraints Explicitly Checked / Total Constraints) × 100%
Expressiveness Gap = Contract Coverage - Schema Coverage
```

### Subtasks [8/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Load test cases | Parse YAML |
| L-3-2 | Schema validator | Try-except ValidationError |
| L-3-3 | Contract validator | Try-except ViolationError |
| L-3-4 | Count detections | Track schema vs contract |
| L-3-5 | Calculate coverage | Apply formula |
| L-3-6 | Verify thresholds | Assert success criteria |

---

## L-4: Test Case Definitions (Complexity: 1, Budget: 6)

### API Signatures

```python
# tests/h_m1/test_cases.yaml
test_cases:
  - id: str
    description: str
    constraint_violated: str | null  # "C1" | "C2" | "C3" | "C4" | null
    input:
      dataset_type: str
      dataset_name: str
      evaluation_method: str
      benchmark_name: str
    expected:
      schema_detects: bool
      contract_detects: bool
```

### Test Cases

| ID | Constraint | Input Violation | Expected |
|----|-----------|-----------------|----------|
| TC-M1-01 | C1 | dataset_name="SyntheticDataset2024" | schema=False, contract=True |
| TC-M1-02 | C2 | evaluation_method="human annotators" | schema=False, contract=True |
| TC-M1-03 | C3 | dataset_type="standard", dataset_name="Unknown" | schema=False, contract=True |
| TC-M1-04 | C4 | benchmark_name="NewBenchmark2024" | schema=False, contract=True |
| TC-M1-05 | None | All valid | schema=False, contract=False |

### Subtasks [5/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Define structure | YAML schema |
| L-4-2 | Create TC-M1-01 | C1 violation |
| L-4-3 | Create TC-M1-02 | C2 violation |
| L-4-4 | Create TC-M1-03 | C3 violation |
| L-4-5 | Create TC-M1-04 | C4 violation |
| L-4-6 | Create TC-M1-05 | Valid case |

---

## External Dependencies

**None** - Self-contained proof-of-concept using only:
- Pydantic >=2.0 (schema validation)
- icontract >=2.0 (contract decorators)
- pyyaml >=6.0 (test case loading)

---

## Budget Summary

| Task | Complexity | Budget | Used | Remaining |
|------|-----------|--------|------|-----------|
| L-1 | 2 | 8 | 6 | 2 |
| L-2 | 3 | 12 | 10 | 2 |
| L-3 | 2 | 10 | 8 | 2 |
| L-4 | 1 | 6 | 5 | 1 |
| **Total** | **8** | **36** | **29** | **7** |

---

**Status**: Complete  
**Next Phase**: Phase 4 Implementation (Coder Agent)
