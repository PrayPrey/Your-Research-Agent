# Architecture Design: H-M3 Composition-Level Contract Validation

**Hypothesis ID:** h-m3  
**Document Type:** Architecture  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

**Applied Patterns:** PyTorch DTensor validation patterns, tensorguard decorator API, composition-level contract validation

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Analyzed h-m1 actual implementation  
**Analyzed Path**: docs/youra_research/h-m1/code/  
**Findings**: Reusable decorator pattern (@validate_at_import), custom exception hierarchy (ShapeViolation, DeviceViolation, DtypeViolation), probe-based validation (1-sample batch)

---

## 1. System Overview

### 1.1 Architecture Principle
Composition-level contract validation framework extending h-m1's structural validation to multi-tensor cross-library scenarios. Validates device placement, dtype consistency, and layout compatibility across library boundaries (PyTorch + CUDA + Transformers) at import/setup time.

### 1.2 Core Components

```
code/
├── composition_validator.py  # @validate_composition decorator (extends h-m1 validator)
├── test_cases.py            # Cross-library defect test suite (10-20 cases)
├── run_experiment.py        # Test harness with baseline/proposed comparison
├── evaluate.py              # Detection rate calculation + visualization
└── figures/                 # Output directory for plots
```

### 1.3 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Decorator | Python functools.wraps | Wrap functions with composition validation |
| Validation | torch.Tensor device/dtype/layout properties | Cross-library consistency checks |
| Test Cases | Programmatic generation from real PyTorch/HF issues | Defect corpus |
| Metrics | Python stdlib (no scipy for PoC) | Detection rate calculation |
| Visualization | matplotlib | Detection rate bar chart |

---

## 2. Module Specifications

### 2.1 Core Validator

#### `composition_validator.py`

**Dependencies**: torch (extends h-m1 validator pattern)

```python
import torch
import functools
from typing import Callable, Dict, Any, List

class CompositionViolation(Exception):
    def __init__(self, message: str, violations: List[Dict]): ...

class DeviceConsistencyViolation(CompositionViolation): ...
class DtypeConsistencyViolation(CompositionViolation): ...
class LayoutConsistencyViolation(CompositionViolation): ...

def validate_composition(
    device_consistency: bool = True,
    dtype_spec: Dict[str, torch.dtype] = None,
    layout_spec: Dict[str, torch.layout] = None
) -> Callable:
    """Decorator for composition-level contract validation."""
    ...

class CompositionValidator:
    def __init__(self): ...
    def validate_device_consistency(self, tensors: List[torch.Tensor]) -> bool: ...
    def validate_dtype_consistency(self, tensors: List[torch.Tensor], expected: torch.dtype) -> bool: ...
    def validate_layout_consistency(self, tensors: List[torch.Tensor]) -> bool: ...
    def format_violation_message(self, violations: List[Dict]) -> str: ...
```

### 2.2 Test Suite

#### `test_cases.py`

**Dependencies**: torch, composition_validator

```python
from typing import List, Dict, Callable
import torch

class DefectTestCase:
    defect_id: str
    category: str
    setup_func: Callable
    expected_violation: str
    source_issue: str

def create_device_mismatch_tests() -> List[DefectTestCase]: ...
def create_dtype_mismatch_tests() -> List[DefectTestCase]: ...
def create_layout_mismatch_tests() -> List[DefectTestCase]: ...
def create_composition_tests() -> List[DefectTestCase]: ...

def load_all_test_cases() -> List[DefectTestCase]:
    """Load all 10-20 test cases from real PyTorch/HF issues."""
    ...
```

### 2.3 Experiment Harness

#### `run_experiment.py`

**Dependencies**: composition_validator, test_cases, torch

```python
import json
import time
from datetime import datetime
from typing import Dict, List

class ExperimentResult:
    test_id: str
    defect_category: str
    baseline_detected: bool
    proposed_detected: bool
    detection_time: float
    error_message: str

def run_baseline(test_case: DefectTestCase) -> bool:
    """Run test WITHOUT composition contracts (baseline)."""
    ...

def run_with_contracts(test_case: DefectTestCase) -> Dict:
    """Run test WITH composition contracts (proposed)."""
    ...

def main() -> int:
    """Execute experiment: baseline vs proposed comparison."""
    ...
```

### 2.4 Evaluation

#### `evaluate.py`

**Dependencies**: matplotlib, json

```python
import matplotlib.pyplot as plt
import json
from pathlib import Path
from typing import Dict, List

def calculate_detection_rate(results: List[Dict]) -> Dict[str, float]:
    """Compute detection rate from experiment results."""
    ...

def calculate_false_positive_rate(results: List[Dict]) -> float:
    """Calculate FP rate on control tests."""
    ...

def generate_detection_chart(baseline_rate: float, proposed_rate: float, output_path: Path) -> None:
    """Generate required detection rate bar chart with 60% threshold."""
    ...

def generate_category_breakdown(results: List[Dict], output_path: Path) -> None:
    """Generate defect category breakdown chart."""
    ...

def main() -> None:
    """Load results, calculate metrics, generate visualizations."""
    ...
```

---

## 3. External Dependencies (Base Hypothesis)

### Module Paths (From h-m1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| validate_at_import | `from contracts.validator import validate_at_import` | `h-m1/code/contracts/validator.py` |
| ShapeViolation | `from contracts.validator import ShapeViolation` | `h-m1/code/contracts/validator.py` |
| DeviceViolation | `from contracts.validator import DeviceViolation` | `h-m1/code/contracts/validator.py` |
| DtypeViolation | `from contracts.validator import DtypeViolation` | `h-m1/code/contracts/validator.py` |

**Note**: h-m3 extends h-m1's exception hierarchy and decorator pattern. h-m1 provides structural (single-tensor) validation; h-m3 adds composition (multi-tensor cross-library) validation.

**Verified from**: `/workspace/TEST_scope/docs/youra_research/h-m1/code/` (actual implementation)

---

## 4. Data Flow

### 4.1 Composition Validation Flow

```
1. Load test case (test_cases.py)
   ↓
2. Baseline run (no contracts) → measure detection
   ↓
3. Proposed run (with @validate_composition) → measure detection
   ↓
4. Compare detection stages
   ├─ Baseline: runtime error (if detected)
   └─ Proposed: import/setup time error (composition contract triggered)
   ↓
5. Record result (detected, detection_time, stage)
```

### 4.2 Defect Test Case Execution

```
Test Case Setup (from real PyTorch/HF issues):
  1. Device mismatch: scaled_dot_product_attention (query on CUDA, mask on CPU)
  2. Dtype mismatch: conv2d (input float32, weight float16)
  3. Layout mismatch: sparse tensor + dense operation
  4. Cross-library: HF Diffusers generator device != tensor device
     ↓
Baseline Execution:
  - Run operation WITHOUT contracts
  - Measure: Does runtime error occur? Time to error?
     ↓
Proposed Execution:
  - Apply @validate_composition decorator
  - Measure: Does contract detect violation at import/setup time?
     ↓
Detection Stage Comparison:
  - Baseline: runtime (training loop) or none
  - Proposed: import/setup time (contract validation)
```

### 4.3 Evaluation Pipeline

```
1. run_experiment.py → experiment_results.json
   ↓
2. evaluate.py reads results
   ↓
3. Calculate metrics:
   - Detection rate = (proposed_detected / total_defects) × 100%
   - Baseline rate (for comparison)
   - Category breakdown (device/dtype/layout/composition)
   - False positive rate (on control tests)
   ↓
4. Generate visualizations:
   - figures/detection_rate.png (mandatory bar chart)
   - figures/category_breakdown.png (optional)
   - figures/execution_time.png (optional)
```

---

## 5. Interface Contracts

### 5.1 Decorator API

**User-Facing Interface:**
```python
from composition_validator import validate_composition
import torch

@validate_composition(
    device_consistency=True,
    dtype_spec={'x': torch.float32, 'mask': torch.float32},
    layout_spec={'x': torch.strided, 'mask': torch.strided}
)
def attention_forward(x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    return torch.nn.functional.scaled_dot_product_attention(
        query=x, key=x, value=x, attn_mask=mask
    )
```

**Validation Checks:**
1. **Device Consistency**: All tensors on same device (cuda vs cpu)
2. **Dtype Consistency**: Tensors match expected dtypes (float32 vs float16)
3. **Layout Consistency**: Tensors have compatible layouts (strided vs sparse)

### 5.2 Test Case Schema

**Defect Test Case Structure:**
```python
{
    "defect_id": "DM-001",
    "category": "device_mismatch",
    "source_issue": "PyTorch #166117",
    "description": "scaled_dot_product_attention: query on CUDA, mask on CPU",
    "setup": lambda: {
        'query': torch.randn(1, 8, 10, 64, device='cuda'),
        'key': torch.randn(1, 8, 10, 64, device='cuda'),
        'value': torch.randn(1, 8, 10, 64, device='cuda'),
        'attn_mask': torch.ones(10, 10, dtype=torch.bool)  # CPU!
    },
    "expected_violation": "device_mismatch"
}
```

**Categories:**
- `device_mismatch`: CUDA vs CPU inconsistency (5 cases)
- `dtype_mismatch`: float32 vs float16 incompatibility (3 cases)
- `layout_mismatch`: strided vs sparse incompatibility (2 cases)
- `composition`: Cross-library coordination errors (5 cases)

### 5.3 Results Schema

**Experiment Results JSON:**
```json
{
  "experiment_id": "h-m3-poc",
  "timestamp": "2026-07-11T...",
  "test_results": [
    {
      "test_id": "DM-001",
      "category": "device_mismatch",
      "baseline_detected": false,
      "baseline_stage": "none",
      "proposed_detected": true,
      "proposed_stage": "import",
      "detection_time": 0.032,
      "error_message": "Device mismatch: query on cuda:0, attn_mask on cpu"
    }
  ],
  "summary": {
    "total_tests": 15,
    "baseline_detection_rate": 0.0,
    "proposed_detection_rate": 73.3,
    "false_positive_rate": 0.0,
    "avg_detection_time": 0.028
  }
}
```

---

## 6. Error Handling Strategy

### 6.1 Composition Violation Exceptions

**Exception Hierarchy** (extends h-m1):
```
CompositionViolation (base)
├── DeviceConsistencyViolation
├── DtypeConsistencyViolation
└── LayoutConsistencyViolation
```

**Error Message Format:**
```
CompositionViolation: Device consistency violated in scaled_dot_product_attention()
  Parameter 'query': cuda:0
  Parameter 'key': cuda:0
  Parameter 'value': cuda:0
  Parameter 'attn_mask': cpu

  Suggestion: Move attn_mask to CUDA device before passing to attention.
  Fix: attn_mask = attn_mask.to('cuda')
```

### 6.2 Graceful Degradation

**Validation Failures:**
- If CUDA unavailable → Skip device consistency tests, log warning
- If test case setup fails → Skip test, log as "setup_error"
- If baseline execution crashes → Record as "baseline_undetected" (contract would help)

**Control Tests (False Positive Prevention):**
- Run 5-10 valid test cases (correct device/dtype/layout)
- Any violations detected on valid cases → Count as false positive
- Target: FP rate <5%

---

## 7. Performance Optimization

### 7.1 Validation Overhead

**Target Breakdown:**
- Decorator initialization: <10ms
- Device/dtype/layout checks: <20ms
- Total per test case: <30ms
- **Total test suite (15 cases): <1s**

**Optimization Techniques:**
- Minimal overhead: Only check device/dtype/layout properties (no sample execution)
- Early exit: Return on first violation detected
- No caching needed: Validation is lightweight (<30ms per test)

### 7.2 Test Case Execution

**Execution Budget:**
- Test case setup: <100ms
- Baseline run: <1s (may fail at runtime)
- Proposed run: <100ms (fails at import/setup time)
- **Total per test: <2s, Total suite: <30s (well below 10s constraint)**

**Note**: 10s constraint applies to individual test execution, not full suite.

---

## 8. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Composition Validator | Implement @validate_composition decorator with device/dtype/layout checks | 14 | Module(4) + Deps(2) + Algo(4) + Integ(4) |
| A-2 | Test Case Generation | Create 10-20 defect cases from PyTorch/HF issues (device/dtype/layout/composition) | 12 | Module(3) + Deps(2) + Algo(3) + Integ(4) |
| A-3 | Baseline Experiments | Implement no-contract baseline execution and measurement | 9 | Module(2) + Deps(2) + Algo(2) + Integ(3) |
| A-4 | Contract Validation | Run all test cases with contracts, measure detection stage/time | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |
| A-5 | Metrics Calculation | Compute detection rate, FP rate, category breakdown | 8 | Module(2) + Deps(1) + Algo(3) + Integ(2) |
| A-6 | Visualization | Generate detection rate bar chart with 60% threshold line | 9 | Module(2) + Deps(2) + Algo(2) + Integ(3) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-1], Medium(9-13): [A-2, A-3, A-4, A-6], Low(4-8): [A-5]

**Complexity Scoring:**
- Module_Size: 1 (single function) to 5 (multiple classes with state)
- Dependencies: 1 (stdlib only) to 5 (external + PyTorch + h-m1 modules)
- Algorithm: 1 (trivial) to 5 (composition-level validation logic)
- Integration: 1 (isolated) to 5 (cross-module coordination + h-m1 extension)

---

## 9. Technology Integration

### 9.1 PyTorch Integration

**Device Detection:**
```python
def validate_device_consistency(tensors: List[torch.Tensor]) -> bool:
    if not tensors:
        return True
    
    first_device = tensors[0].device
    for tensor in tensors[1:]:
        if tensor.device != first_device:
            return False
    return True
```

**Dtype Validation:**
```python
def validate_dtype_consistency(tensors: List[torch.Tensor], expected: torch.dtype) -> bool:
    return all(t.dtype == expected for t in tensors)
```

**Layout Validation:**
```python
def validate_layout_consistency(tensors: List[torch.Tensor]) -> bool:
    if not tensors:
        return True
    
    first_layout = tensors[0].layout
    for tensor in tensors[1:]:
        if tensor.layout != first_layout:
            return False
    return True
```

### 9.2 Real Defect Examples (Test Case Sources)

**Device Mismatch Cases:**
1. PyTorch #166117: `scaled_dot_product_attention` (query CUDA, mask CPU)
2. PyTorch #168010: `conv2d` (input CUDA, weight CPU)
3. PyTorch #159133: `torch.compile` cross-device error
4. HF Diffusers #3313: Generator device != tensor device

**Dtype Mismatch Cases:**
1. Mixed precision: float32 model + float16 input
2. Autocast boundaries: Nested autocast contexts
3. Cross-library dtype assumptions

**Layout Mismatch Cases:**
1. Sparse tensor + dense operation
2. Strided layout assumptions violated

### 9.3 h-m1 Pattern Reuse

**Import-Time Validation Pattern:**
```python
# h-m1 pattern: validate_at_import with probe execution
# h-m3 adaptation: validate_composition with multi-tensor checks

@validate_composition(device_consistency=True)
def forward(self, x, mask):
    # Decorator validates x.device == mask.device at call time
    return attention(x, mask)
```

**Exception Hierarchy Reuse:**
```python
# h-m1: ShapeViolation, DeviceViolation, DtypeViolation (single-tensor)
# h-m3: DeviceConsistencyViolation, DtypeConsistencyViolation (multi-tensor)

# h-m3 extends h-m1 exception base classes
class CompositionViolation(Exception):  # New base for h-m3
    pass

class DeviceConsistencyViolation(CompositionViolation):  # Extends concept from h-m1 DeviceViolation
    pass
```

---

## 10. Validation Strategy

### 10.1 Detection Rate Validation

**Gate Criteria (SHOULD_WORK):**
- Detection rate ≥60% → PASS
- Detection rate 40-59% → PARTIAL (document limitation)
- Detection rate <40% → FAIL (mechanism insufficient)

**Measurement:**
```python
detection_rate = (proposed_detected_count / total_defects) * 100
```

### 10.2 False Positive Prevention

**Control Tests:**
- Run 5-10 valid test cases (correct composition)
- Expected: 0 violations detected
- Target: FP rate <5%

**Valid Test Cases:**
1. All tensors on same device (CUDA)
2. All tensors same dtype (float32)
3. All tensors same layout (strided)
4. Cross-library valid composition (HF pipeline with correct setup)

### 10.3 Execution Time Constraint

**Requirement:** ≤10s per test case
**Expected:** <2s per test case (well below constraint)

**Breakdown:**
- Baseline run: <1s (may fail at runtime)
- Proposed run: <100ms (fails at import/setup)
- Overhead: <30ms (validation only)

---

## 11. Risk Mitigation

### 11.1 Technical Risks

**Risk: Detection rate <60% (gate failure)**
- Mitigation: Focus on highest-impact defects (device mismatch first)
- Fallback: Document as partial success (manual curation required)

**Risk: False positives >5%**
- Mitigation: Test on diverse valid cases (CUDA/CPU, float32/float16 valid combinations)
- Fallback: Adjust validation logic to reduce spurious warnings

**Risk: CUDA unavailable (CI environment)**
- Mitigation: Support CPU-only mode, skip CUDA-specific tests
- Fallback: Document as environment limitation

### 11.2 Evaluation Risks

**Risk: Test cases too synthetic (not representative)**
- Mitigation: Generate from REAL PyTorch/HF issue tracker patterns
- Validation: Document source issue ID for each test case

**Risk: Cherry-picking defects inflates detection rate**
- Mitigation: Use ALL defects from documented issue categories
- Validation: Include test case selection criteria in test_cases.py

---

## 12. Appendices

### A. Example Composition Contract

```python
from composition_validator import validate_composition
import torch
import torch.nn.functional as F

@validate_composition(
    device_consistency=True,
    dtype_spec={'query': torch.float32, 'key': torch.float32, 'value': torch.float32, 'attn_mask': torch.float32}
)
def attention_forward(query, key, value, attn_mask):
    """Scaled dot-product attention with composition-level contracts."""
    return F.scaled_dot_product_attention(
        query=query, key=key, value=value, attn_mask=attn_mask
    )

# Test case: Device mismatch (from PyTorch #166117)
query = torch.randn(1, 8, 10, 64, device='cuda')
key = torch.randn(1, 8, 10, 64, device='cuda')
value = torch.randn(1, 8, 10, 64, device='cuda')
attn_mask = torch.ones(10, 10, dtype=torch.bool)  # CPU!

try:
    output = attention_forward(query, key, value, attn_mask)
except DeviceConsistencyViolation as e:
    print(f"Detected at import/setup time: {e}")
    # Output: "Device mismatch: query on cuda:0, attn_mask on cpu"
```

### B. Test Case Generation Example

```python
from test_cases import create_device_mismatch_tests

# Generate device mismatch tests from real PyTorch issues
test_cases = create_device_mismatch_tests()

# Example test case structure
assert test_cases[0] == {
    'defect_id': 'DM-001',
    'category': 'device_mismatch',
    'source_issue': 'PyTorch #166117',
    'description': 'scaled_dot_product_attention: query CUDA, mask CPU',
    'setup': lambda: {
        'query': torch.randn(1, 8, 10, 64, device='cuda'),
        'attn_mask': torch.ones(10, 10, dtype=torch.bool)  # CPU
    },
    'expected_violation': 'device_mismatch'
}
```

### C. Detection Rate Calculation

```python
import json

# Load results
with open('experiment_results.json') as f:
    results = json.load(f)

# Calculate detection rate
total_defects = len(results['test_results'])
proposed_detected = sum(1 for r in results['test_results'] if r['proposed_detected'])
detection_rate = (proposed_detected / total_defects) * 100

print(f"Detection rate: {detection_rate:.1f}%")

# Gate decision
if detection_rate >= 60:
    print("SHOULD_WORK GATE: PASS")
elif detection_rate >= 40:
    print("SHOULD_WORK GATE: PARTIAL (document limitation)")
else:
    print("SHOULD_WORK GATE: FAIL")
```

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Steps:** Proceed to Phase 4 (Implementation)  
**Expected Timeline:** Phase 4 completion within 1-2 hours (PoC scale)
