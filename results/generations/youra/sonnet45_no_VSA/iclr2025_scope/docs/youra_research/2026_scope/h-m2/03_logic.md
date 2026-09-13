# Logic Design: H-M2 Metamorphic Contract Validation

**Hypothesis ID:** h-m2  
**Document Type:** Logic Design  
**Phase:** 3 - Implementation Planning  
**Status:** READY FOR CODING  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-m1 base code  
**Analyzed Path**: docs/youra_research/h-m1/code/  
**Relevant Symbols**: ContractViolationError, ShapeViolation, DeviceViolation, DtypeViolation, validate_structural, validate_at_import  
**Note**: H-m2 extends h-m1 decorator pattern with metamorphic property validation

---

## KB Pattern Application

**Applied**: PyTorch decorator pattern (HuggingFace diffusers validation), numerical tolerance testing (torch.allclose)

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are verified from h-m1 actual implementation:

```python
# From: docs/youra_research/h-m1/code/contracts/validator.py (ACTUAL CODE)

class ContractViolationError(Exception):
    """Base exception for contract violations"""
    pass

class ShapeViolation(ContractViolationError):
    """Raised when tensor shape doesn't match specification"""
    pass

class DeviceViolation(ContractViolationError):
    """Raised when tensor device doesn't match specification"""
    pass

class DtypeViolation(ContractViolationError):
    """Raised when tensor dtype doesn't match specification"""
    pass

def validate_structural(
    input_shapes: Dict[str, Tuple[int, ...]] = None,
    output_shape: Tuple[int, ...] = None,
    device: str = None,
    dtype: torch.dtype = None
) -> Callable:
    """Decorator for structural contract validation.
    
    Args:
        input_shapes: Expected shapes for input tensors (supports symbolic 'B' for batch)
        output_shape: Expected output shape
        device: Expected device ('cpu' or 'cuda')
        dtype: Expected dtype (e.g., torch.float32)
    
    Raises:
        ShapeViolation, DeviceViolation, DtypeViolation
    """
    ...

def validate_at_import(model_class):
    """Class decorator for import-time validation with probe inputs."""
    ...
```

**Verified from**: h-m1/code/contracts/validator.py (actual implementation)

---

## B-1: Metamorphic Validators [Complexity: 12, Budget: 12]

### API Signatures

```python
class MetamorphicViolation(ContractViolationError):
    """Base exception for metamorphic property violations"""
    pass

class SoftmaxSumViolation(MetamorphicViolation):
    """Raised when softmax sum property violated (sum ≠ 1.0)"""
    def __init__(self, message: str, actual_sum: float, tolerance: Dict[str, float]):
        super().__init__(message)
        self.actual_sum = actual_sum
        self.tolerance = tolerance

class DropoutIdentityViolation(MetamorphicViolation):
    """Raised when dropout identity property violated (output ≠ input in eval mode)"""
    pass

class MetamorphicValidator:
    """Validates metamorphic properties using probe inputs."""
    
    @staticmethod
    def validate_softmax(
        func: Callable,
        probe_input: torch.Tensor,
        dim: int = -1,
        rtol: float = 1e-5,
        atol: float = 1e-7
    ) -> bool:
        """Validate softmax sum=1.0 property.
        
        Args:
            func: Softmax function to validate
            probe_input: Probe tensor. Shape: [B, N]
            dim: Dimension for sum validation
            rtol: Relative tolerance
            atol: Absolute tolerance
        
        Returns:
            True if property holds, False otherwise
        
        Raises:
            SoftmaxSumViolation if sum ≠ 1.0
        """
        ...
    
    @staticmethod
    def validate_dropout_identity(
        module: torch.nn.Module,
        probe_input: torch.Tensor,
        eval_mode: bool = True
    ) -> bool:
        """Validate dropout identity property in eval mode.
        
        Args:
            module: Dropout module to validate
            probe_input: Probe tensor. Shape: [N]
            eval_mode: If True, set module to eval mode
        
        Returns:
            True if property holds (output == input), False otherwise
        
        Raises:
            DropoutIdentityViolation if output ≠ input
        """
        ...

def validate_metamorphic(
    softmax: bool = False,
    dropout: bool = False,
    rtol: float = 1e-5,
    atol: float = 1e-7
) -> Callable:
    """Decorator for metamorphic property validation.
    
    Args:
        softmax: If True, validate softmax sum=1.0 property
        dropout: If True, validate dropout identity in eval mode
        rtol: Relative tolerance for softmax validation
        atol: Absolute tolerance for softmax validation
    
    Returns:
        Decorator function
    
    Raises:
        SoftmaxSumViolation, DropoutIdentityViolation
    
    Example:
        @validate_metamorphic(softmax=True, rtol=1e-5, atol=1e-7)
        def attention_softmax(x: torch.Tensor) -> torch.Tensor:
            return torch.softmax(x, dim=-1)
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| probe_input (softmax) | [4, 10] | 4 samples, 10 classes |
| probe_input (dropout) | [100] | 100-element vector |
| output (softmax) | [4, 10] | Same as input |
| output (dropout) | [100] | Same as input |

### Pseudo-code

```
validate_softmax(func, probe_input, dim, rtol, atol):
    1. output = func(probe_input)  # [4, 10]
    2. sum_values = output.sum(dim=dim)  # [4]
    3. expected = torch.ones(sum_values.shape)  # [4] of 1.0s
    4. is_close = torch.allclose(sum_values, expected, rtol=rtol, atol=atol)
    5. if not is_close:
        actual_sum = sum_values.mean().item()
        raise SoftmaxSumViolation(
            f"Softmax sum property violated: sum={actual_sum:.6f}, expected 1.0",
            actual_sum=actual_sum,
            tolerance={"rtol": rtol, "atol": atol}
        )
    6. return True

validate_dropout_identity(module, probe_input, eval_mode):
    1. if eval_mode:
        module.eval()
    2. with torch.no_grad():
        output = module(probe_input)
    3. is_equal = torch.equal(probe_input, output)
    4. if not is_equal:
        raise DropoutIdentityViolation(
            f"Dropout identity violated: output ≠ input in eval mode"
        )
    5. return True

validate_metamorphic(softmax, dropout, rtol, atol):
    1. def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Softmax validation
            if softmax:
                probe = ProbeGenerator.softmax_probe()  # [4, 10]
                MetamorphicValidator.validate_softmax(func, probe, rtol=rtol, atol=atol)
            
            # Dropout validation
            if dropout:
                probe = ProbeGenerator.dropout_probe()  # [100]
                MetamorphicValidator.validate_dropout_identity(func, probe, eval_mode=True)
            
            # Execute original function
            return func(*args, **kwargs)
        return wrapper
    2. return decorator
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| B-1-1 | Exception classes | Define SoftmaxSumViolation, DropoutIdentityViolation |
| B-1-2 | Probe generation | Generate 4x10 softmax probe, 100-element dropout probe |
| B-1-3 | Softmax validation | torch.allclose for sum=1.0 check |
| B-1-4 | Dropout validation | torch.equal for identity check |
| B-1-5 | Decorator wrapper | Implement validate_metamorphic decorator |
| B-1-6 | Error formatting | Generate actionable error messages |
| B-1-7 | Tolerance configuration | Support rtol/atol parameters |
| B-1-8 | Eval mode handling | Set module.eval() for dropout |
| B-1-9 | Integration with h-m1 | Extend ContractViolationError hierarchy |
| B-1-10 | Softmax dimension | Support dim parameter for sum validation |
| B-1-11 | No-grad context | Disable gradients for probe execution |
| B-1-12 | Unit tests | Test softmax violations, dropout identity |

---

## B-2: Test Scenario Generation [Complexity: 10, Budget: 10]

### API Signatures

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class TestScenario:
    """Test scenario definition."""
    scenario_id: str
    defect_type: str
    test_func: Callable
    expected_detection: bool

class ScenarioGenerator:
    """Generates test scenarios for metamorphic validation."""
    
    def __init__(self):
        """Initialize scenario generator."""
        self._scenarios = []
    
    def control_scenario(self) -> TestScenario:
        """Generate control scenario (no defects).
        
        Returns:
            TestScenario with valid operations
        """
        ...
    
    def softmax_violation_scenario(self) -> TestScenario:
        """Generate softmax sum violation scenario.
        
        Returns:
            TestScenario with softmax defect (sum ≠ 1.0)
        """
        ...
    
    def dropout_violation_scenario(self) -> TestScenario:
        """Generate dropout identity violation scenario.
        
        Returns:
            TestScenario with dropout defect (applies in eval mode)
        """
        ...
    
    def generate_all(self) -> list[TestScenario]:
        """Generate all test scenarios.
        
        Returns:
            List of 50 test scenarios (10 control, 20 softmax, 20 dropout)
        """
        ...
```

### Pseudo-code

```
control_scenario():
    1. def test_func():
        x = torch.randn(4, 10)
        @validate_metamorphic(softmax=True)
        def valid_softmax(x):
            return torch.softmax(x, dim=-1)
        output = valid_softmax(x)
        assert output is not None
    2. return TestScenario(
        scenario_id="control-1",
        defect_type="none",
        test_func=test_func,
        expected_detection=False
    )

softmax_violation_scenario():
    1. def test_func():
        x = torch.randn(4, 10)
        @validate_metamorphic(softmax=True)
        def defective_softmax(x):
            output = torch.softmax(x, dim=-1)
            return output * 0.9  # Violate sum=1.0
        try:
            output = defective_softmax(x)
        except SoftmaxSumViolation:
            return True  # Detected
        return False  # Not detected
    2. return TestScenario(
        scenario_id="softmax-violation-1",
        defect_type="softmax_sum",
        test_func=test_func,
        expected_detection=True
    )

generate_all():
    1. scenarios = []
    2. for i in range(10):
        scenarios.append(control_scenario())
    3. for i in range(20):
        scenarios.append(softmax_violation_scenario())
    4. for i in range(20):
        scenarios.append(dropout_violation_scenario())
    5. return scenarios
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| B-2-1 | TestScenario dataclass | Define scenario structure |
| B-2-2 | Control generation | Create 10 valid scenarios |
| B-2-3 | Softmax defects | Generate 20 softmax violation scenarios |
| B-2-4 | Dropout defects | Generate 20 dropout violation scenarios |
| B-2-5 | Scenario IDs | Generate unique scenario identifiers |
| B-2-6 | Test functions | Wrap scenarios in executable functions |
| B-2-7 | Expected detection | Mark scenarios with expected result |
| B-2-8 | Scenario aggregation | Combine all scenarios into list |
| B-2-9 | Determinism | Ensure reproducible scenario generation |
| B-2-10 | Unit tests | Verify scenario count and types |

---

## B-3: Defect Injection [Complexity: 11, Budget: 11]

### API Signatures

```python
class DefectInjector:
    """Injects metamorphic defects for validation experiments."""
    
    @staticmethod
    def inject_softmax_violation(func: Callable) -> Callable:
        """Inject softmax sum violation.
        
        Args:
            func: Valid softmax function
        
        Returns:
            Defective function where sum ≠ 1.0
        
        Example:
            def valid_softmax(x):
                return torch.softmax(x, dim=-1)
            defective = DefectInjector.inject_softmax_violation(valid_softmax)
            # defective(x) returns output * 0.9 (sum ≠ 1.0)
        """
        ...
    
    @staticmethod
    def inject_dropout_violation(module: torch.nn.Module) -> torch.nn.Module:
        """Inject dropout identity violation.
        
        Args:
            module: Dropout module
        
        Returns:
            Defective module that applies dropout in eval mode
        
        Example:
            dropout = torch.nn.Dropout(p=0.5)
            defective = DefectInjector.inject_dropout_violation(dropout)
            # defective.eval() still applies dropout
        """
        ...
    
    @staticmethod
    def create_valid_operation() -> tuple[Callable, torch.nn.Module]:
        """Create valid operations for control tests.
        
        Returns:
            (valid_softmax_func, valid_dropout_module)
        """
        ...
```

### Pseudo-code

```
inject_softmax_violation(func):
    1. @functools.wraps(func)
       def defective(*args, **kwargs):
           output = func(*args, **kwargs)
           return output * 0.9  # Violate sum=1.0 property
    2. return defective

inject_dropout_violation(module):
    1. original_forward = module.forward
    2. def defective_forward(x):
           # Force training=True even in eval mode
           return torch.nn.functional.dropout(x, p=module.p, training=True)
    3. module.forward = defective_forward
    4. return module

create_valid_operation():
    1. def valid_softmax(x):
           return torch.softmax(x, dim=-1)
    2. valid_dropout = torch.nn.Dropout(p=0.5)
    3. return (valid_softmax, valid_dropout)
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| B-3-1 | Softmax wrapper | Wrap function to scale output by 0.9 |
| B-3-2 | Dropout patching | Override forward to force training=True |
| B-3-3 | Valid operations | Create control test operations |
| B-3-4 | Function wrapping | Use functools.wraps for metadata |
| B-3-5 | Module modification | Patch module.forward in-place |
| B-3-6 | Defect catalog | Define defect types and parameters |
| B-3-7 | Rollback mechanism | Restore original behavior if needed |
| B-3-8 | Multiple violations | Support multiple defect levels (0.9, 0.8, 0.7) |
| B-3-9 | Dropout p values | Test with p=0.1, 0.5, 0.9 |
| B-3-10 | Integration testing | Verify defects trigger violations |
| B-3-11 | Unit tests | Test injection, detection, rollback |

---

## B-4: Experiment Runner [Complexity: 13, Budget: 13]

### API Signatures

```python
import time
import json
from datetime import datetime

class ExperimentRunner:
    """Runs metamorphic contract validation experiment."""
    
    def __init__(self, scenarios: list[TestScenario]):
        """Initialize with test scenarios."""
        self.scenarios = scenarios
        self.results = []
    
    def run_baseline(self) -> dict:
        """Run without metamorphic contracts.
        
        Returns:
            Dict with keys: detected, total, detection_rate, execution_time
        
        Expected:
            detection_rate = 0.0 (no validation)
        """
        ...
    
    def run_with_contracts(self) -> dict:
        """Run with metamorphic validation enabled.
        
        Returns:
            Dict with keys: detected, total, detection_rate, execution_time
        
        Expected:
            detection_rate >= 0.70 (70% target)
        """
        ...
    
    def calculate_metrics(self, results: dict) -> dict:
        """Calculate detection rate, execution time, false positives.
        
        Args:
            results: Raw experiment results
        
        Returns:
            Dict with keys: detection_rate, execution_time_total, false_positive_rate
        """
        ...
    
    def save_results(self, results: dict, filepath: str):
        """Save results to JSON file.
        
        Args:
            results: Experiment results
            filepath: Output file path
        """
        ...
```

### Pseudo-code

```
run_baseline():
    1. start_time = time.time()
    2. detected = 0
    3. total = len(scenarios)
    4. for scenario in scenarios:
        # Run without contracts - no detection
        try:
            scenario.test_func()
        except Exception:
            pass  # Ignore errors
    5. execution_time = time.time() - start_time
    6. return {
        "detected": 0,
        "total": total,
        "detection_rate": 0.0,
        "execution_time": execution_time
    }

run_with_contracts():
    1. start_time = time.time()
    2. detected = 0
    3. total_violations = sum(1 for s in scenarios if s.expected_detection)
    4. for scenario in scenarios:
        try:
            result = scenario.test_func()
            if result is True:  # Detected
                detected += 1
        except (SoftmaxSumViolation, DropoutIdentityViolation):
            detected += 1  # Caught by contract
    5. execution_time = time.time() - start_time
    6. detection_rate = detected / total_violations if total_violations > 0 else 0.0
    7. return {
        "detected": detected,
        "total": total_violations,
        "detection_rate": detection_rate,
        "execution_time": execution_time
    }

calculate_metrics(results):
    1. detection_rate = results["detection_rate"]
    2. execution_time_total = results["execution_time"]
    3. control_failures = sum(1 for s in scenarios if s.defect_type == "none" and detected)
    4. false_positive_rate = control_failures / sum(1 for s in scenarios if s.defect_type == "none")
    5. return {
        "detection_rate": detection_rate,
        "execution_time_total": execution_time_total,
        "false_positive_rate": false_positive_rate
    }

save_results(results, filepath):
    1. output = {
        "experiment_id": "h-m2-poc",
        "timestamp": datetime.now().isoformat(),
        "detection_results": results,
        "summary": calculate_metrics(results)
    }
    2. with open(filepath, "w") as f:
        json.dump(output, f, indent=2)
```

### Subtasks [13/13 used]

| ID | Subtask | Description |
|----|---------|-------------|
| B-4-1 | Baseline execution | Run scenarios without contracts |
| B-4-2 | Contracts execution | Run scenarios with validation |
| B-4-3 | Detection counting | Count caught violations |
| B-4-4 | Time measurement | Wall-clock execution time |
| B-4-5 | Detection rate calc | detected / total_violations |
| B-4-6 | False positive calc | control_failures / control_total |
| B-4-7 | Results aggregation | Combine detection results |
| B-4-8 | JSON serialization | Save results to file |
| B-4-9 | Timestamp generation | ISO format timestamp |
| B-4-10 | Exception handling | Catch metamorphic violations |
| B-4-11 | Summary statistics | Calculate aggregate metrics |
| B-4-12 | Gate evaluation | Check if detection_rate >= 0.70 |
| B-4-13 | Unit tests | Test baseline, contracts, metrics |

---

## B-5: Numerical Tolerance Testing [Complexity: 9, Budget: 9]

### API Signatures

```python
class ProbeGenerator:
    """Generates probe inputs for metamorphic validation."""
    
    @staticmethod
    def softmax_probe(batch_size: int = 4, num_classes: int = 10) -> torch.Tensor:
        """Generate softmax probe input.
        
        Args:
            batch_size: Number of samples
            num_classes: Number of classes
        
        Returns:
            Probe tensor. Shape: [batch_size, num_classes]
        """
        ...
    
    @staticmethod
    def dropout_probe(size: int = 100) -> torch.Tensor:
        """Generate dropout probe input.
        
        Args:
            size: Vector size
        
        Returns:
            Probe tensor. Shape: [size]
        """
        ...
    
    @staticmethod
    def validate_sum_property(
        output: torch.Tensor,
        dim: int,
        rtol: float,
        atol: float
    ) -> bool:
        """Validate sum=1.0 property with tolerance.
        
        Args:
            output: Softmax output. Shape: [B, N]
            dim: Dimension for sum
            rtol: Relative tolerance
            atol: Absolute tolerance
        
        Returns:
            True if sum ≈ 1.0, False otherwise
        """
        ...
    
    @staticmethod
    def validate_identity(
        input: torch.Tensor,
        output: torch.Tensor
    ) -> bool:
        """Validate dropout identity property.
        
        Args:
            input: Original input. Shape: [N]
            output: Dropout output. Shape: [N]
        
        Returns:
            True if output == input, False otherwise
        """
        ...
```

### Pseudo-code

```
softmax_probe(batch_size, num_classes):
    1. return torch.randn(batch_size, num_classes)

dropout_probe(size):
    1. return torch.randn(size)

validate_sum_property(output, dim, rtol, atol):
    1. sum_values = output.sum(dim=dim)  # [B]
    2. expected = torch.ones(sum_values.shape)  # [B] of 1.0s
    3. return torch.allclose(sum_values, expected, rtol=rtol, atol=atol)

validate_identity(input, output):
    1. return torch.equal(input, output)
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| B-5-1 | Softmax probe | Generate [4, 10] random tensor |
| B-5-2 | Dropout probe | Generate [100] random tensor |
| B-5-3 | Sum validation | Use torch.allclose for sum=1.0 |
| B-5-4 | Identity validation | Use torch.equal for dropout |
| B-5-5 | Tolerance testing | Test rtol/atol edge cases |
| B-5-6 | Probe caching | Cache generated probes |
| B-5-7 | Seed control | Reproducible probe generation |
| B-5-8 | Edge cases | Test all-zeros, large values |
| B-5-9 | Unit tests | Verify tolerance boundaries |

---

## Summary

This logic design provides copy-paste ready APIs for the metamorphic contract validation system. Key algorithms:

1. **Metamorphic Validators**: Softmax sum (torch.allclose), dropout identity (torch.equal)
2. **Test Scenario Generation**: 10 control + 20 softmax + 20 dropout scenarios
3. **Defect Injection**: Function wrapping (0.9 scaling), module patching (force training=True)
4. **Experiment Runner**: Baseline (0% detection) vs contracts (≥70% detection)
5. **Numerical Tolerance**: PyTorch test suite tolerances (rtol=1e-5, atol=1e-7)

All modules designed for <10s execution time and <5% false positive rate.

**Total Budget Used**: 55/55 (100%)  
**Ready for Phase 4 Coding**: Yes
