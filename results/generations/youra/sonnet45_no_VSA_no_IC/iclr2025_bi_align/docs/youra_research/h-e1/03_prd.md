# Product Requirements Document: Contract-Based Phase Transition Validation

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-08-20  
**Phase:** 3 - Implementation Planning  
**Tier:** 1 (Low Complexity)

---

## 1. Executive Summary

### 1.1 Objective

Build proof-of-concept three-layer validation framework (schema + pattern + contract) for research pipeline phase boundaries and validate that contract-based validation detects >50% more constraint violations than schema-only validation.

### 1.2 Scope

**In Scope:**
- Validation framework for Phase 2A→2B boundary
- Three validation layers: schema (Pydantic), pattern (regex/predicates), contract (contractme)
- 20-case adversarial test suite with known violations
- Baseline (schema-only) and proposed (full contract) experiments
- Detection rate measurement and comparison

**Out of Scope:**
- Validation for other phase boundaries (Phase 0→1, Phase 3→4)
- Production deployment infrastructure
- Real-world violation datasets
- Performance optimization beyond profiling

### 1.3 Success Criteria

**Primary:**
- Contract-based detection rate improvement ≥50% over schema-only
- All three layers execute without errors

**Secondary:**
- False positive rate <10%
- Execution overhead <100ms
- Contract specification <50 LOC per boundary

**Failure Threshold:**
- Improvement <20% → ABORT

---

## 2. Product Requirements

### 2.1 Functional Requirements

**FR-01: Schema Layer**
- Implement Pydantic BaseModel for Phase2AOutput
- Type checking for all fields
- Required field validation
- Field type coercion

**FR-02: Pattern Layer**
- Implement field_validator decorators
- Constraint C1: Detect "synthetic" keyword in dataset_type
- Constraint C2: Detect ["human", "manual", "annotator"] in evaluation_method
- Pattern matching via regex + custom predicates

**FR-03: Contract Layer**
- Implement contractme preconditions/postconditions
- Constraint C3: Cross-field validation (dataset_type + dataset_name)
- Constraint C4: State-based validation (benchmark_name in EXISTING_BENCHMARKS)
- Compositional invariants (hypotheses count ≥1)

**FR-04: Test Suite**
- Generate 20 adversarial test cases:
  - 5 valid (no violations)
  - 5 schema violations
  - 5 pattern violations
  - 5 contract violations
- Ground truth labels per case
- YAML storage format

**FR-05: Validation Executors**
- `validate_schema_only(dict) -> bool`
- `validate_schema_pattern(dict) -> bool`
- `validate_full_contracts(dict) -> bool`
- Exception handling for ValidationError, ContractViolationError

**FR-06: Metrics Computation**
- Detection rate per layer
- Improvement percentage calculation
- False positive rate
- Execution time profiling

**FR-07: Results Documentation**
- Detection rate table (schema-only vs contract)
- Layer-wise breakdown
- Example violations caught/missed
- Execution overhead measurements

### 2.2 Non-Functional Requirements

**NFR-01: Performance**
- Validation execution <100ms per test case
- Test suite runs in <5 seconds total

**NFR-02: Maintainability**
- Contract specifications <50 LOC per boundary
- Clear separation between layers
- Reusable validation patterns

**NFR-03: Testability**
- Pytest-compatible test structure
- Parametrized tests for all cases
- Ground truth assertions

**NFR-04: Reliability**
- Pydantic strict mode enabled
- Explicit type coercion validators
- Comprehensive error messages

---

## 3. Technical Specifications

### 3.1 Technology Stack

**Core Libraries:**
- Python ≥3.11
- Pydantic v2.8.0 (schema + pattern validation)
- contractme v2.2.0 (contract validation)
- pytest ≥7.0 (test framework)
- PyYAML ≥6.0 (test case loading)

**Development Tools:**
- pytest-benchmark (profiling)
- mypy (type checking)
- ruff (linting)

### 3.2 Data Models

**Phase2AOutput Schema:**
```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal

class Phase2AOutput(BaseModel):
    research_question: str = Field(min_length=10)
    detailed_question: str
    reference_papers: List[dict]
    hypotheses: List[dict]
    causal_mechanism: dict
    predictions: List[dict]
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str
    model_approach: str
    evaluation_method: str
```

**Test Case Schema:**
```python
@dataclass
class TestCase:
    id: str
    name: str
    violation_type: Literal["schema", "pattern", "contract", "none"]
    constraint_violated: Literal["C1", "C2", "C3", "C4", "none"]
    phase2a_output: dict
    expected_detection: dict  # {schema: bool, pattern: bool, contract: bool}
```

### 3.3 File Structure

```
tests/phase_boundary_validation/
├── __init__.py
├── conftest.py                      # Pytest configuration
├── test_cases.yaml                  # 20 adversarial cases
├── test_schema_only.py              # Baseline A
├── test_schema_pattern.py           # Baseline B
├── test_contract_validation.py      # Proposed
└── generate_test_cases.py           # Test case generator

src/validation/
├── __init__.py
├── schemas.py                       # Layer 1: Pydantic BaseModel
├── patterns.py                      # Layer 2: field_validator
├── contracts.py                     # Layer 3: contractme decorators
└── constants.py                     # STANDARD_DATASETS, ALLOWED_TYPES

experiments/
└── h_e1_contract_validation.py      # Experiment runner

docs/youra_research/h-e1/
└── 04_validation.md                 # Results report
```

### 3.4 Validation Layers

**Layer 1: Schema (Pydantic BaseModel)**
```python
class Phase2AOutput(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    
    research_question: str = Field(min_length=10)
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    hypotheses: List[dict] = Field(min_length=1)
```

**Layer 2: Pattern (field_validator)**
```python
class Phase2AOutputWithPatterns(Phase2AOutput):
    @field_validator("dataset_type")
    @classmethod
    def no_synthetic_data(cls, v):
        if re.match(r"synthetic|simulated|generated", v, re.I):
            raise ValueError("C1 violation: synthetic data forbidden")
        return v
    
    @field_validator("evaluation_method")
    @classmethod
    def no_human_eval(cls, v):
        forbidden = ["human", "manual", "annotator", "labeler"]
        if any(kw in v.lower() for kw in forbidden):
            raise ValueError("C2 violation: human evaluation forbidden")
        return v
```

**Layer 3: Contract (contractme)**
```python
from contractme import postcondition, set_policy

set_policy("raise")

class Phase2AOutputWithContracts(Phase2AOutputWithPatterns):
    @postcondition(lambda self: len(self.hypotheses) >= 1)
    @postcondition(lambda self: self.dataset_type in ALLOWED_TYPES)
    @postcondition(lambda self: 
        (self.dataset_type == "standard" and 
         self.dataset_name in STANDARD_DATASETS) or
        self.dataset_type != "standard"
    )
    def validate_contracts(self):
        return self
```

### 3.5 Test Case Examples

**Valid Case:**
```yaml
- id: tc-01
  name: "Valid Phase 2A output"
  violation_type: none
  constraint_violated: none
  phase2a_output:
    research_question: "Can contracts detect violations?"
    detailed_question: "..."
    dataset_type: "standard"
    dataset_name: "MNIST"
    evaluation_method: "automated metrics"
    hypotheses: [{id: "h1", statement: "..."}]
  expected_detection:
    schema: true
    pattern: true
    contract: true
```

**Pattern Violation (C1):**
```yaml
- id: tc-06
  name: "Synthetic data keyword"
  violation_type: pattern
  constraint_violated: C1
  phase2a_output:
    dataset_type: "synthetic-generated"
    # ... other fields valid
  expected_detection:
    schema: true   # Type matches Literal
    pattern: false # Regex catches keyword
    contract: false
```

**Contract Violation (C3):**
```yaml
- id: tc-11
  name: "Unknown standard dataset"
  violation_type: contract
  constraint_violated: C3
  phase2a_output:
    dataset_type: "standard"
    dataset_name: "UnknownDataset123"
    # ... other fields valid
  expected_detection:
    schema: true
    pattern: true
    contract: false  # Cross-field check fails
```

### 3.6 Experiment Procedure

**Step 1: Environment Setup**
```bash
pip install pydantic==2.8.0 contractme==2.2.0 pytest pyyaml pytest-benchmark
mkdir -p tests/phase_boundary_validation src/validation experiments
```

**Step 2: Generate Test Suite**
```python
# tests/phase_boundary_validation/generate_test_cases.py
def generate_adversarial_suite() -> List[TestCase]:
    cases = []
    cases.extend(generate_valid_cases(count=5))
    cases.extend(generate_schema_violations(count=5))
    cases.extend(generate_pattern_violations(count=5))
    cases.extend(generate_contract_violations(count=5))
    return cases

# Output to test_cases.yaml
```

**Step 3: Run Experiments**
```bash
# Baseline A: Schema-only
pytest tests/phase_boundary_validation/test_schema_only.py -v

# Baseline B: Schema + Pattern
pytest tests/phase_boundary_validation/test_schema_pattern.py -v

# Proposed: Full Contracts
pytest tests/phase_boundary_validation/test_contract_validation.py -v
```

**Step 4: Compute Metrics**
```python
def compute_metrics(results: dict) -> dict:
    return {
        "detection_rates": {
            "schema_only": sum(r["schema"] for r in results) / len(results),
            "schema_pattern": sum(r["pattern"] for r in results) / len(results),
            "full_contract": sum(r["contract"] for r in results) / len(results),
        },
        "improvement": (
            (full_contract - schema_only) / schema_only * 100
        ),
        "false_positive_rate": count_false_positives(results) / count_valid(results),
    }
```

**Step 5: Document Results**
Write to `04_validation.md`:
- Detection rate table
- Improvement percentage
- Layer-wise breakdown
- Example violations

---

## 4. Deliverables

**Code Artifacts:**
1. `src/validation/schemas.py` - Pydantic BaseModel definitions
2. `src/validation/patterns.py` - field_validator patterns
3. `src/validation/contracts.py` - contractme decorators
4. `src/validation/constants.py` - STANDARD_DATASETS, ALLOWED_TYPES
5. `tests/phase_boundary_validation/test_cases.yaml` - 20 test cases
6. `tests/phase_boundary_validation/test_*.py` - 3 test suites
7. `experiments/h_e1_contract_validation.py` - Experiment runner

**Documentation:**
1. `04_validation.md` - Experiment results and analysis

**Metrics:**
1. Detection rates (schema-only, schema+pattern, full contract)
2. Improvement percentage
3. False positive rate
4. Execution overhead (milliseconds)
5. Contract LOC

---

## 5. Risks and Mitigation

**R1: Pattern Set Completeness**
- Risk: Patterns may not cover all constraint violations
- Mitigation: Start with 4 constraints only, use mutation testing
- Detection: Track validation pass rate vs ground-truth

**R3: Schema Enforcement Reliability**
- Risk: Pydantic may not strictly enforce types
- Mitigation: Use strict mode + explicit validators
- Detection: Test with malformed inputs

**R5: Validation Overhead**
- Risk: Contract validation too slow
- Mitigation: Profile each layer, cache compiled patterns
- Detection: Measure overhead as secondary metric

---

## 6. Acceptance Criteria

**Code Quality:**
- [ ] All validation layers execute without runtime errors
- [ ] Test suite passes with 100% expected outcomes
- [ ] Type checking passes (mypy --strict)
- [ ] Linting passes (ruff)

**Functional:**
- [ ] Schema layer detects type/missing field errors
- [ ] Pattern layer detects C1, C2 keyword violations
- [ ] Contract layer detects C3, C4 compositional failures
- [ ] 20 test cases execute with expected detection outcomes

**Performance:**
- [ ] Detection rate improvement ≥50%
- [ ] False positive rate <10%
- [ ] Execution overhead <100ms per case
- [ ] Contract specification <50 LOC

**Documentation:**
- [ ] 04_validation.md contains detection rate table
- [ ] Layer-wise breakdown documented
- [ ] Example violations with explanations
- [ ] Failure threshold evaluation

---

## 7. Timeline Estimate

**Total Duration:** 1.5 days (12 hours)

| Task | Duration |
|------|----------|
| Environment setup | 15 min |
| Test case generation | 2 hours |
| Schema layer implementation | 1 hour |
| Pattern layer implementation | 2 hours |
| Contract layer implementation | 3 hours |
| Baseline experiments | 1 hour |
| Contract experiments | 1 hour |
| Metrics computation | 1 hour |
| Documentation | 1 hour |

---

## 8. Dependencies

**External Libraries:**
- pydantic==2.8.0
- contractme==2.2.0
- pytest>=7.0
- pyyaml>=6.0

**Internal:**
- None (standalone PoC)

**Data:**
- STANDARD_DATASETS constant (predefined list)
- EXISTING_BENCHMARKS constant (predefined list)

---

## 9. Future Considerations

**If Hypothesis Passes:**
- Extend to other phase boundaries (Phase 0→1, Phase 3→4)
- Add contract templates for common patterns
- Integrate into pipeline harness

**If Hypothesis Fails:**
- Document which violation types contracts cannot catch
- Explore alternative validation approaches (property-based testing)
- Analyze failure modes (edge cases, overhead)

---

**Status:** DRAFT  
**Version:** 1.0  
**Next Phase:** Architecture Design (03_architecture.md)
