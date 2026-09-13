# Logic Design: H-M3 Composition-Level Contract Validation

**Hypothesis ID:** h-m3  
**Document Type:** Logic Design  
**Phase:** 3 - Implementation Planning  
**Status:** READY FOR CODING  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-m1 actual implementation  
**Analyzed Path**: docs/youra_research/h-m1/code/  
**Relevant Symbols**: validate_structural, validate_at_import, ShapeViolation, DeviceViolation, DtypeViolation, ContractViolationError

**Critical Finding**: h-m1 uses runtime validation (checks during forward pass). h-m3 extends to composition-level (multi-tensor cross-library) validation.

---

## KB Pattern Application

**Applied**: PyTorch decorator pattern (functools.wraps), HuggingFace device placement testing, multi-tensor consistency validation

---

## A-1: Composition Validator [Complexity: 14, Budget: 10]

### API Signatures

```python
from typing import Callable, Dict, List, Optional, Any
import torch
import functools


class CompositionViolation(Exception):
    """Base exception for composition-level violations."""
    def __init__(self, message: str, violations: List[Dict[str, Any]]):
        """Initialize with structured violation data.
        
        Args:
            message: Human-readable error message
            violations: List of dicts with keys: param_name, expected, actual, violation_type
        """
        super().__init__(message)
        self.violations = violations


class DeviceConsistencyViolation(CompositionViolation):
    """Raised when tensors are on inconsistent devices."""
    pass


class DtypeConsistencyViolation(CompositionViolation):
    """Raised when tensors have inconsistent dtypes."""
    pass


class LayoutConsistencyViolation(CompositionViolation):
    """Raised when tensors have incompatible layouts."""
    pass


def validate_composition(
    device_consistency: bool = True,
    dtype_spec: Optional[Dict[str, torch.dtype]] = None,
    layout_spec: Optional[Dict[str, torch.layout]] = None
) -> Callable:
    """Decorator for composition-level contract validation.
    
    Args:
        device_consistency: If True, validate all tensors on same device
        dtype_spec: Dict of param_name -> expected_dtype
        layout_spec: Dict of param_name -> expected_layout
    
    Returns:
        Decorator that wraps function with composition validation
    
    Raises:
        DeviceConsistencyViolation: If tensors on different devices
        DtypeConsistencyViolation: If dtypes don't match spec
        LayoutConsistencyViolation: If layouts incompatible
    
    Example:
        @validate_composition(
            device_consistency=True,
            dtype_spec={'query': torch.float32, 'mask': torch.float32}
        )
        def attention(query: Tensor, key: Tensor, value: Tensor, mask: Tensor):
            return F.scaled_dot_product_attention(query, key, value, attn_mask=mask)
    """
    ...


class CompositionValidator:
    """Core validator for composition-level contracts."""
    
    def validate_device_consistency(self, tensors: Dict[str, torch.Tensor]) -> Tuple[bool, Optional[str]]:
        """Validate all tensors on same device.
        
        Args:
            tensors: Dict of param_name -> tensor
        
        Returns:
            (is_valid, error_message). error_message is None if valid.
        """
        ...
    
    def validate_dtype_consistency(
        self,
        tensors: Dict[str, torch.Tensor],
        dtype_spec: Dict[str, torch.dtype]
    ) -> Tuple[bool, Optional[str]]:
        """Validate tensors match expected dtypes.
        
        Args:
            tensors: Dict of param_name -> tensor
            dtype_spec: Dict of param_name -> expected_dtype
        
        Returns:
            (is_valid, error_message). error_message is None if valid.
        """
        ...
    
    def validate_layout_consistency(self, tensors: Dict[str, torch.Tensor]) -> Tuple[bool, Optional[str]]:
        """Validate tensors have compatible layouts.
        
        Args:
            tensors: Dict of param_name -> tensor
        
        Returns:
            (is_valid, error_message). error_message is None if valid.
        """
        ...
    
    def format_violation_message(self, violations: List[Dict[str, Any]]) -> str:
        """Format structured violation data into actionable error message.
        
        Args:
            violations: List of violation dicts
        
        Returns:
            Formatted error message with suggestions
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| tensors | Dict[str, Tensor] | Parameter name to tensor mapping |
| violations | List[Dict] | Structured violation records |

### Pseudo-code

```
validate_composition(device_consistency, dtype_spec, layout_spec):
    1. def decorator(func):
        2. @functools.wraps(func)
        3. def wrapper(*args, **kwargs):
            # Extract tensors from args/kwargs
            4. tensor_dict = extract_tensors_from_args(func, args, kwargs)
            
            # Device consistency check
            5. if device_consistency:
                is_valid, error = validator.validate_device_consistency(tensor_dict)
                if not is_valid:
                    raise DeviceConsistencyViolation(error, violations=[...])
            
            # Dtype consistency check
            6. if dtype_spec:
                is_valid, error = validator.validate_dtype_consistency(tensor_dict, dtype_spec)
                if not is_valid:
                    raise DtypeConsistencyViolation(error, violations=[...])
            
            # Layout consistency check
            7. if layout_spec:
                is_valid, error = validator.validate_layout_consistency(tensor_dict)
                if not is_valid:
                    raise LayoutConsistencyViolation(error, violations=[...])
            
            # Execute function
            8. return func(*args, **kwargs)
        9. return wrapper
    10. return decorator

validate_device_consistency(tensors):
    1. if len(tensors) == 0:
        return (True, None)
    2. devices = {name: str(t.device) for name, t in tensors.items()}
    3. unique_devices = set(devices.values())
    4. if len(unique_devices) > 1:
        violations = [{'param': name, 'device': dev} for name, dev in devices.items()]
        message = format_violation_message(violations)
        return (False, message)
    5. return (True, None)

validate_dtype_consistency(tensors, dtype_spec):
    1. violations = []
    2. for param_name, expected_dtype in dtype_spec.items():
        if param_name not in tensors:
            continue
        actual_dtype = tensors[param_name].dtype
        if actual_dtype != expected_dtype:
            violations.append({
                'param': param_name,
                'expected': expected_dtype,
                'actual': actual_dtype
            })
    3. if violations:
        message = format_violation_message(violations)
        return (False, message)
    4. return (True, None)

validate_layout_consistency(tensors):
    1. layouts = {name: t.layout for name, t in tensors.items()}
    2. unique_layouts = set(layouts.values())
    3. if len(unique_layouts) > 1:
        violations = [{'param': name, 'layout': layout} for name, layout in layouts.items()]
        message = format_violation_message(violations)
        return (False, message)
    4. return (True, None)
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Decorator wrapper | Implement validate_composition decorator |
| L-1-2 | Tensor extraction | Extract tensors from args/kwargs using inspect |
| L-1-3 | Device validation | Check all tensors on same device |
| L-1-4 | Dtype validation | Check tensors match dtype_spec |
| L-1-5 | Layout validation | Check layout compatibility |
| L-1-6 | Violation formatting | Format structured error messages |
| L-1-7 | Exception hierarchy | Implement 3 exception classes |
| L-1-8 | Test integration | Unit tests for each validator |
| L-1-9 | Argument mapping | Map function signature to tensor dict |
| L-1-10 | Error suggestions | Generate actionable fix suggestions |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following exception classes from h-m1 are REFERENCED (not called) for conceptual consistency:

```python
# From: /workspace/TEST_scope/docs/youra_research/h-m1/code/contracts/validator.py

class ContractViolationError(Exception):
    """Base exception for contract violations."""
    pass

class ShapeViolation(ContractViolationError):
    """Raised when tensor shape doesn't match specification."""
    pass

class DeviceViolation(ContractViolationError):
    """Raised when tensor device doesn't match specification."""
    pass

class DtypeViolation(ContractViolationError):
    """Raised when tensor dtype doesn't match specification."""
    pass
```

**Note**: h-m3 does NOT import these classes. h-m3 implements its own exception hierarchy (CompositionViolation, DeviceConsistencyViolation, etc.) following the same pattern. h-m1 validates single-tensor structural properties; h-m3 validates multi-tensor composition properties.

**Verified from**: `/workspace/TEST_scope/docs/youra_research/h-m1/code/contracts/validator.py` (actual implementation)

---

## A-2: Test Case Generation [Complexity: 12, Budget: Not allocated - uses A-1 subtasks]

**Note**: Test case generation is part of the test harness, not a separate high-complexity task. Test cases are programmatically generated using documented defect patterns.

### Test Case Structure

```python
from typing import Callable, Dict, Any
import torch


class DefectTestCase:
    """Represents a single composition defect test case."""
    
    def __init__(
        self,
        defect_id: str,
        category: str,
        setup_func: Callable[[], Dict[str, torch.Tensor]],
        expected_violation: str,
        source_issue: str
    ):
        """Initialize test case.
        
        Args:
            defect_id: Unique ID (e.g., "DM-001")
            category: "device_mismatch", "dtype_mismatch", "layout_mismatch", "composition"
            setup_func: Function that returns dict of tensors with defect
            expected_violation: Expected violation type
            source_issue: Source issue tracker reference (e.g., "PyTorch #166117")
        """
        self.defect_id = defect_id
        self.category = category
        self.setup_func = setup_func
        self.expected_violation = expected_violation
        self.source_issue = source_issue


def create_device_mismatch_tests() -> List[DefectTestCase]:
    """Generate device mismatch test cases.
    
    Returns:
        List of 5 device mismatch test cases
    
    Example cases:
        - DM-001: scaled_dot_product_attention (query CUDA, mask CPU)
        - DM-002: conv2d (input CUDA, weight CPU)
        - DM-003: torch.compile cross-device
        - DM-004: HF Diffusers generator device mismatch
        - DM-005: Multi-GPU placement inconsistency
    """
    ...


def create_dtype_mismatch_tests() -> List[DefectTestCase]:
    """Generate dtype mismatch test cases (3 cases)."""
    ...


def create_layout_mismatch_tests() -> List[DefectTestCase]:
    """Generate layout mismatch test cases (2 cases)."""
    ...


def create_composition_tests() -> List[DefectTestCase]:
    """Generate cross-library composition test cases (5 cases)."""
    ...


def load_all_test_cases() -> List[DefectTestCase]:
    """Load all 15 test cases.
    
    Returns:
        List of 15 DefectTestCase objects
    """
    return (
        create_device_mismatch_tests() +
        create_dtype_mismatch_tests() +
        create_layout_mismatch_tests() +
        create_composition_tests()
    )
```

### Example Test Case Implementation

```python
def create_device_mismatch_tests():
    tests = []
    
    # DM-001: PyTorch #166117
    def dm001_setup():
        return {
            'query': torch.randn(1, 8, 10, 64, device='cuda'),
            'key': torch.randn(1, 8, 10, 64, device='cuda'),
            'value': torch.randn(1, 8, 10, 64, device='cuda'),
            'attn_mask': torch.ones(10, 10, dtype=torch.bool)  # CPU!
        }
    
    tests.append(DefectTestCase(
        defect_id='DM-001',
        category='device_mismatch',
        setup_func=dm001_setup,
        expected_violation='device_mismatch',
        source_issue='PyTorch #166117'
    ))
    
    # ... (4 more test cases)
    
    return tests
```

---

## Edge Cases & Error Handling

### Edge Case 1: No Tensors in Function Args

**Scenario**: Function has no tensor arguments (e.g., config-only function)  
**Solution**: Skip validation if tensor_dict is empty  
**Validation**: Return early from validator, no error

### Edge Case 2: CPU-Only Environment

**Scenario**: CUDA unavailable, all tensors on CPU  
**Solution**: Device consistency passes (all on CPU)  
**Validation**: Tests skip CUDA-specific cases if torch.cuda.is_available() == False

### Edge Case 3: Mixed Precision Training (AMP)

**Scenario**: Autocast changes dtypes at runtime  
**Solution**: dtype_spec optional, skip if not specified  
**Validation**: Only validate dtypes if explicitly specified in decorator

### Edge Case 4: Sparse Tensors

**Scenario**: Sparse tensor + dense tensor operation  
**Solution**: Layout consistency check detects torch.strided vs torch.sparse_coo  
**Validation**: Raise LayoutConsistencyViolation with clear message

### Edge Case 5: Optional Tensor Arguments

**Scenario**: Function has optional tensors (e.g., mask=None)  
**Solution**: Skip validation for None values  
**Validation**: Filter out None before checking consistency

---

## Algorithm Complexity Analysis

| Component | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| Tensor extraction | O(n) | O(n) | n = number of args |
| Device check | O(t) | O(t) | t = number of tensors |
| Dtype check | O(t) | O(1) | t = number of tensors |
| Layout check | O(t) | O(t) | t = number of tensors |
| Violation formatting | O(v) | O(v) | v = number of violations |
| Total per call | O(n + t) | O(n + t) | Negligible overhead |

**Expected Latency**: <10ms per decorated function call (property access only, no tensor operations)

---

## Implementation Notes

### Device Consistency Implementation

```python
def validate_device_consistency(tensors):
    if not tensors:
        return (True, None)
    
    # Extract devices
    devices = {name: str(t.device) for name, t in tensors.items()}
    unique_devices = set(devices.values())
    
    # Check consistency
    if len(unique_devices) > 1:
        # Format error message
        device_list = ", ".join(f"{name} on {dev}" for name, dev in devices.items())
        message = f"Device mismatch: {device_list}"
        suggestions = f"Suggestion: Move all tensors to same device before calling function."
        return (False, f"{message}\n{suggestions}")
    
    return (True, None)
```

### Dtype Consistency Implementation

```python
def validate_dtype_consistency(tensors, dtype_spec):
    violations = []
    
    for param_name, expected_dtype in dtype_spec.items():
        if param_name not in tensors:
            continue  # Skip optional params
        
        actual_dtype = tensors[param_name].dtype
        if actual_dtype != expected_dtype:
            violations.append({
                'param': param_name,
                'expected': str(expected_dtype),
                'actual': str(actual_dtype)
            })
    
    if violations:
        message = "Dtype mismatches detected:\n"
        for v in violations:
            message += f"  {v['param']}: expected {v['expected']}, got {v['actual']}\n"
        return (False, message)
    
    return (True, None)
```

### Layout Consistency Implementation

```python
def validate_layout_consistency(tensors):
    if not tensors:
        return (True, None)
    
    layouts = {name: t.layout for name, t in tensors.items()}
    unique_layouts = set(layouts.values())
    
    if len(unique_layouts) > 1:
        layout_list = ", ".join(f"{name}: {layout}" for name, layout in layouts.items())
        message = f"Layout mismatch: {layout_list}"
        return (False, message)
    
    return (True, None)
```

---

## Summary

This logic design provides **copy-paste ready APIs** for composition-level contract validation. Key components:

1. **Composition Validator**: Multi-tensor device/dtype/layout consistency checks
2. **Test Case Framework**: Programmatic generation of 15 real defect cases
3. **Exception Hierarchy**: 3 specialized exception classes for composition violations
4. **Error Formatting**: Actionable error messages with fix suggestions

All modules designed for <30ms overhead and extends h-m1's decorator pattern to multi-tensor scenarios.

**Total Budget Used**: 10/10 (100%)  
**Ready for Phase 4 Coding**: Yes
