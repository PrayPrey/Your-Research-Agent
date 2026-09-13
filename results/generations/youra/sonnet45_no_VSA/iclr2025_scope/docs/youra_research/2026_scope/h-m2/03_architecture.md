# Architecture Design: H-M2 Metamorphic Contract Validation

**Hypothesis ID:** h-m2  
**Document Type:** Architecture  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

**Applied Patterns:** Decorator-based validation, numerical tolerance checking, probe-based testing

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: patterns found from base code  
**Analyzed Path**: docs/youra_research/h-m1/code/  
**Findings**: h-m1 implements decorator-based structural contracts with import-time validation. Reuses decorator pattern and probe-based validation approach.

---

## 1. System Overview

### 1.1 Architecture Principle
Extends h-m1 structural contracts with metamorphic property validation (softmax sum=1.0, dropout identity) using lightweight numerical probes.

### 1.2 Core Components

```
contracts/                # Extends h-m1 contracts
├── metamorphic.py        # Metamorphic property validators
└── probes.py             # Numerical probe generation

test_suite/               # Programmatic API test cases
├── scenarios.py          # Test scenario definitions
└── defect_injection.py   # Controlled violation injection

experiments/
└── run_experiment.py     # Main experiment runner

results/
└── *.json               # Detection results, metrics
```

### 1.3 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Validation | h-m1 decorator pattern | Structural + metamorphic |
| Numerical checks | torch.allclose | Tolerance-based validation |
| Probes | Small tensors (4x10, 100) | Lightweight validation |
| Test framework | Python unittest | Test execution |

---

## 2. Module Specifications

### 2.1 Metamorphic Validators

#### `contracts/metamorphic.py`

**Dependencies**: torch, h-m1 validator

```python
import torch
from typing import Callable

class MetamorphicValidator:
    @staticmethod
    def validate_softmax(func: Callable, probe_input: torch.Tensor, 
                         dim: int = -1, rtol: float = 1e-5, atol: float = 1e-7) -> bool: ...
    
    @staticmethod
    def validate_dropout_identity(module: torch.nn.Module, probe_input: torch.Tensor, 
                                  eval_mode: bool = True) -> bool: ...
    
    @staticmethod
    def generate_probe(shape: tuple, dtype: torch.dtype = torch.float32) -> torch.Tensor: ...

def validate_metamorphic(softmax: bool = False, dropout: bool = False, 
                         rtol: float = 1e-5, atol: float = 1e-7) -> Callable:
    """Decorator for metamorphic property validation."""
    ...
```

#### `contracts/probes.py`

**Dependencies**: torch

```python
class ProbeGenerator:
    @staticmethod
    def softmax_probe(batch_size: int = 4, num_classes: int = 10) -> torch.Tensor: ...
    
    @staticmethod
    def dropout_probe(size: int = 100) -> torch.Tensor: ...
    
    @staticmethod
    def validate_sum_property(output: torch.Tensor, dim: int, 
                              rtol: float, atol: float) -> bool: ...
    
    @staticmethod
    def validate_identity(input: torch.Tensor, output: torch.Tensor) -> bool: ...
```

### 2.2 Test Suite

#### `test_suite/scenarios.py`

**Dependencies**: torch, metamorphic

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class TestScenario:
    scenario_id: str
    defect_type: str
    test_func: Callable
    expected_detection: bool

class ScenarioGenerator:
    def __init__(self): ...
    
    def control_scenario(self) -> TestScenario: ...
    def softmax_violation_scenario(self) -> TestScenario: ...
    def dropout_violation_scenario(self) -> TestScenario: ...
    
    def generate_all(self) -> list[TestScenario]: ...
```

#### `test_suite/defect_injection.py`

**Dependencies**: torch

```python
class DefectInjector:
    @staticmethod
    def inject_softmax_violation(func: Callable) -> Callable:
        """Modify softmax output to violate sum=1.0 property."""
        ...
    
    @staticmethod
    def inject_dropout_violation(module: torch.nn.Module) -> torch.nn.Module:
        """Force dropout to apply in eval mode."""
        ...
    
    @staticmethod
    def create_valid_operation() -> tuple[Callable, torch.nn.Module]:
        """Create valid operations for control tests."""
        ...
```

### 2.3 Experiment Runner

#### `experiments/run_experiment.py`

**Dependencies**: test_suite, contracts, torch

```python
import time
import json
from datetime import datetime

class ExperimentRunner:
    def __init__(self, scenarios: list[TestScenario]): ...
    
    def run_baseline(self) -> dict:
        """Run without metamorphic contracts (detection rate = 0%)."""
        ...
    
    def run_with_contracts(self) -> dict:
        """Run with metamorphic validation enabled."""
        ...
    
    def calculate_metrics(self, results: dict) -> dict:
        """Calculate detection rate, execution time, false positives."""
        ...
    
    def save_results(self, results: dict, filepath: str): ...

def main():
    """Execute metamorphic contract validation experiment."""
    ...
```

---

## 3. External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| validate_structural | `from h_m1.contracts.validator import validate_structural` | h-m1/code/contracts/validator.py |
| validate_at_import | `from h_m1.contracts.validator import validate_at_import` | h-m1/code/contracts/validator.py |
| ContractViolationError | `from h_m1.contracts.validator import ContractViolationError` | h-m1/code/contracts/validator.py |

**Verified from**: /workspace/TEST_scope/docs/youra_research/h-m1/code/ (actual implementation)

**Note**: h-m2 extends h-m1 by adding metamorphic property checks to the decorator pattern. Structural validation from h-m1 is reused as foundation.

---

## 4. Data Flow

### 4.1 Metamorphic Validation Flow

```
1. Test scenario initialization
   ↓
2. Generate probe input (4x10 for softmax, 100 for dropout)
   ↓
3. Execute test function/module with probe
   ↓
4. Validate metamorphic property:
   - Softmax: sum(output, dim=-1) ≈ 1.0 (rtol=1e-5, atol=1e-7)
   - Dropout: output == input (eval mode)
   ↓
5. Record detection result (pass/fail)
   ↓
6. Aggregate results across test suite
```

### 4.2 Defect Injection Flow

```
1. Create valid operation (control)
   ↓
2. Inject defect:
   - Softmax: multiply output by 0.9 (sum ≠ 1.0)
   - Dropout: force train=True in eval mode
   ↓
3. Apply metamorphic validator
   ↓
4. Detect violation
   ├─ Detected → Log success
   └─ Not detected → Log false negative
```

---

## 5. Interface Contracts

### 5.1 Metamorphic Decorator API

**User-Facing Interface:**
```python
from contracts.metamorphic import validate_metamorphic
import torch
import torch.nn as nn

# Softmax validation
@validate_metamorphic(softmax=True, rtol=1e-5, atol=1e-7)
def attention_softmax(x: torch.Tensor) -> torch.Tensor:
    return torch.softmax(x, dim=-1)

# Dropout validation
class ModelWithDropout(nn.Module):
    def __init__(self):
        super().__init__()
        self.dropout = nn.Dropout(p=0.5)
    
    @validate_metamorphic(dropout=True)
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(x)
```

### 5.2 Test Scenario Schema

**Scenario Definition:**
```python
scenario = TestScenario(
    scenario_id="softmax-violation-1",
    defect_type="softmax_sum",
    test_func=lambda: test_softmax_violation(),
    expected_detection=True
)
```

### 5.3 Results Schema

**Detection Results JSON:**
```json
{
  "experiment_id": "h-m2-poc",
  "timestamp": "2026-07-11T12:00:00",
  "detection_results": [
    {
      "scenario_id": "control-1",
      "defect_type": "none",
      "detected": false,
      "execution_time": 0.012
    },
    {
      "scenario_id": "softmax-violation-1",
      "defect_type": "softmax_sum",
      "detected": true,
      "detection_stage": "validation",
      "execution_time": 0.025
    }
  ],
  "summary": {
    "total_tests": 50,
    "total_violations": 40,
    "detected": 32,
    "detection_rate": 80.0,
    "execution_time_total": 0.45,
    "false_positive_rate": 0.0
  }
}
```

---

## 6. Error Handling Strategy

### 6.1 Metamorphic Violations

**Exception Hierarchy:**
```
Exception
└── ContractViolationError (from h-m1)
    ├── MetamorphicViolation (new)
        ├── SoftmaxSumViolation
        └── DropoutIdentityViolation
```

**Error Message Format:**
```
SoftmaxSumViolation: Softmax sum property violated
  Expected: sum(output, dim=-1) ≈ 1.0
  Actual:   sum = 0.9 (deviation: 0.1)
  Tolerance: rtol=1e-5, atol=1e-7
  
  Suggestion: Check softmax implementation or post-processing steps.
```

### 6.2 Numerical Tolerance

**Floating-Point Handling:**
- Use torch.allclose for sum validation
- Default tolerance: rtol=1e-5, atol=1e-7
- Configurable via decorator parameters

---

## 7. Performance Optimizations

### 7.1 Probe Size Limits

**Target Overhead:**
- Probe generation: <5ms
- Softmax validation: <10ms (4x10 tensor)
- Dropout validation: <10ms (100-element tensor)
- Total per test: <30ms

### 7.2 Execution Budget

**Total Test Suite:**
- 50 test cases × 30ms = 1.5s
- Target: <10s (well within budget)

---

## 8. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Metamorphic Validators | Implement softmax sum and dropout identity validators | 12 | Module(3) + Deps(2) + Algo(4) + Integ(3) |
| B-2 | Test Scenario Generation | Create control, softmax, dropout test scenarios | 10 | Module(3) + Deps(2) + Algo(2) + Integ(3) |
| B-3 | Defect Injection | Implement controlled violation injection | 11 | Module(2) + Deps(2) + Algo(4) + Integ(3) |
| B-4 | Experiment Runner | Run baseline vs contracts, calculate metrics | 13 | Module(3) + Deps(3) + Algo(3) + Integ(4) |
| B-5 | Numerical Tolerance Testing | Validate rtol/atol configurations for stability | 9 | Module(2) + Deps(1) + Algo(4) + Integ(2) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-1, B-2, B-3, B-4, B-5], Low(4-8): []

**Complexity Scoring:**
- Module_Size: 1-5 (functions to classes)
- Dependencies: 1-5 (h-m1 reuse + PyTorch)
- Algorithm: 1-5 (numerical validation complexity)
- Integration: 1-5 (test framework coordination)

---

## 9. Non-Functional Requirements Mapping

### 9.1 Performance (NFR-1)
- Execution time ≤10s: Probe-based validation with minimal tensor sizes
- Overhead <30ms per test: Lightweight numerical checks

### 9.2 Reliability (NFR-2)
- Determinism: Fixed seeds for probe generation
- Numerical stability: Tolerance-based validation (rtol=1e-5, atol=1e-7)
- False positive rate <5%: Control scenarios validate no spurious failures

### 9.3 Code Quality (NFR-3)
- Pattern consistency: Extends h-m1 decorator pattern
- Documentation: Docstrings for all validation methods
- Testing: pytest-based test suite

### 9.4 Research Validity (NFR-4)
- PoC focus: Mechanism validation with controlled defects
- Ground truth: Known violations for detection validation
- Gate compliance: SHOULD_WORK (≥70% detection rate)

---

## 10. Technology Integration

### 10.1 PyTorch Integration

**Softmax Validation:**
```python
output = torch.softmax(x, dim=-1)
sum_check = torch.allclose(
    output.sum(dim=-1),
    torch.ones(output.shape[:-1]),
    rtol=1e-5,
    atol=1e-7
)
```

**Dropout Validation:**
```python
module.eval()
input = torch.randn(100)
output = module(input)
identity_check = torch.equal(input, output)
```

### 10.2 h-m1 Pattern Reuse

**Decorator Extension:**
```python
from h_m1.contracts.validator import validate_structural

# Combine structural + metamorphic
@validate_structural(input_shapes={'x': ('B', 10)}, dtype=torch.float32)
@validate_metamorphic(softmax=True)
def combined_validation(x):
    return torch.softmax(x, dim=-1)
```

---

## 11. Validation Strategy

### 11.1 Unit Tests

**Test Coverage:**
- Softmax sum validation: Edge cases (all zeros, large values)
- Dropout identity: p=0.0, p=0.5, p=1.0 configurations
- Numerical tolerance: Boundary cases for rtol/atol

### 11.2 Integration Tests

**Test Scenarios:**
- Full pipeline: Scenario → Validation → Detection
- Baseline comparison: No contracts (0% detection) vs contracts (≥70%)
- False positives: 10-20 control scenarios

### 11.3 Acceptance Tests

**Gate Criteria:**
- Detection rate ≥70% (SHOULD_WORK)
- Execution time ≤10s
- False positive rate <5%
- All 3 scenarios tested (control, softmax, dropout)

---

## 12. Risk Mitigation

### 12.1 Technical Risks

**Risk: Numerical precision causes false positives**
- Mitigation: PyTorch test suite tolerance values (rtol=1e-5, atol=1e-7)
- Fallback: Widen tolerance if necessary, document in results

**Risk: Probe inputs not representative**
- Mitigation: PoC validation only - Phase 5 will use real defect corpus
- Validation: Document probe design rationale

### 12.2 Evaluation Risks

**Risk: Detection rate <70%**
- Consequence: SHOULD_WORK gate allows graceful degradation
- Mitigation: Document as limitation, h-m1 structural contracts remain valid

---

## 13. Appendices

### A. Example Metamorphic Validation

```python
from contracts.metamorphic import validate_metamorphic
import torch
import torch.nn as nn

# Softmax validation example
@validate_metamorphic(softmax=True, rtol=1e-5, atol=1e-7)
def attention_weights(logits: torch.Tensor) -> torch.Tensor:
    return torch.softmax(logits, dim=-1)

# Dropout validation example
class AttentionLayer(nn.Module):
    def __init__(self):
        super().__init__()
        self.dropout = nn.Dropout(p=0.1)
    
    @validate_metamorphic(dropout=True)
    def apply_dropout(self, attn_weights: torch.Tensor) -> torch.Tensor:
        return self.dropout(attn_weights)

# Test usage
layer = AttentionLayer()
layer.eval()  # Set to eval mode

# Generate probe
probe = torch.randn(4, 10)

# Validate (should pass - dropout is identity in eval mode)
output = layer.apply_dropout(probe)
```

### B. Defect Injection Example

```python
from test_suite.defect_injection import DefectInjector
import torch

# Inject softmax violation
def valid_softmax(x):
    return torch.softmax(x, dim=-1)

defective_softmax = DefectInjector.inject_softmax_violation(valid_softmax)

# Test detection
probe = torch.randn(4, 10)
try:
    output = defective_softmax(probe)
    # Validator should raise SoftmaxSumViolation
except SoftmaxSumViolation as e:
    print(f"Detected: {e}")
```

### C. Detection Metrics

```python
# Calculate detection rate
results = {
    "total_violations": 40,
    "detected": 32,
    "false_positives": 0,
    "control_tests": 10
}

detection_rate = (results["detected"] / results["total_violations"]) * 100
fp_rate = (results["false_positives"] / results["control_tests"]) * 100

print(f"Detection Rate: {detection_rate:.1f}%")  # Target: ≥70%
print(f"False Positive Rate: {fp_rate:.1f}%")   # Target: <5%

# Gate decision
if detection_rate >= 70:
    print("SHOULD_WORK GATE: PASS")
else:
    print("SHOULD_WORK GATE: Document as limitation")
```

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Steps:** Proceed to Phase 4 (Implementation)  
**Expected Timeline:** Phase 3 completion by 2026-07-12
