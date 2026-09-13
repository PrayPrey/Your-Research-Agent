# Product Requirements Document: Contract Expressiveness Validation

**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Date:** 2026-08-20  
**Phase:** 3 - Implementation Planning

---

## 1. Executive Summary

### 1.1 Purpose

Implement a constraint coverage comparison experiment demonstrating that contract-based validation (icontract preconditions/postconditions) forces explicit checking of feasibility constraints that schema-only validation (Pydantic typed fields) cannot express.

### 1.2 Success Criteria

**Primary:**
- Contract-based validation checks 100% of 4 feasibility constraints (4/4)
- Schema-only validation checks <50% of constraints (<2/4)
- Expressiveness gap ≥75 percentage points

**Secondary:**
- Contract violations halt execution at phase boundaries
- Violation messages cite specific constraint IDs (C1-C4)
- Implementation complexity <50 LOC for contract layer

### 1.3 Scope

**In Scope:**
- Schema-only baseline implementation (Pydantic BaseModel)
- Contract-based implementation (icontract decorators)
- 5 validation test cases (4 violations + 1 valid)
- Coverage comparison experiment
- Validation report (04_validation.md)

**Out of Scope:**
- Multi-layer validation (tested in h-e1)
- Performance benchmarking (not a metric)
- Integration with real pipeline (proof-of-concept only)
- Additional constraints beyond C1-C4

---

## 2. Background

### 2.1 Research Context

**Hypothesis Statement:** Under research pipeline phase transitions with typed schemas, if explicit contracts (preconditions/postconditions/invariants) are specified at each boundary, then feasibility constraints are explicitly checked because Design by Contract formal methods force constraint validation that schema-only approaches leave implicit.

**Prerequisites:**
- h-e1 validated that contract framework exists and works (200% improvement)

**Causal Chain:**
1. **h-m1 (this experiment):** Contracts force explicit constraint checking
2. **h-m2:** Multi-layer validation catches violations
3. **h-m3:** Early detection prevents downstream failures

### 2.2 Technical Foundation

**Baseline Limitation:** Pydantic schema validation validates structure and types but cannot express:
- Keyword patterns (C1: no "synthetic" in dataset_name)
- Keyword blacklists (C2: no "human" in evaluation_method)
- Cross-field constraints (C3: IF dataset_type="standard" THEN dataset_name ∈ KNOWN)
- State-based validation (C4: benchmark_name ∈ EXISTING_BENCHMARKS)

**Proposed Solution:** icontract Design-by-Contract library adds:
- `@require`: Preconditions checked at function entry
- `@ensure`: Postconditions checked at function exit
- `@invariant`: Class invariants checked after init and mutations

---

## 3. Requirements

### 3.1 Functional Requirements

**FR-01: Schema-Only Baseline**
- Implement `Phase2AOutputSchemaOnly` using Pydantic BaseModel
- Use only Field() constraints and Literal[] enums
- No field_validator or model_validator decorators
- Document which constraints schema CANNOT express

**FR-02: Contract-Based Implementation**
- Implement `Phase2AOutputWithContracts` with icontract decorators
- Add @require/@ensure for each of C1-C4
- Contracts must trigger ViolationError on breach
- Violation messages cite specific constraint ID

**FR-03: Constraint Definitions**
- C1: No synthetic data (keyword pattern)
- C2: No human evaluation (keyword blacklist)
- C3: Standard dataset membership (cross-field)
- C4: No new benchmarks (state-based)

**FR-04: Test Suite**
- TC-M1-01: C1 violation (dataset_name contains "synthetic")
- TC-M1-02: C2 violation (evaluation_method contains "human")
- TC-M1-03: C3 violation (dataset_type="standard" but dataset_name not in KNOWN)
- TC-M1-04: C4 violation (benchmark_name not in EXISTING_BENCHMARKS)
- TC-M1-05: Valid input (no violations)

**FR-05: Coverage Experiment**
- Feed each test case to schema-only validator
- Feed each test case to contract-based validator
- Count detections: schema vs contract
- Generate coverage report with per-constraint breakdown

**FR-06: Validation Report**
- Document coverage percentages (schema vs contract)
- Calculate expressiveness gap
- Verify success criteria met
- Output: 04_validation.md

### 3.2 Non-Functional Requirements

**NFR-01: Maintainability**
- Contract layer implementation <50 LOC
- Clear error messages citing constraint IDs

**NFR-02: Reproducibility**
- All test cases defined in YAML
- Deterministic test execution (no randomness)

**NFR-03: Documentation**
- Each constraint has inline comment explaining semantic meaning
- Test cases tagged with ground truth (which constraint violated)

---

## 4. Architecture Overview

### 4.1 Component Structure

```
src/validation/
├── __init__.py
├── constants.py              # STANDARD_DATASETS, EXISTING_BENCHMARKS
├── schemas.py                # Schema-only baseline
└── contracts.py              # Contract-based implementation

tests/h_m1/
├── __init__.py
├── test_cases.yaml           # 5 validation test cases
└── run_coverage_test.py      # Coverage comparison experiment
```

### 4.2 Data Flow

```
Test Cases (YAML)
    ↓
Schema-Only Validator → Detection Count (Schema)
    ↓
Contract-Based Validator → Detection Count (Contract)
    ↓
Coverage Calculation → Report (04_validation.md)
```

---

## 5. Implementation Details

### 5.1 Schema-Only Baseline

```python
from pydantic import BaseModel, Field
from typing import Literal, List

class Phase2AOutputSchemaOnly(BaseModel):
    """Schema-only validation: structure + types"""
    research_question: str = Field(min_length=10)
    hypotheses: List[dict] = Field(min_length=1)
    
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str  # Schema CANNOT check keyword patterns
    evaluation_method: str  # Schema CANNOT blacklist keywords
    benchmark_name: str  # Schema CANNOT reference external state
```

### 5.2 Contract-Based Implementation

```python
from pydantic import BaseModel, Field
from icontract import require, ensure
from typing import Literal, List

STANDARD_DATASETS = {"CIFAR-10", "MNIST", "ImageNet", "COCO"}
EXISTING_BENCHMARKS = {"GLUE", "SuperGLUE", "SQuAD"}

class Phase2AOutputWithContracts(BaseModel):
    """Contract-based validation: schema + behavior constraints"""
    research_question: str = Field(min_length=10)
    hypotheses: List[dict] = Field(min_length=1)
    
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str
    evaluation_method: str
    benchmark_name: str
    
    @require(lambda self: "synthetic" not in self.dataset_name.lower(),
             "C1 violation: synthetic keyword forbidden in dataset_name")
    @require(lambda self: not any(kw in self.evaluation_method.lower() 
                                   for kw in ["human", "manual", "annotator"]),
             "C2 violation: human evaluation forbidden")
    @ensure(lambda self: self.dataset_type != "standard" or 
                         self.dataset_name in STANDARD_DATASETS,
            "C3 violation: unknown standard dataset")
    @ensure(lambda self: self.benchmark_name in EXISTING_BENCHMARKS or
                         self.benchmark_name == "N/A",
            "C4 violation: new benchmark not allowed")
    def model_post_init(self, __context) -> None:
        """Trigger contract validation after model construction"""
        pass
```

### 5.3 Test Cases (YAML)

```yaml
# tests/h_m1/test_cases.yaml
test_cases:
  - id: TC-M1-01
    description: "C1 Synthetic Data Detection"
    constraint_violated: C1
    input:
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
      dataset_type: "standard"
      dataset_name: "CIFAR-10"
      evaluation_method: "automatic accuracy measurement"
      benchmark_name: "GLUE"
    expected:
      schema_detects: false  # N/A (passes)
      contract_detects: false  # N/A (passes)
```

### 5.4 Coverage Experiment

```python
# tests/h_m1/run_coverage_test.py
import yaml
from src.validation.schemas import Phase2AOutputSchemaOnly
from src.validation.contracts import Phase2AOutputWithContracts

def run_coverage_test():
    with open('test_cases.yaml') as f:
        test_cases = yaml.safe_load(f)['test_cases']
    
    schema_detected = 0
    contract_detected = 0
    
    for tc in test_cases:
        if tc['constraint_violated'] is None:
            continue  # Skip valid case
        
        # Test schema-only
        try:
            Phase2AOutputSchemaOnly(**tc['input'])
            schema_detected += 0  # No violation caught
        except Exception:
            schema_detected += 1  # Violation caught
        
        # Test contract-based
        try:
            Phase2AOutputWithContracts(**tc['input'])
            contract_detected += 0  # No violation caught
        except Exception:
            contract_detected += 1  # Violation caught
    
    total_constraints = 4
    schema_coverage = schema_detected / total_constraints
    contract_coverage = contract_detected / total_constraints
    gap = contract_coverage - schema_coverage
    
    print(f"Schema Coverage: {schema_coverage:.1%}")
    print(f"Contract Coverage: {contract_coverage:.1%}")
    print(f"Expressiveness Gap: {gap:.1%}")
    
    assert contract_coverage >= 1.0, "Contract coverage must be 100%"
    assert schema_coverage < 0.5, "Schema coverage must be <50%"
    assert gap >= 0.75, "Expressiveness gap must be ≥75 percentage points"

if __name__ == '__main__':
    run_coverage_test()
```

---

## 6. Validation Metrics

### 6.1 Primary Metrics

**Constraint Coverage:**
```
Coverage = (Constraints Explicitly Checked / Total Constraints) × 100%
```

- **Schema-Only Coverage:** Expected 0-25% (0-1 of 4 constraints)
- **Contract-Based Coverage:** Expected 100% (4 of 4 constraints)

**Expressiveness Gap:**
```
Gap = Contract Coverage - Schema Coverage
```
- **Expected Gap:** ≥75 percentage points

### 6.2 Success Thresholds

| Metric | Threshold | Result |
|--------|-----------|--------|
| Contract Coverage | ≥100% | PASS/FAIL |
| Schema Coverage | <50% | PASS/FAIL |
| Expressiveness Gap | ≥75 pp | PASS/FAIL |
| Contract LOC | <50 lines | PASS/FAIL |

---

## 7. Risk Management

### 7.1 Risks

**R1: icontract integration with Pydantic may fail**
- **Likelihood:** Low (h-e1 validated integration works)
- **Impact:** High (cannot implement contracts)
- **Mitigation:** Use h-e1 implementation as template

**R2: Schema-only may unexpectedly express constraints**
- **Likelihood:** Medium (Pydantic V2 has validators)
- **Impact:** Medium (reduces gap)
- **Mitigation:** Strictly limit baseline to Field() + Literal[] (no field_validator)

**R3: Constraint definitions may be ambiguous**
- **Likelihood:** Low (constraints defined in h-e1)
- **Impact:** Low (affects interpretation)
- **Mitigation:** Use exact C1-C4 definitions from verification plan

### 7.2 Failure Modes

**IF schema_coverage ≥50%:**
- **Diagnosis:** Schema-only can express 2+ constraints
- **Response:** PIVOT — redefine constraints to be more semantic

**IF contract_coverage <100%:**
- **Diagnosis:** icontract cannot express compositional constraint
- **Response:** PIVOT — use alternative contract library (deal.py, dpcontracts)

---

## 8. Timeline

| Day | Milestone | Deliverable |
|-----|-----------|-------------|
| 1 | Implement schema-only baseline | `src/validation/schemas.py` |
| 1 | Document expressiveness gaps | Comments in schemas.py |
| 2 | Implement contract-based validation | `src/validation/contracts.py` |
| 2 | Verify contract violations halt execution | Unit tests |
| 3 | Create test suite | `tests/h_m1/test_cases.yaml` |
| 3 | Run coverage experiment | `tests/h_m1/run_coverage_test.py` |
| 4 | Analyze results | Coverage report |
| 4 | Verify success criteria | `04_validation.md` |

**Total Duration:** 4 days

---

## 9. Dependencies

### 9.1 Prerequisites

- h-e1 validation complete (contract framework exists)
- Python ≥3.11
- Pydantic ≥2.0
- icontract ≥2.0
- pytest ≥7.0
- pyyaml ≥6.0

### 9.2 External Dependencies

None (self-contained proof-of-concept)

---

## 10. Deliverables

1. **Source Code:**
   - `src/validation/constants.py`
   - `src/validation/schemas.py`
   - `src/validation/contracts.py`

2. **Test Suite:**
   - `tests/h_m1/test_cases.yaml`
   - `tests/h_m1/run_coverage_test.py`

3. **Documentation:**
   - `04_validation.md` (coverage report)
   - Inline comments explaining each constraint

4. **Validation Artifacts:**
   - Coverage comparison results
   - Constraint-by-constraint breakdown
   - Gate validation (PASS/FAIL)

---

## 11. Acceptance Criteria

**Primary (Gate Criteria):**
- ✅ Contract coverage ≥100% (4/4 constraints)
- ✅ Schema coverage <50% (<2/4 constraints)
- ✅ Expressiveness gap ≥75 percentage points

**Secondary:**
- ✅ Contract violations halt execution (no silent failures)
- ✅ Violation messages cite constraint IDs (C1-C4)
- ✅ Contract layer implementation <50 LOC

**Documentation:**
- ✅ 04_validation.md generated with results
- ✅ Each constraint has inline explanation
- ✅ Test cases tagged with ground truth

---

**Document Status:** Complete  
**Generated:** Phase 3 Implementation Planning (Unattended Mode)  
**Next Phase:** Launch architecture/logic/config agents
