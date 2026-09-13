# Logic Specification: Contract-Based Phase Transition Validation

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-08-20  
**Phase:** 3 - Implementation Planning

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New API design - no existing validation code  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## Applied Patterns

**Applied:** Standard Pydantic validation + contractme decorator pattern

---

## API Signatures

### Layer 1: Schema Validation

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Dict

class Phase2AOutput(BaseModel):
    """Schema-only validation layer."""
    model_config = ConfigDict(strict=True, extra='forbid')
    
    research_question: str = Field(min_length=10)
    detailed_question: str
    reference_papers: List[Dict]
    hypotheses: List[Dict] = Field(min_length=1)
    causal_mechanism: Dict
    predictions: List[Dict]
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str
    model_approach: str
    evaluation_method: str
```

### Layer 2: Pattern Validation

```python
from pydantic import field_validator
import re

class Phase2AOutputWithPatterns(Phase2AOutput):
    """Schema + pattern validation layer."""
    
    @field_validator("dataset_type")
    @classmethod
    def validate_no_synthetic(cls, v: str) -> str:
        """C1: No synthetic data. Raises ValueError if pattern matches."""
        if re.search(r"synthetic|simulated|generated", v, re.IGNORECASE):
            raise ValueError("C1 violation: synthetic data forbidden")
        return v
    
    @field_validator("evaluation_method")
    @classmethod
    def validate_no_human_eval(cls, v: str) -> str:
        """C2: No human evaluation. Raises ValueError if keywords found."""
        forbidden = ["human", "manual", "annotator", "labeler"]
        if any(kw in v.lower() for kw in forbidden):
            raise ValueError("C2 violation: human evaluation forbidden")
        return v
```

### Layer 3: Contract Validation

```python
from contractme import postcondition, set_policy

STANDARD_DATASETS = ["MNIST", "CIFAR10", "ImageNet", "COCO", "SQuAD"]
EXISTING_BENCHMARKS = ["SuperGLUE", "GLUE", "ImageNet1K"]

set_policy("raise")

class Phase2AOutputWithContracts(Phase2AOutputWithPatterns):
    """Full contract validation layer."""
    
    @postcondition(lambda self: len(self.hypotheses) >= 1)
    @postcondition(lambda self: 
        self.dataset_type != "standard" or 
        self.dataset_name in STANDARD_DATASETS
    )
    def __init__(self, **data):
        """C3: Real standard datasets only. C4: No new benchmarks."""
        super().__init__(**data)
        self._validate_no_new_benchmarks()
    
    def _validate_no_new_benchmarks(self) -> None:
        """C4: Benchmark name must be in existing list."""
        if "benchmark" in self.evaluation_method.lower():
            benchmark_mentioned = any(
                b.lower() in self.evaluation_method.lower() 
                for b in EXISTING_BENCHMARKS
            )
            if not benchmark_mentioned:
                raise ValueError("C4 violation: new benchmark not allowed")
```

### Validation Executors

```python
from typing import Dict, Tuple
from pydantic import ValidationError

def validate_schema_only(data: Dict) -> Tuple[bool, str]:
    """
    Baseline A: Schema-only validation.
    Returns: (is_valid, error_message)
    """
    try:
        Phase2AOutput(**data)
        return (True, "")
    except ValidationError as e:
        return (False, str(e))

def validate_schema_pattern(data: Dict) -> Tuple[bool, str]:
    """
    Baseline B: Schema + pattern validation.
    Returns: (is_valid, error_message)
    """
    try:
        Phase2AOutputWithPatterns(**data)
        return (True, "")
    except ValidationError as e:
        return (False, str(e))

def validate_full_contracts(data: Dict) -> Tuple[bool, str]:
    """
    Proposed: Full contract validation.
    Returns: (is_valid, error_message)
    """
    try:
        Phase2AOutputWithContracts(**data)
        return (True, "")
    except (ValidationError, ValueError) as e:
        return (False, str(e))
```

---

## Constraint Patterns

### C1: No Synthetic Data

**Pattern:** Keyword match in `dataset_type`  
**Keywords:** ["synthetic", "simulated", "generated"]  
**Validation:** Regex `r"synthetic|simulated|generated"` with IGNORECASE

```python
# Pseudo-code
if re.search(pattern, dataset_type, re.I):
    raise ValueError("C1 violation")
```

### C2: No Human Evaluation

**Pattern:** Keyword match in `evaluation_method`  
**Keywords:** ["human", "manual", "annotator", "labeler"]  
**Validation:** Substring check (case-insensitive)

```python
# Pseudo-code
forbidden = ["human", "manual", "annotator", "labeler"]
if any(kw in eval_method.lower() for kw in forbidden):
    raise ValueError("C2 violation")
```

### C3: Real Standard Datasets Only

**Pattern:** Cross-field constraint  
**Fields:** `dataset_type`, `dataset_name`  
**Validation:** If type="standard" → name must be in STANDARD_DATASETS

```python
# Pseudo-code
if dataset_type == "standard":
    if dataset_name not in STANDARD_DATASETS:
        raise ValueError("C3 violation")
```

### C4: No New Benchmarks

**Pattern:** State-based constraint  
**Field:** `evaluation_method`  
**Validation:** If "benchmark" keyword → must mention existing benchmark

```python
# Pseudo-code
if "benchmark" in evaluation_method.lower():
    if not any(b in evaluation_method.lower() for b in EXISTING_BENCHMARKS):
        raise ValueError("C4 violation")
```

---

## Test Case Generation

### Generator API

```python
from dataclasses import dataclass
from typing import Literal, Dict

@dataclass
class TestCase:
    """Test case structure."""
    id: str
    name: str
    violation_type: Literal["schema", "pattern", "contract", "none"]
    constraint_violated: Literal["C1", "C2", "C3", "C4", "none"]
    phase2a_output: Dict
    expected_detection: Dict[str, bool]

def generate_adversarial_suite() -> List[TestCase]:
    """
    Generate 20 test cases with known violations.
    Returns: 5 valid + 5 schema + 5 pattern + 5 contract
    """
    cases = []
    cases.extend(generate_valid_cases(count=5))
    cases.extend(generate_schema_violations(count=5))
    cases.extend(generate_pattern_violations(count=5))
    cases.extend(generate_contract_violations(count=5))
    return cases
```

### Generation Logic

```python
def generate_valid_cases(count: int) -> List[TestCase]:
    """Valid cases: all fields conform."""
    template = {
        "research_question": "Can contracts detect violations?",
        "detailed_question": "Detailed version...",
        "reference_papers": [{"title": "Paper1"}],
        "hypotheses": [{"id": "h1", "statement": "..."}],
        "causal_mechanism": {"type": "intervention"},
        "predictions": [{"metric": "accuracy"}],
        "dataset_type": "standard",
        "dataset_name": "MNIST",
        "model_approach": "neural network",
        "evaluation_method": "automated metrics"
    }
    # Mutate template with valid variations

def generate_schema_violations(count: int) -> List[TestCase]:
    """Schema violations: type errors, missing fields."""
    # Missing required field
    # Wrong type (int instead of str)
    # hypotheses = [] (violates min_length=1)
    # dataset_type = "invalid_literal"

def generate_pattern_violations(count: int) -> List[TestCase]:
    """Pattern violations: C1, C2 keyword matches."""
    # dataset_type = "synthetic-generated"  # C1
    # evaluation_method = "human annotators"  # C2

def generate_contract_violations(count: int) -> List[TestCase]:
    """Contract violations: C3, C4 compositional failures."""
    # dataset_type="standard", dataset_name="UnknownDataset"  # C3
    # evaluation_method="new benchmark XYZ"  # C4
```

---

## Metrics Computation

### Detection Rate

```python
def compute_detection_rate(results: List[Tuple[bool, str]]) -> float:
    """
    Detection rate = (violations detected) / (total violations)
    Input: results from validation executor
    Returns: rate in [0, 1]
    """
    detected = sum(1 for is_valid, _ in results if not is_valid)
    total = len(results)
    return detected / total if total > 0 else 0.0
```

### Improvement Percentage

```python
def compute_improvement(contract_rate: float, schema_rate: float) -> float:
    """
    Improvement = (contract_rate - schema_rate) / schema_rate * 100
    Returns: percentage improvement
    """
    if schema_rate == 0:
        return 0.0
    return ((contract_rate - schema_rate) / schema_rate) * 100
```

### False Positive Rate

```python
def compute_false_positive_rate(
    results: List[Tuple[bool, str]], 
    ground_truth: List[bool]
) -> float:
    """
    FPR = false_positives / total_valid_cases
    False positive = validation fails but case is valid
    """
    false_positives = sum(
        1 for (is_valid, _), is_actually_valid in zip(results, ground_truth)
        if not is_valid and is_actually_valid
    )
    total_valid = sum(ground_truth)
    return false_positives / total_valid if total_valid > 0 else 0.0
```

### Execution Overhead

```python
import time

def measure_overhead(
    validator_func, 
    data: Dict, 
    iterations: int = 100
) -> float:
    """
    Measure average execution time.
    Returns: milliseconds per validation
    """
    start = time.perf_counter()
    for _ in range(iterations):
        validator_func(data)
    end = time.perf_counter()
    return ((end - start) / iterations) * 1000  # ms
```

---

## Data Structures

### Test Case YAML Schema

```yaml
test_cases:
  - id: tc-01
    name: "Valid Phase 2A output"
    violation_type: none
    constraint_violated: none
    phase2a_output:
      research_question: "Can contracts detect violations?"
      detailed_question: "..."
      reference_papers: [{title: "Paper1"}]
      hypotheses: [{id: "h1", statement: "..."}]
      causal_mechanism: {type: "intervention"}
      predictions: [{metric: "accuracy"}]
      dataset_type: "standard"
      dataset_name: "MNIST"
      model_approach: "neural network"
      evaluation_method: "automated metrics"
    expected_detection:
      schema: true
      pattern: true
      contract: true
```

### Results Schema

```python
@dataclass
class ValidationResults:
    """Results from validation experiment."""
    test_case_id: str
    schema_only: bool
    schema_pattern: bool
    full_contract: bool
    expected_schema: bool
    expected_pattern: bool
    expected_contract: bool
    execution_time_ms: float

@dataclass
class ExperimentMetrics:
    """Aggregated metrics."""
    detection_rates: Dict[str, float]  # {schema_only, schema_pattern, full_contract}
    improvement_percentage: float
    false_positive_rate: float
    avg_execution_time_ms: Dict[str, float]
    layer_breakdown: Dict[str, int]  # {schema: 5, pattern: 5, contract: 5}
```

---

## Experiment Execution Flow

```
1. Load test_cases.yaml → List[TestCase]

2. For each test case:
   a. Run validate_schema_only(case.phase2a_output) → (bool, str)
   b. Run validate_schema_pattern(case.phase2a_output) → (bool, str)
   c. Run validate_full_contracts(case.phase2a_output) → (bool, str)
   d. Measure execution time for each
   e. Store ValidationResults

3. Aggregate results:
   a. Compute detection rates per layer
   b. Compute improvement percentage
   c. Compute false positive rate
   d. Compute average execution times

4. Evaluate success criteria:
   a. improvement >= 50% → PASS
   b. improvement < 20% → ABORT
   c. false_positive_rate < 10%
   d. execution_overhead < 100ms

5. Write 04_validation.md with results
```

---

## Contract Decorator Specifications

### Preconditions

```python
from contractme import precondition

@precondition(lambda data: isinstance(data, dict))
@precondition(lambda data: "dataset_type" in data)
def validate_full_contracts(data: Dict) -> Tuple[bool, str]:
    """Preconditions check input structure before validation."""
    ...
```

### Postconditions

```python
from contractme import postcondition

class Phase2AOutputWithContracts:
    @postcondition(lambda self: len(self.hypotheses) >= 1)
    @postcondition(lambda self: self.dataset_type in ["standard", "custom", "programmatic-api"])
    @postcondition(lambda self: 
        self.dataset_type != "standard" or 
        self.dataset_name in STANDARD_DATASETS
    )
    def __init__(self, **data):
        """Postconditions enforce invariants after initialization."""
        super().__init__(**data)
```

### Policy Configuration

```python
from contractme import set_policy

# Raise exceptions on contract violations (default)
set_policy("raise")

# Alternative: log warnings only (for testing)
# set_policy("warn")
```

---

## Constants

```python
# src/validation/constants.py

STANDARD_DATASETS = [
    "MNIST",
    "CIFAR10",
    "CIFAR100",
    "ImageNet",
    "COCO",
    "SQuAD",
    "WikiText",
    "GLUE",
]

EXISTING_BENCHMARKS = [
    "SuperGLUE",
    "GLUE",
    "ImageNet1K",
    "COCO Detection",
    "SQuAD v1.1",
    "SQuAD v2.0",
]

FORBIDDEN_DATASET_KEYWORDS = [
    "synthetic",
    "simulated",
    "generated",
]

FORBIDDEN_EVAL_KEYWORDS = [
    "human",
    "manual",
    "annotator",
    "labeler",
]
```

---

## File Structure

```
src/validation/
├── __init__.py
├── schemas.py          # Phase2AOutput, Phase2AOutputWithPatterns
├── contracts.py        # Phase2AOutputWithContracts
├── constants.py        # STANDARD_DATASETS, EXISTING_BENCHMARKS
└── executors.py        # validate_schema_only, validate_schema_pattern, validate_full_contracts

tests/phase_boundary_validation/
├── __init__.py
├── conftest.py
├── test_cases.yaml
├── test_schema_only.py
├── test_schema_pattern.py
├── test_contract_validation.py
└── generate_test_cases.py

experiments/
└── h_e1_contract_validation.py
```

---

## Implementation Notes

1. **Pydantic strict mode** prevents type coercion (catches "123" as int)
2. **field_validator** runs after type validation (layer 2 depends on layer 1)
3. **contractme decorators** check after object initialization (layer 3 depends on layer 2)
4. **Test case mutations** generate violations by changing single fields
5. **YAML storage** allows manual inspection and modification of test cases
6. **Pytest parametrize** runs all 20 cases with single test function

---

**Status:** DRAFT  
**Version:** 1.0  
**Next Phase:** Phase 4 - Coding
