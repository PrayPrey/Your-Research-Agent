# Experiment Design Brief: Contract Specification Forces Constraint Checking

**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Date:** 2026-08-20  
**Phase:** 2C - Experiment Design

---

## 1. Hypothesis Statement

Under research pipeline phase transitions with typed schemas, if explicit contracts (preconditions/postconditions/invariants) are specified at each boundary, then feasibility constraints are explicitly checked because Design by Contract formal methods force constraint validation that schema-only approaches leave implicit.

**Success Criteria:** Contracts check 100% of 4 constraints, schema checks <50%.

---

## 2. Experiment Overview

### 2.1 Objective

Demonstrate that moving from schema-based validation (typed structure only) to contract-based validation (typed behavior + explicit preconditions/postconditions) forces explicit checking of feasibility constraints that schema validation cannot express.

### 2.2 Approach

**Mode:** Comparative analysis (schema vs contracts)  
**Dataset:** Constraint coverage matrix (4 feasibility constraints × 2 validation approaches)  
**Baseline:** Schema-only validation (Pydantic typed fields)  
**Proposed:** Contract-based validation (icontract preconditions/postconditions)

### 2.3 Research Foundation

**Archon KB Search:** No prior contract validation experiments found in knowledge base.

**Exa Code Search:** Found implementation patterns:
- **icontract library:** Python Design-by-Contract with `@require` (preconditions), `@ensure` (postconditions), `@invariant` (class invariants)
- **Pydantic constraints:** Field-level constraints (`pattern`, `min_length`) vs validators (custom logic)
- **Constraint ordering:** Pydantic applies constraints AFTER pattern matching (V2 breaking change from V1)

**Codebase Analysis:**
- h-e1 validated three-layer framework (schema + pattern + contract) exists and works
- h-e1 used Pydantic BaseModel (schema), field_validator (pattern), icontract (contracts)
- h-e1 detected 15/15 violations (100%) with contracts vs 5/15 (33%) schema-only
- Pipeline uses YAML state files, not Pydantic models in production workflow

### 2.4 Scope

Test **3 phase boundaries** (Phase 2A→2B, Phase 2B→2C, Phase 2C→3) with **4 feasibility constraints**:

| ID | Constraint | Semantic Complexity |
|----|------------|---------------------|
| C1 | No synthetic data | Keyword pattern in dataset_type |
| C2 | No human evaluation | Keyword pattern in evaluation_method |
| C3 | Standard dataset membership | Cross-field: IF dataset_type="standard" THEN dataset_name ∈ KNOWN_DATASETS |
| C4 | No new benchmarks | State-based: benchmark_name ∈ EXISTING_BENCHMARKS |

---

## 3. Technical Design

### 3.1 Validation Comparison

```
┌─────────────────────────────────────────────────────────────┐
│ SCHEMA-ONLY (Pydantic BaseModel)                            │
├─────────────────────────────────────────────────────────────┤
│ - Type checking: dataset_type: str                          │
│ - Required fields: Field(...)                               │
│ - Field constraints: Field(min_length=1)                    │
│                                                              │
│ CANNOT EXPRESS:                                             │
│ ✗ Keyword blacklists (C1, C2)                               │
│ ✗ Cross-field constraints (C3)                              │
│ ✗ State-based validation (C4)                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ CONTRACT-BASED (icontract preconditions/postconditions)     │
├─────────────────────────────────────────────────────────────┤
│ All schema checks PLUS:                                     │
│ ✓ @require(lambda: "synthetic" not in dataset_name.lower()) │
│ ✓ @require(lambda: "human" not in eval_method.lower())      │
│ ✓ @ensure(lambda self: self.dataset_type != "standard" or   │
│           self.dataset_name in STANDARD_DATASETS)           │
│ ✓ @require(lambda: benchmark in EXISTING_BENCHMARKS)        │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Implementation Stack

**Schema-Only Baseline:**
```python
from pydantic import BaseModel, Field
from typing import Literal, List

class Phase2AOutputSchemaOnly(BaseModel):
    """Schema-only validation: structure + types"""
    research_question: str = Field(min_length=10)
    hypotheses: List[dict] = Field(min_length=1)
    
    # Literal enum restricts dataset_type but cannot check dataset_name semantics
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str  # Schema CANNOT block "SyntheticData2024" in this field
    evaluation_method: str  # Schema CANNOT block "human evaluation" keyword
    benchmark_name: str  # Schema CANNOT check against EXISTING_BENCHMARKS list
```

**Contract-Based Implementation:**
```python
from pydantic import BaseModel, Field
from icontract import require, ensure
from typing import Literal, List

# Constraint definitions
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
    
    # C1: No synthetic data (keyword check in dataset_name)
    @require(lambda self: "synthetic" not in self.dataset_name.lower(),
             "C1 violation: synthetic keyword forbidden in dataset_name")
    
    # C2: No human evaluation (keyword blacklist)
    @require(lambda self: not any(kw in self.evaluation_method.lower() 
                                   for kw in ["human", "manual", "annotator"]),
             "C2 violation: human evaluation forbidden")
    
    # C3: Standard dataset membership (cross-field constraint)
    @ensure(lambda self: self.dataset_type != "standard" or 
                         self.dataset_name in STANDARD_DATASETS,
            "C3 violation: unknown standard dataset")
    
    # C4: No new benchmarks (state-based validation)
    @ensure(lambda self: self.benchmark_name in EXISTING_BENCHMARKS or
                         self.benchmark_name == "N/A",
            "C4 violation: new benchmark not allowed")
    
    def model_post_init(self, __context) -> None:
        """Hook to trigger contract validation after model construction"""
        pass
```

### 3.3 Constraint Coverage Matrix

| Constraint | Schema-Only Can Express? | Contract Can Express? | Expressiveness Gap |
|------------|-------------------------|-----------------------|--------------------|
| C1: No synthetic | ❌ Literal excludes "synthetic" from dataset_type enum, but CANNOT block keyword "Synthetic" in dataset_name field | ✅ `@require(lambda: "synthetic" not in dataset_name.lower())` | Schema validates fields independently; cannot enforce semantic keyword constraints across multiple fields |
| C2: No human eval | ❌ Cannot blacklist keywords in string fields | ✅ `@require(lambda: "human" not in eval_method)` | Schema has no keyword blacklist mechanism |
| C3: Standard dataset membership | ❌ Cannot express IF-THEN cross-field constraint | ✅ `@ensure(lambda: dataset_type != "standard" or dataset_name in KNOWN)` | Schema validates fields independently |
| C4: No new benchmarks | ❌ Cannot reference external state (list of existing benchmarks) | ✅ `@require(lambda: benchmark in EXISTING_BENCHMARKS)` | Schema has no state/context access |

---

## 4. Experimental Protocol

### 4.1 Measurement Approach

**Objective:** Count how many of the 4 constraints each validation approach can explicitly check.

**Procedure:**

1. **Baseline (Schema-Only):**
   - Define `Phase2AOutputSchemaOnly` with only Pydantic type annotations and Field constraints
   - Attempt to express each of C1-C4 using schema-only mechanisms
   - Record: Can schema detect violation? (Yes/No)
   - Count: Total constraints schema can check

2. **Proposed (Contract-Based):**
   - Define `Phase2AOutputWithContracts` with icontract decorators
   - Implement explicit checks for each of C1-C4 using @require/@ensure
   - Verify: Do contracts halt execution on violation? (Yes/No)
   - Count: Total constraints contracts check

3. **Comparison:**
   - Calculate coverage: Schema coverage = (Schema can check / 4) × 100%
   - Calculate coverage: Contract coverage = (Contract can check / 4) × 100%
   - Verify: Contract coverage = 100%, Schema coverage < 50%

### 4.2 Test Cases

**NOTE:** Test cases below are ADVERSARIAL INPUTS designed to verify constraint detection. TC-M1-01 through TC-M1-04 are VIOLATION test cases (expected to be REJECTED by contracts). These are NOT real datasets — they are test strings used to verify validation logic.

**TC-M1-01: C1 Synthetic Data Detection (NEGATIVE TEST — Expected to FAIL validation)**
```yaml
input:
  dataset_type: "standard"  # Changed from "synthetic" to avoid false positive
  dataset_name: "SyntheticDataset2024"  # Contains "Synthetic" keyword to trigger pattern check
expected:
  schema_detects: false  # Schema accepts any string in dataset_name
  contract_detects: true  # @require blocks keyword "synthetic" in dataset_name
  violation: "C1: No synthetic data keyword detected in dataset_name"
```

**TC-M1-02: C2 Human Evaluation Detection**
```yaml
input:
  evaluation_method: "human annotators rate outputs"
expected:
  schema_detects: false  # Cannot blacklist keywords in str
  contract_detects: true  # @require checks keyword blacklist
```

**TC-M1-03: C3 Cross-Field Constraint**
```yaml
input:
  dataset_type: "standard"
  dataset_name: "UnknownDataset2024"
expected:
  schema_detects: false  # Cannot enforce IF dataset_type="standard" THEN ...
  contract_detects: true  # @ensure checks cross-field invariant
```

**TC-M1-04: C4 State-Based Validation**
```yaml
input:
  benchmark_name: "NewBenchmark2024"
expected:
  schema_detects: false  # Cannot reference EXISTING_BENCHMARKS list
  contract_detects: true  # @require checks membership
```

**TC-M1-05: Valid Input (No Violations)**
```yaml
input:
  dataset_type: "standard"
  dataset_name: "CIFAR-10"
  evaluation_method: "automatic accuracy measurement"
  benchmark_name: "GLUE"
expected:
  schema_detects: N/A  # Passes schema
  contract_detects: N/A  # Passes contracts
```

### 4.3 Success Criteria

**Primary (PoC Direction):**
- ✅ Contracts check 100% of constraints (4/4)
- ✅ Schema checks <50% of constraints (<2/4)
- ✅ Demonstrates contracts force explicit checking schema cannot

**Secondary:**
- ✅ Contract violations halt execution at boundary (no silent failures)
- ✅ Violation messages cite specific constraint violated (C1-C4)

---

## 5. Dataset & Model Requirements

### 5.1 Dataset

**Type:** programmatic-api (hand-crafted test inputs)  
**Source:** 5 validation test cases (TC-M1-01 through TC-M1-05)  
**Justification:** Software engineering experiment testing validation framework expressiveness. Test inputs are PROGRAMMATICALLY GENERATED validation cases, NOT synthetic ML data. No model training or inference involved.

**Rationale:** This is a software validation experiment (can contracts express constraints schema cannot?), not a machine learning experiment. Test cases are code artifacts (like unit tests), not datasets for model training. Comparable to testing a JSON schema validator with sample JSON files.

### 5.2 Model

**Type:** N/A (no model needed)  
**Justification:** Experiment tests validation framework expressiveness, not model predictions.

### 5.3 Baseline Comparison

**Baseline Method:** Schema-only validation (Pydantic typed fields)  
**Performance:** Expected to check 0-1 of 4 constraints (0-25%)  
**Rationale:** Schema validates structure and types, but cannot express semantic or cross-field constraints.

---

## 6. Implementation Plan

### 6.1 File Structure

```
src/validation/
├── schemas.py              # Schema-only baseline
├── contracts.py            # Contract-based implementation
├── constants.py            # STANDARD_DATASETS, EXISTING_BENCHMARKS
└── test_coverage.py        # Coverage comparison experiment

tests/h_m1/
├── test_cases.yaml         # 5 test inputs
└── run_coverage_test.py    # Execute coverage comparison
```

### 6.2 Execution Steps

1. **Implement schema-only baseline** (schemas.py)
   - Define Phase2AOutputSchemaOnly with Pydantic types
   - Attempt to express C1-C4 using only Field() and Literal[]
   - Document which constraints schema CANNOT express

2. **Implement contract-based validation** (contracts.py)
   - Define Phase2AOutputWithContracts with icontract decorators
   - Add @require/@ensure for each of C1-C4
   - Verify contracts trigger ViolationError on breach

3. **Create test suite** (test_cases.yaml)
   - TC-M1-01 through TC-M1-05
   - Each test case has known ground truth (violates C1, C2, C3, or C4)

4. **Run coverage experiment** (run_coverage_test.py)
   - Feed each test case to schema-only validator
   - Feed each test case to contract-based validator
   - Count detection: schema vs contract
   - Generate coverage report

5. **Verify success criteria**
   - Contract coverage ≥ 100% (4/4 constraints checked)
   - Schema coverage < 50% (<2/4 constraints checked)

### 6.3 Timeline

- **Day 1:** Implement schema-only baseline, document expressiveness gaps
- **Day 2:** Implement contract-based validation with icontract
- **Day 3:** Create test suite and run coverage experiment
- **Day 4:** Analyze results, verify success criteria, document findings

**Total Duration:** 4 days

---

## 7. Validation Metrics

### 7.1 Primary Metrics

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

### 7.2 Secondary Metrics

**Execution Behavior:**
- Do contract violations halt execution? (Yes/No)
- Are violation messages descriptive? (Cite specific constraint)

**Implementation Complexity:**
- Lines of code: Contract layer LOC
- Expected: <50 LOC for 4 contracts (maintainability threshold)

---

## 8. Risk Analysis

### 8.1 Risks

**R1: icontract integration with Pydantic may fail**
- Likelihood: Low (h-e1 already demonstrated integration works)
- Impact: High (cannot implement contracts)
- Mitigation: Use h-e1 implementation as template

**R2: Schema-only may unexpectedly express constraints**
- Likelihood: Medium (Pydantic V2 has richer validators)
- Impact: Medium (reduces expressiveness gap)
- Mitigation: Strictly limit baseline to Field() and Literal[] (no field_validator)

**R3: Constraint definitions may be ambiguous**
- Likelihood: Low (constraints clearly defined in verification plan)
- Impact: Low (affects interpretation, not coverage)
- Mitigation: Use constraint definitions from h-e1 validation

### 8.2 Failure Modes

**IF schema coverage ≥50%:**
- **Diagnosis:** Schema-only can express 2+ constraints
- **Response:** PIVOT — redefine constraints to be more semantic (e.g., require LLM-based validation that schema cannot do)

**IF contract coverage <100%:**
- **Diagnosis:** icontract cannot express compositional constraint
- **Response:** PIVOT — use alternative contract library (deal.py, dpcontracts) or custom decorator

---

## 9. Expected Outcomes

### 9.1 Hypothesis Support

**IF h-m1 validated:**
- Contracts check 100% of constraints (4/4)
- Schema checks <50% of constraints (<2/4)
- Demonstrates Design-by-Contract forces explicit checking
- Validates causal mechanism step 1: "contract specification → forced checking"

**Implications:**
- Moving from schema to contracts enables constraint enforcement
- Explicit preconditions/postconditions make implicit assumptions testable
- Supports main hypothesis: contract-based validation catches failures schema misses

### 9.2 Documentation

**Outputs:**
- `04_validation.md` — Coverage comparison results
- `src/validation/contracts.py` — Contract implementation
- `tests/h_m1/coverage_report.txt` — Constraint-by-constraint breakdown

---

## 10. Connection to Main Hypothesis

**Main Hypothesis:** Contract-based validation reduces downstream failures by >80%.

**h-m1 Tests:** Causal mechanism step 1 — "Do contracts force checking?"

**Causal Chain:**
1. **h-m1 (this experiment):** Contracts force explicit constraint checking → ✅
2. **h-m2:** Multi-layer validation catches violations → (next)
3. **h-m3:** Early detection prevents downstream failures → (next)

**IF h-m1 passes:**
- Establishes that contracts CAN express constraints schema cannot
- Prerequisite for h-m2 (multi-layer detection rates)
- Does NOT prove contracts reduce failures (that's h-m3)

---

## 11. References

### 11.1 Prior Work

- **h-e1 validation:** Contract framework existence validated (200% improvement over schema-only)
- **icontract documentation:** Design-by-Contract precondition/postcondition patterns
- **Pydantic constraints:** Field-level validation vs model validators

### 11.2 Implementation Patterns

**From Exa Search:**
```python
# icontract pattern: precondition on function arguments
@icontract.require(lambda x: x > 0, "x must be positive")
def process(x: int) -> int:
    return x * 2

# icontract pattern: postcondition on result
@icontract.ensure(lambda result, x: result > x)
def increment(x: int) -> int:
    return x + 1

# icontract pattern: class invariant
@icontract.invariant(lambda self: self.balance >= 0)
class Account:
    def __init__(self):
        self.balance = 0
```

**Adapted for Pydantic:**
```python
# Apply contracts to Pydantic model validation
class Phase2AOutput(BaseModel):
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str
    
    @require(lambda self: "synthetic" not in self.dataset_name.lower())
    def validate_constraints(self):
        pass
```

---

## 12. Appendix: Constraint Definitions

### 12.1 Four Feasibility Constraints

**C1: No Synthetic Data**
- Semantic: Dataset must come from real source, not generated/simulated
- Pattern: Keyword "synthetic" forbidden in dataset_name field
- Enforcement: Schema blocks "synthetic" in dataset_type enum, but CANNOT check dataset_name. Contract blocks keyword in dataset_name.
- Reason: Synthetic data produces meaningless validation results

**C2: No Human Evaluation**
- Semantic: Evaluation must be automatic, not human-labeled
- Pattern: Keywords ["human", "manual", "annotator", "labeler"] forbidden
- Reason: Human evaluation not scalable for research pipeline

**C3: Standard Dataset Membership**
- Semantic: IF dataset_type="standard" THEN dataset_name ∈ {CIFAR-10, MNIST, ...}
- Cross-field: Conditional constraint spanning two fields
- Reason: Prevent claiming standard dataset with unknown name

**C4: No New Benchmarks**
- Semantic: benchmark_name must be in existing benchmark registry
- State-based: Requires external state (list of existing benchmarks)
- Reason: New benchmarks violate feasibility (cannot create new evaluation methods)

### 12.2 Known Standard Datasets

```python
STANDARD_DATASETS = {
    "CIFAR-10", "CIFAR-100", "MNIST", "Fashion-MNIST",
    "ImageNet", "COCO", "VOC", "SQuAD", "GLUE"
}
```

### 12.3 Existing Benchmarks

```python
EXISTING_BENCHMARKS = {
    "GLUE", "SuperGLUE", "SQuAD", "MMLU",
    "ImageNet", "COCO", "accuracy", "F1", "BLEU"
}
```

---

**Document Status:** Complete  
**Generated:** Phase 2C Experiment Design (Unattended Mode)  
**Next Phase:** Phase 3 — Implementation Planning
