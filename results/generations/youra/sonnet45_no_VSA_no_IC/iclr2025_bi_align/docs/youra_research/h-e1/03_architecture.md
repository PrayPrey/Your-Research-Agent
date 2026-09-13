# Architecture: Contract-Based Phase Transition Validation

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-08-20  
**Phase:** 3 - Implementation Planning

---

## Applied Patterns

**Archon KB**: Pydantic validation patterns (field_validator, model_validator)

**Codebase Analysis (Serena):**
- **Project Type**: green-field
- **Status**: New implementation from scratch
- **Analyzed Path**: N/A
- **Findings**: No existing validation framework - creating minimal PoC structure

---

## 1. System Overview

Proof-of-concept three-layer validation framework for Phase 2A→2B boundary.

**Validation Flow:**
```
Test Case (dict)
  → Layer 1: Schema (Pydantic BaseModel - types, required fields)
    → Layer 2: Pattern (field_validator - keyword blacklist)
      → Layer 3: Contract (contractme - cross-field invariants)
        → Detection Result (bool + layer info)
```

**Components:**
- Validation schemas (3 classes stacked via inheritance)
- Test suite generator (20 adversarial cases)
- Validation executors (3 functions: schema/pattern/contract)
- Metrics calculator (detection rates, improvement %)

---

## 2. Module Interfaces

### 2.1 Schema Layer (`src/validation/schemas.py`)

**Dependencies**: Pydantic

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal

class Phase2AOutput(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    
    research_question: str = Field(min_length=10)
    detailed_question: str
    reference_papers: List[dict]
    hypotheses: List[dict] = Field(min_length=1)
    causal_mechanism: dict
    predictions: List[dict]
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str
    model_approach: str
    evaluation_method: str
```

### 2.2 Pattern Layer (`src/validation/patterns.py`)

**Dependencies**: schemas.py, constants.py

```python
from pydantic import field_validator
from .schemas import Phase2AOutput
import re

class Phase2AOutputWithPatterns(Phase2AOutput):
    @field_validator("dataset_type")
    @classmethod
    def no_synthetic_data(cls, v: str) -> str: ...
    
    @field_validator("evaluation_method")
    @classmethod
    def no_human_eval(cls, v: str) -> str: ...
```

### 2.3 Contract Layer (`src/validation/contracts.py`)

**Dependencies**: patterns.py, constants.py

```python
from contractme import postcondition
from .patterns import Phase2AOutputWithPatterns

class Phase2AOutputWithContracts(Phase2AOutputWithPatterns):
    @postcondition(lambda self: len(self.hypotheses) >= 1)
    @postcondition(lambda self: self.dataset_type in ALLOWED_TYPES)
    @postcondition(lambda self: 
        (self.dataset_type == "standard" and self.dataset_name in STANDARD_DATASETS) or
        self.dataset_type != "standard"
    )
    def validate_contracts(self) -> "Phase2AOutputWithContracts": ...
```

### 2.4 Constants (`src/validation/constants.py`)

**Dependencies**: None

```python
STANDARD_DATASETS: List[str] = ["MNIST", "CIFAR10", "ImageNet", "COCO"]
ALLOWED_TYPES: List[str] = ["standard", "custom", "programmatic-api"]
EXISTING_BENCHMARKS: List[str] = ["GLUE", "SuperGLUE", "SQuAD"]
```

### 2.5 Test Case Generator (`tests/phase_boundary_validation/generate_test_cases.py`)

**Dependencies**: constants.py

```python
from dataclasses import dataclass
from typing import List, Literal

@dataclass
class TestCase:
    id: str
    name: str
    violation_type: Literal["schema", "pattern", "contract", "none"]
    constraint_violated: Literal["C1", "C2", "C3", "C4", "none"]
    phase2a_output: dict
    expected_detection: dict

def generate_valid_cases(count: int) -> List[TestCase]: ...
def generate_schema_violations(count: int) -> List[TestCase]: ...
def generate_pattern_violations(count: int) -> List[TestCase]: ...
def generate_contract_violations(count: int) -> List[TestCase]: ...
def save_to_yaml(cases: List[TestCase], path: str) -> None: ...
```

### 2.6 Validation Executors (`src/validation/executors.py`)

**Dependencies**: schemas.py, patterns.py, contracts.py

```python
from pydantic import ValidationError
from contractme import ContractViolationError

def validate_schema_only(output_dict: dict) -> bool: ...
def validate_schema_pattern(output_dict: dict) -> bool: ...
def validate_full_contracts(output_dict: dict) -> bool: ...
def get_detection_layer(output_dict: dict) -> dict: ...
```

### 2.7 Metrics Calculator (`experiments/h_e1_contract_validation.py`)

**Dependencies**: executors.py, test_cases.yaml

```python
from typing import List, Dict

def load_test_cases(yaml_path: str) -> List[TestCase]: ...
def run_validation_suite(cases: List[TestCase]) -> Dict[str, List[bool]]: ...
def compute_detection_rates(results: Dict) -> Dict[str, float]: ...
def compute_improvement(schema_dr: float, contract_dr: float) -> float: ...
def measure_execution_time(validator: callable, cases: List[TestCase]) -> float: ...
def write_results(metrics: dict, output_path: str) -> None: ...
```

---

## 3. File Structure

```
src/validation/
├── __init__.py                 # Export all validators
├── schemas.py                  # Layer 1: BaseModel (40 LOC)
├── patterns.py                 # Layer 2: field_validator (30 LOC)
├── contracts.py                # Layer 3: contractme (25 LOC)
├── constants.py                # Datasets/types (10 LOC)
└── executors.py                # Validation functions (40 LOC)

tests/phase_boundary_validation/
├── __init__.py
├── conftest.py                 # Pytest fixtures (20 LOC)
├── test_cases.yaml             # 20 test cases (150 LOC)
├── generate_test_cases.py     # Case generator (120 LOC)
├── test_schema_only.py        # Baseline A (30 LOC)
├── test_schema_pattern.py     # Baseline B (30 LOC)
└── test_contract_validation.py # Proposed (30 LOC)

experiments/
└── h_e1_contract_validation.py # Metrics runner (80 LOC)

docs/youra_research/h-e1/
└── 04_validation.md            # Results report
```

**Total LOC Estimate:** ~600 LOC

---

## 4. Data Flow

### 4.1 Test Case Generation

```
Constants (STANDARD_DATASETS, ALLOWED_TYPES)
  → generate_valid_cases() → 5 valid cases
  → generate_schema_violations() → 5 schema-broken cases
  → generate_pattern_violations() → 5 keyword-violating cases
  → generate_contract_violations() → 5 cross-field-broken cases
    → save_to_yaml(test_cases.yaml)
```

### 4.2 Validation Execution

```
load_test_cases(test_cases.yaml)
  → For each case:
      → validate_schema_only(case.phase2a_output)
        → Try: Phase2AOutput(**dict) → True if valid, False if ValidationError
      → validate_schema_pattern(case.phase2a_output)
        → Try: Phase2AOutputWithPatterns(**dict) → True if valid, False if error
      → validate_full_contracts(case.phase2a_output)
        → Try: Phase2AOutputWithContracts(**dict).validate_contracts() → True/False
    → Collect results: {schema: [bool], pattern: [bool], contract: [bool]}
```

### 4.3 Metrics Computation

```
results: {schema: [20 bools], pattern: [20 bools], contract: [20 bools]}
  → compute_detection_rates()
    → schema_dr = sum(results["schema"]) / 20
    → pattern_dr = sum(results["pattern"]) / 20
    → contract_dr = sum(results["contract"]) / 20
  → compute_improvement(schema_dr, contract_dr)
    → improvement = (contract_dr - schema_dr) / schema_dr * 100
  → measure_execution_time() → overhead_ms
  → write_results(04_validation.md)
```

---

## 5. Integration Points

### 5.1 Pydantic v2.x

**Usage:**
- `BaseModel` with strict mode (`ConfigDict(strict=True)`)
- `Field()` descriptors for constraints (`min_length=10`, `min_items=1`)
- `@field_validator` for pattern matching
- `@model_validator(mode="after")` for cross-field checks (not used - contractme replaces)

**Configuration:**
```python
model_config = ConfigDict(
    strict=True,        # Strict type checking
    extra='forbid',     # Reject unknown fields
    validate_assignment=True  # Re-validate on field updates
)
```

### 5.2 contractme v2.2.0

**Usage:**
- `@precondition(lambda params: predicate)` for input validation
- `@postcondition(lambda self: predicate)` for output validation
- `set_policy("raise")` to throw exceptions on violations

**Contract Style:**
```python
@postcondition(lambda self: len(self.hypotheses) >= 1)
@postcondition(lambda self: 
    (self.dataset_type == "standard" and self.dataset_name in STANDARD_DATASETS) or
    self.dataset_type != "standard"
)
def validate_contracts(self):
    return self
```

### 5.3 Pytest

**Test Parameterization:**
```python
@pytest.fixture
def test_cases():
    return load_yaml("test_cases.yaml")

@pytest.mark.parametrize("case", test_cases())
def test_schema_only_validation(case):
    result = validate_schema_only(case.phase2a_output)
    expected = (case.violation_type != "schema")
    assert result == expected
```

---

## 6. Technology Stack

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| Schema | Pydantic | 2.8.0 | Industry standard for data validation, strict type checking |
| Pattern | Pydantic field_validator | 2.8.0 | Integrated with schema layer, regex support |
| Contract | contractme | 2.2.0 | Lightweight design-by-contract library, decorator-based |
| Testing | pytest | >=7.0 | Parametrized tests, fixtures |
| Data | PyYAML | >=6.0 | Test case storage |

**Why contractme over alternatives:**
- `icontract`: Heavier (runtime overhead), more complex
- `dpcontracts`: Unmaintained (last update 2016)
- `deal`: Feature-heavy (formal verification), overkill for PoC
- `contractme`: Minimal API, decorator-only, sufficient for existence proof

**Why not Pydantic model_validator for contracts:**
- Cannot access old state (`old.self`)
- No explicit precondition/postcondition semantics
- Less clear separation of concerns (pattern vs contract)

---

## 7. Constraint Mapping

| Constraint | Layer | Implementation | Example Violation |
|-----------|-------|----------------|------------------|
| C1: No synthetic data | Pattern | Regex blacklist (`synthetic|simulated|generated`) | `dataset_type="synthetic-generated"` |
| C2: No human eval | Pattern | Keyword blacklist (`["human", "manual", "annotator"]`) | `evaluation_method="human labeling"` |
| C3: Standard dataset membership | Contract | Cross-field check (`dataset_type=="standard" → dataset_name in STANDARD_DATASETS`) | `dataset_type="standard", dataset_name="UnknownDataset"` |
| C4: No new benchmarks | Contract | State-based check (`benchmark_name in EXISTING_BENCHMARKS`) | `benchmark_name="NewBenchmark2026"` |

**Layer Selection Rationale:**
- **Schema**: Structural violations (type errors, missing fields)
- **Pattern**: Keyword-based violations (detectable via regex/string matching)
- **Contract**: Compositional violations (relationships between fields, state invariants)

---

## 8. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Setup environment | Install deps, create folders | 4 | 1(pip)+1(mkdir)+2(verify) |
| E2 | Implement schema layer | Phase2AOutput BaseModel | 6 | 2(fields)+2(config)+2(test) |
| E3 | Implement pattern layer | field_validator for C1/C2 | 8 | 3(C1)+3(C2)+2(test) |
| E4 | Implement contract layer | contractme decorators for C3/C4 | 10 | 4(C3)+4(C4)+2(test) |
| E5 | Generate test suite | 20 adversarial cases in YAML | 12 | 3(valid)+3(schema)+3(pattern)+3(contract) |
| E6 | Implement executors | 3 validation functions | 6 | 2(schema)+2(pattern)+2(contract) |
| E7 | Run experiments | Execute baselines + proposed | 5 | 2(baseline)+2(contract)+1(collect) |
| E8 | Compute metrics | Detection rates, improvement | 4 | 2(rates)+1(improvement)+1(overhead) |

**Complexity Scoring:** Module_Size(1-5) + Dependencies(1-5) + Algorithm(1-5) + Integration(1-5)

**Distribution:**
- VeryHigh(18-20): []
- High(14-17): []
- Medium(9-13): [E4, E5]
- Low(4-8): [E1, E2, E3, E6, E7, E8]

**Total Estimated Complexity:** 55 points (~12 hours at 5 points/hour)

---

## 9. Example Test Cases

### 9.1 Valid Case (tc-01)

```yaml
id: tc-01
name: "Valid Phase 2A output"
violation_type: none
constraint_violated: none
phase2a_output:
  research_question: "Can contracts detect violations?"
  detailed_question: "Testing three-layer validation"
  reference_papers: [{title: "Paper1", year: 2024}]
  hypotheses: [{id: "h1", statement: "Contracts work"}]
  causal_mechanism: {cause: "X", effect: "Y"}
  predictions: [{metric: "accuracy", value: 0.9}]
  dataset_type: "standard"
  dataset_name: "MNIST"
  model_approach: "transformer"
  evaluation_method: "automated metrics"
expected_detection:
  schema: true
  pattern: true
  contract: true
```

### 9.2 Pattern Violation (tc-06)

```yaml
id: tc-06
name: "Synthetic data keyword"
violation_type: pattern
constraint_violated: C1
phase2a_output:
  research_question: "Testing C1 violation"
  detailed_question: "Synthetic data should be caught"
  reference_papers: [{title: "Paper1"}]
  hypotheses: [{id: "h1"}]
  causal_mechanism: {}
  predictions: []
  dataset_type: "synthetic-generated"  # VIOLATION
  dataset_name: "GeneratedData"
  model_approach: "baseline"
  evaluation_method: "automated"
expected_detection:
  schema: true   # Type matches Literal["standard", "custom", "programmatic-api"] - WAIT NO
  pattern: false # field_validator catches regex
  contract: false
```

**Note:** Need to fix `dataset_type` Literal to allow any string for pattern to catch.

### 9.3 Contract Violation (tc-11)

```yaml
id: tc-11
name: "Unknown standard dataset"
violation_type: contract
constraint_violated: C3
phase2a_output:
  research_question: "Testing C3 violation"
  detailed_question: "Cross-field check"
  reference_papers: [{title: "Paper1"}]
  hypotheses: [{id: "h1"}]
  causal_mechanism: {}
  predictions: []
  dataset_type: "standard"
  dataset_name: "UnknownDataset123"  # NOT in STANDARD_DATASETS
  model_approach: "baseline"
  evaluation_method: "automated"
expected_detection:
  schema: true
  pattern: true
  contract: false  # Cross-field postcondition fails
```

---

## 10. Design Decisions

**Schema Type Change:**
- PRD specified `dataset_type: Literal["standard", "custom", "programmatic-api"]`
- Architecture change to `dataset_type: str` for pattern layer to catch violations
- **Reason**: Literal would reject invalid values at schema layer, preventing pattern layer test

**Contract Method Pattern:**
- Contracts attached to `validate_contracts()` method, not `__init__`
- **Reason**: Cleaner separation, explicit validation call, easier debugging

**Test Case Storage:**
- YAML format instead of Python dataclasses
- **Reason**: Easier manual inspection, no code execution risk, language-agnostic

---

## Status

**Architecture Completeness:** MINIMAL (EXISTENCE PoC)

**Next Phase:** Phase 4 - Coding (Epic tasks E1-E8)

**Estimated Duration:** 12 hours (1.5 days)

**File Structure Paths:**
- Schema layer: `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_bi_align/src/validation/schemas.py`
- Test suite: `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_bi_align/tests/phase_boundary_validation/test_cases.yaml`
- Results: `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_bi_align/docs/youra_research/h-e1/04_validation.md`
