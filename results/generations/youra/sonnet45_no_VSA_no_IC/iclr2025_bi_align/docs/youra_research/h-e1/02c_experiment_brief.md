# Experiment Design Brief: Contract-Based Phase Transition Validation

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-08-20  
**Phase:** 2C - Experiment Design

---

## 1. Hypothesis Statement

Under research workflows with sequential multi-phase structure and typed interfaces, if contract-based validation (schema + pattern + composition layers) is implemented at phase boundaries, then constraint violations can be detected before Phase 4/5 execution because contracts enforce preconditions/postconditions/invariants that schema-only validation cannot check.

**Success Criteria:** Contract-based validation detects >50% more violations than schema-only validation.

---

## 2. Experiment Overview

### 2.1 Objective

Demonstrate that a three-layer contract validation framework (schema + pattern + composition) can be implemented for research pipeline phase transitions and detects constraint violations that schema-only validation misses.

### 2.2 Approach

**Mode:** Proof-of-Concept (PoC) validation  
**Dataset:** Controlled adversarial test suite (20 test cases)  
**Baseline:** Schema-only validation (Pydantic BaseModel)  
**Proposed:** Contract-based validation (Pydantic + contractme)

### 2.3 Scope

Test **one phase boundary** (Phase 2A → Phase 2B) with **4 feasibility constraints**:
1. No new benchmarks/datasets
2. No synthetic data generation
3. No human evaluation
4. Real standard datasets only

---

## 3. Technical Design

### 3.1 Validation Architecture

```
Layer 1: SCHEMA VALIDATION (Pydantic BaseModel)
  ↓ Type checking, required fields, field types
  
Layer 2: PATTERN VALIDATION (Pydantic field_validator)
  ↓ Constraint pattern matching via regex/predicates
  
Layer 3: CONTRACT VALIDATION (contractme decorators)
  ↓ Preconditions, postconditions, compositional invariants
```

### 3.2 Implementation Stack

**Schema Layer:**
- Library: Pydantic v2.x BaseModel
- Mechanism: Type annotations + Field() descriptors
- Coverage: Structure, types, required fields

**Pattern Layer:**
- Library: Pydantic field_validator decorators
- Mechanism: Regex patterns + custom predicates
- Coverage: 4 feasibility constraint patterns

**Contract Layer:**
- Library: contractme v2.2.0
- Mechanism: @precondition/@postcondition decorators
- Coverage: Cross-field relationships, state invariants

### 3.3 Phase 2A→2B Interface Contract

**Input (Phase 2A Output):**
```python
from pydantic import BaseModel, Field, field_validator
from contractme import precondition, postcondition
from typing import List, Literal

class Phase2AOutput(BaseModel):
    """Phase 2A: Extended Hypothesis Analysis output schema"""
    research_question: str = Field(min_length=10)
    detailed_question: str
    reference_papers: List[dict]
    
    hypotheses: List[dict]  # Sub-hypotheses
    causal_mechanism: dict
    predictions: List[dict]
    
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    model_approach: str
    
    # Pattern layer: No synthetic data
    @field_validator("dataset_type")
    @classmethod
    def no_synthetic_data(cls, v):
        if v == "synthetic":
            raise ValueError("Constraint violation: synthetic datasets forbidden")
        return v
    
    # Contract layer: Composition validation
    @postcondition(lambda self: len(self.hypotheses) >= 1)
    @postcondition(lambda self: self.dataset_type in ["standard", "custom", "programmatic-api"])
    def validate_output(self):
        return self
```

**Output (Phase 2B Input):**
```python
class Phase2BInput(BaseModel):
    """Phase 2B: Verification Plan input schema"""
    hypotheses: List[dict]
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    
    # Precondition: Input must satisfy Phase 2A contract
    @precondition(lambda hypotheses: len(hypotheses) >= 1)
    @precondition(lambda dataset_type: dataset_type != "synthetic")
    def __init__(self, **data):
        super().__init__(**data)
```

### 3.4 Constraint Patterns

**C1: No Synthetic Data**
```python
# Schema: Cannot express (accepts any string)
dataset_type: str

# Pattern: Regex blacklist
@field_validator("dataset_type")
def no_synthetic(cls, v):
    if re.match(r"synthetic|simulated|generated", v, re.I):
        raise ValueError("Synthetic data forbidden")
    return v

# Contract: Semantic postcondition
@postcondition(lambda self: self.dataset_type in ALLOWED_TYPES)
```

**C2: No Human Evaluation**
```python
# Pattern: Keyword blacklist in evaluation_method
@field_validator("evaluation_method")
def no_human_eval(cls, v):
    forbidden = ["human", "manual", "annotator", "labeler"]
    if any(kw in v.lower() for kw in forbidden):
        raise ValueError("Human evaluation forbidden")
    return v
```

**C3: Real Standard Datasets Only**
```python
# Contract: Cross-field validation
@postcondition(lambda self: 
    (self.dataset_type == "standard" and self.dataset_name in STANDARD_DATASETS) or
    (self.dataset_type == "custom")
)
```

**C4: No New Benchmarks**
```python
# Contract: State-based validation
@precondition(lambda self, old: 
    self.benchmark_name in EXISTING_BENCHMARKS if hasattr(old, "benchmark_name") else True
)
```

---

## 4. Dataset Preparation

### 4.1 Adversarial Test Suite

**Test Case Structure:**
```python
@dataclass
class TestCase:
    id: str
    name: str
    violation_type: Literal["schema", "pattern", "contract"]
    constraint_violated: Literal["C1", "C2", "C3", "C4", "none"]
    phase2a_output: dict  # Violates constraint
    expected_detection: dict  # Which layers should catch it
```

**Test Case Distribution:**
- 5 valid cases (no violations)
- 5 schema violations (type errors, missing fields)
- 5 pattern violations (constraint keywords present)
- 5 contract violations (compositional failures)

**Example Cases:**

```python
# Case 1: Schema violation (missing required field)
{
    "id": "tc-01",
    "violation_type": "schema",
    "phase2a_output": {
        "research_question": "...",
        # Missing "detailed_question" field
        "hypotheses": [...]
    },
    "expected_detection": {
        "schema": True,
        "pattern": False,  # Never reached
        "contract": False
    }
}

# Case 2: Pattern violation (synthetic data keyword)
{
    "id": "tc-06",
    "violation_type": "pattern",
    "phase2a_output": {
        "research_question": "...",
        "detailed_question": "...",
        "dataset_type": "synthetic-generated",  # Violates C1
        "hypotheses": [...]
    },
    "expected_detection": {
        "schema": False,  # Type matches
        "pattern": True,  # Regex catches
        "contract": True   # Also caught here
    }
}

# Case 3: Contract violation (composition failure)
{
    "id": "tc-11",
    "violation_type": "contract",
    "phase2a_output": {
        "research_question": "...",
        "dataset_type": "standard",
        "dataset_name": "UnknownDataset123",  # Not in STANDARD_DATASETS
        "hypotheses": [...]
    },
    "expected_detection": {
        "schema": False,
        "pattern": False,  # No keywords
        "contract": True   # Cross-field check fails
    }
}
```

### 4.2 Ground Truth Labels

Each test case tagged with:
- `violation_type`: Which layer *should* catch it
- `constraint_violated`: Which of 4 constraints broken
- `expected_detection`: Boolean per layer

**Storage:** `tests/phase_boundary_validation/test_cases.yaml`

---

## 5. Baseline Experiments

### 5.1 Baseline A: Schema-Only Validation

**Implementation:**
```python
from pydantic import BaseModel, ValidationError

def validate_schema_only(output_dict: dict) -> bool:
    try:
        Phase2AOutput(**output_dict)
        return True  # Passed
    except ValidationError as e:
        return False  # Failed
```

**Expected Performance:**
- Detects: Type errors, missing fields (schema violations)
- Misses: Constraint keywords, compositional failures

### 5.2 Baseline B: Schema + Pattern Validation

**Implementation:**
```python
def validate_schema_pattern(output_dict: dict) -> bool:
    try:
        output = Phase2AOutputWithPatterns(**output_dict)
        return True
    except (ValidationError, ValueError) as e:
        return False
```

**Expected Performance:**
- Detects: Schema + keyword patterns (C1, C2)
- Misses: Cross-field constraints (C3, C4)

---

## 6. Proposed Experiment: Contract-Based Validation

### 6.1 Implementation

**Three-Layer Validator:**
```python
from contractme import precondition, postcondition, set_policy

set_policy("raise")  # Fail-fast on contract violation

class Phase2AOutputWithContracts(Phase2AOutputWithPatterns):
    """Adds contract layer to schema+pattern validation"""
    
    @postcondition(lambda self: len(self.hypotheses) >= 1)
    @postcondition(lambda self: self.dataset_type in ALLOWED_TYPES)
    @postcondition(lambda self: 
        (self.dataset_type == "standard" and 
         self.dataset_name in STANDARD_DATASETS) or
        self.dataset_type != "standard"
    )
    def validate_contracts(self):
        return self

def validate_full_contracts(output_dict: dict) -> bool:
    try:
        output = Phase2AOutputWithContracts(**output_dict)
        output.validate_contracts()
        return True
    except (ValidationError, ValueError, ContractViolationError) as e:
        return False
```

### 6.2 Evaluation Metrics

**Primary Metric:**
```
Detection Rate = (Detected Violations) / (Total Violations)

Improvement = (Contract_DR - SchemaOnly_DR) / SchemaOnly_DR × 100%
```

**Success Criterion:** Improvement ≥ 50%

**Secondary Metrics:**
- False Positive Rate (valid cases rejected)
- Layer-wise detection breakdown
- Execution time overhead

---

## 7. Experimental Procedure

### Step 01: Environment Setup
```bash
pip install pydantic==2.8.0 contractme==2.2.0 pytest
mkdir -p tests/phase_boundary_validation
```

### Step 02: Generate Test Suite
```python
# tests/phase_boundary_validation/generate_test_cases.py
def generate_adversarial_suite() -> List[TestCase]:
    cases = []
    
    # Valid cases
    cases.extend(generate_valid_cases(count=5))
    
    # Schema violations
    cases.extend(generate_schema_violations(count=5))
    
    # Pattern violations
    cases.extend(generate_pattern_violations(count=5))
    
    # Contract violations
    cases.extend(generate_contract_violations(count=5))
    
    return cases
```

### Step 03: Implement Validation Layers
```python
# src/validation/phase_2a_output.py
class Phase2AOutput(BaseModel): ...
class Phase2AOutputWithPatterns(Phase2AOutput): ...
class Phase2AOutputWithContracts(Phase2AOutputWithPatterns): ...
```

### Step 04: Run Baseline Experiments
```python
# tests/test_schema_only.py
@pytest.mark.parametrize("case", load_test_cases())
def test_schema_only_validation(case):
    result = validate_schema_only(case.phase2a_output)
    assert result == (case.violation_type != "schema")
```

### Step 05: Run Contract Validation
```python
# tests/test_contract_validation.py
@pytest.mark.parametrize("case", load_test_cases())
def test_contract_validation(case):
    result = validate_full_contracts(case.phase2a_output)
    assert result == (case.violation_type == "none")
```

### Step 06: Compute Metrics
```python
def compute_detection_rates(results: dict) -> dict:
    return {
        "schema_only": sum(r["schema"] for r in results) / len(results),
        "schema_pattern": sum(r["pattern"] for r in results) / len(results),
        "full_contract": sum(r["contract"] for r in results) / len(results),
    }
```

### Step 07: Analyze Results
- Compare detection rates across layers
- Identify which constraint types benefit most from contracts
- Measure false positive rate
- Profile execution overhead

### Step 08: Document Findings
Write to `04_validation.md`:
- Detection rate table
- Improvement percentage
- Layer-wise breakdown
- Example violations caught/missed

---

## 8. Expected Outcomes

### 8.1 Quantitative Results

**Predicted Detection Rates:**
| Approach | Detection Rate | Improvement |
|----------|---------------|-------------|
| Schema-Only | ~30% (6/20) | Baseline |
| Schema + Pattern | ~60% (12/20) | +100% |
| Full Contracts | ~95% (19/20) | +217% |

**Success:** >50% improvement = contract-based detects ≥9/20 violations (schema-only detects ≤6/20)

### 8.2 Qualitative Insights

**Questions Answered:**
1. Can contracts be specified for workflow phase boundaries? → YES (Layer 3 implemented)
2. Do contracts catch violations schema misses? → YES (compositional failures detected)
3. Is implementation feasible? → YES (contractme + Pydantic compose)

**Failure Modes:**
- Contract specification too complex (>50 LOC per boundary)
- Execution overhead >100ms per validation
- False positive rate >10%

---

## 9. Implementation Complexity

### 9.1 Effort Estimate

**Tier Assessment:** Tier 1 (Low Complexity)

**Breakdown:**
- Environment setup: 15 min
- Test case generation: 2 hours
- Schema layer: 1 hour
- Pattern layer: 2 hours
- Contract layer: 3 hours
- Baseline experiments: 1 hour
- Contract experiments: 1 hour
- Analysis: 2 hours

**Total:** ~12 hours (1.5 days)

### 9.2 File Structure

```
tests/phase_boundary_validation/
├── __init__.py
├── conftest.py
├── test_cases.yaml              # 20 adversarial cases
├── test_schema_only.py          # Baseline A
├── test_schema_pattern.py       # Baseline B
├── test_contract_validation.py  # Proposed
└── generate_test_cases.py

src/validation/
├── __init__.py
├── schemas.py                   # Layer 1: Pydantic schemas
├── patterns.py                  # Layer 2: Constraint patterns
├── contracts.py                 # Layer 3: Contract decorators
└── constants.py                 # STANDARD_DATASETS, ALLOWED_TYPES

experiments/
└── h_e1_contract_validation.py  # Experiment runner
```

---

## 10. Risk Mitigation

### Risk R3: Schema Enforcement Reliability

**Mitigation:**
- Use Pydantic v2.x strict mode
- Add explicit type coercion validators
- Test with malformed inputs

### Risk R1: Pattern Set Completeness

**Mitigation:**
- Start with 4 constraints only (not all possible violations)
- Use mutation testing to find gaps
- Document pattern coverage explicitly

### Risk R5: Validation Overhead

**Mitigation:**
- Profile each layer separately
- Optimize hot paths (cache compiled patterns)
- Measure overhead as secondary metric

---

## 11. Success Criteria Summary

**Primary (Gate: MUST_WORK):**
- Contract-based detection rate >50% better than schema-only
- All three layers execute without errors

**Secondary (Quality):**
- False positive rate <10%
- Execution overhead <100ms
- Contract specification <50 LOC per boundary

**Tertiary (Insight):**
- Identify which constraint types need contracts vs patterns
- Document reusable contract templates

**Failure Threshold:**
- Improvement <20% → ABORT (contracts don't help)
- Implementation >3 days → ABORT (too complex)

---

## 12. Next Steps

**Immediate (Phase 2C → Phase 3):**
1. Generate experiment brief → `02c_experiment_brief.md` ✓
2. Proceed to Phase 3: Implementation Planning
3. Create PRD, Architecture, PRP for h-e1
4. Initialize Archon tasks for implementation

**Post-Phase 4 (Validation):**
1. Run adversarial test suite
2. Compute detection rates
3. Write validation report → `04_validation.md`
4. Update hypothesis status based on gate criteria

---

## Appendix A: Reference Implementations

### A.1 Pydantic Validation Patterns

Source: Pydantic Docs - Validators (https://docs.pydantic.dev/latest/concepts/validators/)

```python
from pydantic import BaseModel, field_validator, model_validator

class Example(BaseModel):
    value: int
    
    # Field-level validator
    @field_validator("value")
    @classmethod
    def check_positive(cls, v):
        if v <= 0:
            raise ValueError("must be positive")
        return v
    
    # Model-level validator (cross-field)
    @model_validator(mode="after")
    def check_composition(self):
        # Access all fields
        if self.value > 100:
            raise ValueError("too large")
        return self
```

### A.2 Contractme Precondition/Postcondition

Source: contractme v2.2.0 (https://pypi.org/project/contractme/2.2.0/)

```python
from contractme import precondition, postcondition

@precondition(lambda x: x >= 0)
@postcondition(lambda x, result: result >= x)
def increment(x: int) -> int:
    return x + 1

# On methods: access self and old state
@postcondition(lambda self, old: self.balance == old.self.balance - amount)
def withdraw(self, amount):
    self.balance -= amount
```

### A.3 Workflow Validation Pattern

Source: Flowspec workflow-schema-validation.md (GitHub)

```python
import yaml
from jsonschema import validate, ValidationError

with open("workflow.yml") as f:
    config = yaml.safe_load(f)

try:
    validate(instance=config, schema=schema)
    print("✅ Valid")
except ValidationError as e:
    print(f"❌ {e.message}")
```

---

**Document Status:** COMPLETE  
**Experiment Tier:** 1 (Low Complexity)  
**Estimated Duration:** 1.5 days  
**Ready for Phase 3:** YES
