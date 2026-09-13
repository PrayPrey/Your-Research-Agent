# Logic Design: H-C2 Cross-Framework Contract Validation System

**Hypothesis ID:** h-c2  
**Document Type:** Logic Design  
**Phase:** 3 - Implementation Planning  
**Status:** READY FOR CODING  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-m3 actual implementation  
**Analyzed Path**: docs/youra_research/h-m3/code/  
**Relevant Symbols**: validate_composition, CompositionValidator, CompositionViolation, DeviceConsistencyViolation, DtypeConsistencyViolation

**Critical Finding**: h-m3 validates cross-library composition within single framework (PyTorch + torchvision). h-c2 extends to cross-framework (PyTorch ↔ TensorFlow, PyTorch → JAX, * → ONNX) with numerical tolerance validation.

---

## KB Pattern Application

**Applied**: PyTorch torch.allclose pattern, ONNX validation protocol, cuBLAS numerical reproducibility guidelines, HuggingFace dtype preservation patterns

---

## A-1: Framework Adapter Protocol [Complexity: 12, Budget: 12]

### API Signatures

```python
from typing import Protocol, Union, Optional, Tuple, Any
import numpy as np
import torch


FrameworkTensor = Union[torch.Tensor, Any]  # tf.Tensor, jax.Array, onnx.TensorProto


class FrameworkAdapter(Protocol):
    """Unified interface for cross-framework model operations."""
    
    def infer_dtype(self, model: Any, test_input: np.ndarray) -> str:
        """Infer output dtype from model.
        
        Args:
            model: Framework-specific model object
            test_input: Input as NumPy array [N, ...]
        
        Returns:
            Dtype string (e.g., "float32", "int64")
        """
        ...
    
    def infer_shape(self, model: Any, test_input: np.ndarray) -> Tuple[int, ...]:
        """Infer output shape from model.
        
        Args:
            model: Framework-specific model object
            test_input: Input as NumPy array [N, ...]
        
        Returns:
            Output shape tuple (e.g., (1, 10))
        """
        ...
    
    def run_inference(self, model: Any, test_input: np.ndarray) -> np.ndarray:
        """Run forward pass and return NumPy output.
        
        Args:
            model: Framework-specific model object
            test_input: Input as NumPy array [N, ...]
        
        Returns:
            Output as NumPy array
        """
        ...
    
    def convert_input(self, input_array: np.ndarray) -> FrameworkTensor:
        """Convert NumPy array to framework-specific tensor.
        
        Args:
            input_array: NumPy array [N, ...]
        
        Returns:
            Framework tensor on appropriate device
        """
        ...


class PyTorchAdapter:
    """Adapter for PyTorch models."""
    
    def __init__(self, device: str = "cpu"):
        """Initialize adapter. device: [cpu, cuda, cuda:0]"""
        self.device = device
    
    def infer_dtype(self, model: torch.nn.Module, test_input: np.ndarray) -> str:
        """Returns PyTorch dtype string."""
        ...
    
    def infer_shape(self, model: torch.nn.Module, test_input: np.ndarray) -> Tuple[int, ...]:
        """Returns output shape tuple."""
        ...
    
    def run_inference(self, model: torch.nn.Module, test_input: np.ndarray) -> np.ndarray:
        """Run forward pass. model: [N, F] -> [N, C]"""
        ...
    
    def convert_input(self, input_array: np.ndarray) -> torch.Tensor:
        """NumPy -> torch.Tensor on self.device"""
        ...


class TensorFlowAdapter:
    """Adapter for TensorFlow/Keras models."""
    
    def infer_dtype(self, model: Any, test_input: np.ndarray) -> str:
        """Returns TF dtype string (float32, int32)."""
        ...
    
    def infer_shape(self, model: Any, test_input: np.ndarray) -> Tuple[int, ...]:
        """Returns output shape tuple."""
        ...
    
    def run_inference(self, model: Any, test_input: np.ndarray) -> np.ndarray:
        """Run inference. model: [N, F] -> [N, C]"""
        ...
    
    def convert_input(self, input_array: np.ndarray) -> Any:
        """NumPy -> tf.Tensor"""
        ...


class JAXAdapter:
    """Adapter for JAX models."""
    
    def infer_dtype(self, model: Any, test_input: np.ndarray) -> str:
        """Returns JAX dtype string."""
        ...
    
    def infer_shape(self, model: Any, test_input: np.ndarray) -> Tuple[int, ...]:
        """Returns output shape tuple."""
        ...
    
    def run_inference(self, model: Any, test_input: np.ndarray) -> np.ndarray:
        """Run inference. model: [N, F] -> [N, C]"""
        ...
    
    def convert_input(self, input_array: np.ndarray) -> Any:
        """NumPy -> jax.Array"""
        ...


class ONNXAdapter:
    """Adapter for ONNX models."""
    
    def infer_dtype(self, model: Any, test_input: np.ndarray) -> str:
        """Returns ONNX dtype string from output metadata."""
        ...
    
    def infer_shape(self, model: Any, test_input: np.ndarray) -> Tuple[int, ...]:
        """Returns output shape from ONNX graph."""
        ...
    
    def run_inference(self, model: Any, test_input: np.ndarray) -> np.ndarray:
        """Run ONNX inference session. model: [N, F] -> [N, C]"""
        ...
    
    def convert_input(self, input_array: np.ndarray) -> np.ndarray:
        """ONNX uses NumPy directly."""
        ...
```

### Pseudo-code

```
PyTorchAdapter.run_inference(model, test_input):
    1. model.eval()
    2. tensor_input = torch.from_numpy(test_input).to(self.device)
    3. with torch.no_grad():
        output = model(tensor_input)
    4. return output.cpu().numpy()

TensorFlowAdapter.run_inference(model, test_input):
    1. tf_input = tf.convert_to_tensor(test_input, dtype=tf.float32)
    2. output = model(tf_input, training=False)
    3. return output.numpy()

JAXAdapter.run_inference(model, test_input):
    1. jax_input = jnp.array(test_input)
    2. output = model.apply(params, jax_input)  # Assumes params bound
    3. return np.array(output)

ONNXAdapter.run_inference(model, test_input):
    1. ort_session = onnxruntime.InferenceSession(model)
    2. input_name = ort_session.get_inputs()[0].name
    3. output = ort_session.run(None, {input_name: test_input})
    4. return output[0]
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | PyTorchAdapter | Implement 4 methods for PyTorch |
| L-1-2 | TensorFlowAdapter | Implement 4 methods for TensorFlow |
| L-1-3 | JAXAdapter | Implement 4 methods for JAX |
| L-1-4 | ONNXAdapter | Implement 4 methods for ONNX |
| L-1-5 | Device management | Handle CPU/GPU device placement |
| L-1-6 | Dtype inference | Extract dtype from model metadata |
| L-1-7 | Shape inference | Extract shape from model output |
| L-1-8 | Error handling | Timeout + framework crash recovery |
| L-1-9 | DLPack conversion | Zero-copy tensor conversion |
| L-1-10 | Unit tests | Test each adapter on sample models |
| L-1-11 | Protocol validation | Ensure all adapters implement protocol |
| L-1-12 | Adapter factory | Select adapter based on framework type |

---

## A-2: Dtype Preservation Contract [Complexity: 8, Budget: 8]

### API Signatures

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ContractResult:
    """Result of contract validation."""
    passed: bool
    defect_type: Optional[str] = None  # "DtypeCorruption", "ShapeInconsistency", etc.
    details: Dict[str, Any] = None
    validation_time: float = 0.0


def cross_framework_contract(func):
    """Decorator marking function as cross-framework contract."""
    func._is_contract = True
    return func


@cross_framework_contract
def dtype_preserved(
    src_model: Any,
    tgt_model: Any,
    test_input: np.ndarray,
    src_adapter: FrameworkAdapter,
    tgt_adapter: FrameworkAdapter
) -> ContractResult:
    """Validate dtype consistency across framework conversion.
    
    Args:
        src_model: Source framework model
        tgt_model: Target framework model
        test_input: NumPy input [N, ...]
        src_adapter: Adapter for source framework
        tgt_adapter: Adapter for target framework
    
    Returns:
        ContractResult with pass/fail status
    
    Example:
        result = dtype_preserved(
            torch_model, tf_model, test_input,
            PyTorchAdapter(), TensorFlowAdapter()
        )
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| test_input | [N, F] | NumPy input batch |
| src_dtype | str | Source framework dtype |
| tgt_dtype | str | Target framework dtype |

### Pseudo-code

```
dtype_preserved(src_model, tgt_model, test_input, src_adapter, tgt_adapter):
    1. start_time = time.time()
    2. src_dtype = src_adapter.infer_dtype(src_model, test_input)
    3. tgt_dtype = tgt_adapter.infer_dtype(tgt_model, test_input)
    
    4. dtype_map = normalize_dtype_names()  # float32 -> float32, tf.float32 -> float32
    5. src_normalized = dtype_map.get(src_dtype, src_dtype)
    6. tgt_normalized = dtype_map.get(tgt_dtype, tgt_dtype)
    
    7. passed = (src_normalized == tgt_normalized)
    8. validation_time = time.time() - start_time
    
    9. if not passed:
        return ContractResult(
            passed=False,
            defect_type="DtypeCorruption",
            details={"expected": src_normalized, "actual": tgt_normalized},
            validation_time=validation_time
        )
    
    10. return ContractResult(passed=True, validation_time=validation_time)
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Dtype inference | Call adapter.infer_dtype() |
| L-2-2 | Dtype normalization | Map framework dtypes to canonical names |
| L-2-3 | Comparison logic | Check src == tgt after normalization |
| L-2-4 | ContractResult | Create result object with details |
| L-2-5 | Timeout handling | Max 10s per contract |
| L-2-6 | Error recovery | Handle adapter failures gracefully |
| L-2-7 | Unit tests | Test on known dtype defects |
| L-2-8 | Integration test | Test on ONNX converter corpus |

---

## A-3: Shape Consistency Contract [Complexity: 8, Budget: 8]

### API Signatures

```python
@cross_framework_contract
def shape_consistent(
    src_model: Any,
    tgt_model: Any,
    test_input: np.ndarray,
    src_adapter: FrameworkAdapter,
    tgt_adapter: FrameworkAdapter
) -> ContractResult:
    """Validate output shape equivalence across frameworks.
    
    Args:
        src_model: Source framework model
        tgt_model: Target framework model
        test_input: NumPy input [N, ...]
        src_adapter: Adapter for source framework
        tgt_adapter: Adapter for target framework
    
    Returns:
        ContractResult with pass/fail status
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| test_input | [N, F] | NumPy input batch |
| src_shape | Tuple[int, ...] | Source output shape |
| tgt_shape | Tuple[int, ...] | Target output shape |

### Pseudo-code

```
shape_consistent(src_model, tgt_model, test_input, src_adapter, tgt_adapter):
    1. start_time = time.time()
    2. src_shape = src_adapter.infer_shape(src_model, test_input)
    3. tgt_shape = tgt_adapter.infer_shape(tgt_model, test_input)
    
    4. passed = (src_shape == tgt_shape)
    5. validation_time = time.time() - start_time
    
    6. if not passed:
        # Check for common transpose errors
        if src_shape == tuple(reversed(tgt_shape)):
            defect_details = {
                "expected": src_shape,
                "actual": tgt_shape,
                "error_type": "transpose_error"
            }
        else:
            defect_details = {
                "expected": src_shape,
                "actual": tgt_shape,
                "error_type": "dimension_mismatch"
            }
        
        return ContractResult(
            passed=False,
            defect_type="ShapeInconsistency",
            details=defect_details,
            validation_time=validation_time
        )
    
    7. return ContractResult(passed=True, validation_time=validation_time)
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Shape inference | Call adapter.infer_shape() |
| L-3-2 | Shape comparison | Check exact tuple equality |
| L-3-3 | Transpose detection | Check for axis permutation errors |
| L-3-4 | Dimension mismatch | Detect missing/extra dimensions |
| L-3-5 | Dynamic shape handling | Handle None/-1 in shape tuples |
| L-3-6 | Error formatting | Create actionable error messages |
| L-3-7 | Unit tests | Test on shape defect samples |
| L-3-8 | Integration test | Test on CrossedWires models |

---

## A-4: Numerical Tolerance Contract [Complexity: 14, Budget: 14]

### API Signatures

```python
@cross_framework_contract
def numerical_tolerance(
    src_model: Any,
    tgt_model: Any,
    test_input: np.ndarray,
    src_adapter: FrameworkAdapter,
    tgt_adapter: FrameworkAdapter,
    rtol: float = 1e-5,
    atol: float = 1e-7
) -> ContractResult:
    """Validate numerical equivalence using np.allclose semantics.
    
    Args:
        src_model: Source framework model
        tgt_model: Target framework model
        test_input: NumPy input [N, ...]
        src_adapter: Adapter for source framework
        tgt_adapter: Adapter for target framework
        rtol: Relative tolerance (default: 1e-5 for float32)
        atol: Absolute tolerance (default: 1e-7 for near-zero)
    
    Returns:
        ContractResult with pass/fail status and numerical details
    
    Note:
        Uses np.allclose: |src - tgt| <= atol + rtol * |tgt|
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| test_input | [N, F] | NumPy input batch |
| src_output | [N, C] | Source framework output |
| tgt_output | [N, C] | Target framework output |
| diff | [N, C] | Absolute difference |

### Pseudo-code

```
numerical_tolerance(src_model, tgt_model, test_input, src_adapter, tgt_adapter, rtol, atol):
    1. start_time = time.time()
    
    # Run inference on both frameworks
    2. src_output = src_adapter.run_inference(src_model, test_input)
    3. tgt_output = tgt_adapter.run_inference(tgt_model, test_input)
    
    # Shape must match for numerical comparison
    4. if src_output.shape != tgt_output.shape:
        return ContractResult(
            passed=False,
            defect_type="ShapeInconsistency",
            details={"src_shape": src_output.shape, "tgt_shape": tgt_output.shape},
            validation_time=time.time() - start_time
        )
    
    # Numerical comparison using np.allclose
    5. passed = np.allclose(src_output, tgt_output, rtol=rtol, atol=atol)
    6. validation_time = time.time() - start_time
    
    7. if not passed:
        # Compute detailed error metrics
        diff = np.abs(src_output - tgt_output)
        max_abs_error = np.max(diff)
        mean_abs_error = np.mean(diff)
        
        # Compute relative error
        rel_error = diff / (np.abs(tgt_output) + 1e-10)
        max_rel_error = np.max(rel_error)
        
        # Find worst offending element
        worst_idx = np.unravel_index(np.argmax(diff), diff.shape)
        
        return ContractResult(
            passed=False,
            defect_type="NumericalDrift",
            details={
                "max_abs_error": float(max_abs_error),
                "mean_abs_error": float(mean_abs_error),
                "max_rel_error": float(max_rel_error),
                "worst_index": worst_idx,
                "src_value": float(src_output[worst_idx]),
                "tgt_value": float(tgt_output[worst_idx]),
                "rtol": rtol,
                "atol": atol
            },
            validation_time=validation_time
        )
    
    8. return ContractResult(passed=True, validation_time=validation_time)
```

### Subtasks [14/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Inference execution | Run src_adapter.run_inference() |
| L-4-2 | Target inference | Run tgt_adapter.run_inference() |
| L-4-3 | Shape validation | Check shapes match before comparison |
| L-4-4 | np.allclose | Apply tolerance check |
| L-4-5 | Error metrics | Compute max/mean absolute error |
| L-4-6 | Relative error | Compute max relative error |
| L-4-7 | Worst element | Find index of maximum error |
| L-4-8 | Per-operator tuning | Adjust rtol/atol per operator type |
| L-4-9 | Timeout handling | Max 10s per inference |
| L-4-10 | Device management | Handle GPU memory allocation |
| L-4-11 | Batch processing | Support multiple test inputs |
| L-4-12 | Error reporting | Format numerical details |
| L-4-13 | Unit tests | Test on synthetic defects |
| L-4-14 | Integration test | Test on CrossedWires accuracy discrepancies |

---

## A-5: Operator Semantics Contract [Complexity: 16, Budget: 16]

### API Signatures

```python
from typing import List, Set


@dataclass
class OperatorConstraint:
    """Extracted constraint from operator assertion."""
    param_name: str
    constraint_type: str  # "range", "enum", "dependency"
    values: Any  # e.g., [0, inf), ["valid", "same"], etc.


def extract_constraints(operator: Any, framework: str) -> List[OperatorConstraint]:
    """Extract parameter constraints from framework assertions.
    
    Args:
        operator: Framework operator (e.g., torch.nn.Conv2d, tf.keras.layers.Conv2D)
        framework: Framework name ("pytorch", "tensorflow", "jax")
    
    Returns:
        List of extracted constraints
    
    Note:
        Parses TORCH_CHECK, OP_REQUIRES, JAX checks from operator source
    """
    ...


@cross_framework_contract
def operator_semantics(
    src_op: Any,
    tgt_op: Any,
    params: Dict[str, Any],
    src_framework: str,
    tgt_framework: str
) -> ContractResult:
    """Validate API parameter equivalence at operator level.
    
    Args:
        src_op: Source operator (e.g., torch.nn.Conv2d)
        tgt_op: Target operator (e.g., tf.keras.layers.Conv2D)
        params: Parameter values (e.g., {"padding": "same", "stride": 2})
        src_framework: Source framework name
        tgt_framework: Target framework name
    
    Returns:
        ContractResult with pass/fail status
    """
    ...
```

### Pseudo-code

```
extract_constraints(operator, framework):
    1. if framework == "pytorch":
        # Parse TORCH_CHECK macros from C++ source
        source = inspect.getsource(operator.__init__)
        constraints = parse_torch_checks(source)
    
    2. elif framework == "tensorflow":
        # Parse OP_REQUIRES from TF source
        source = inspect.getsource(operator)
        constraints = parse_tf_requires(source)
    
    3. elif framework == "jax":
        # Parse JAX type annotations + docstring constraints
        sig = inspect.signature(operator)
        constraints = parse_jax_annotations(sig)
    
    4. return constraints

operator_semantics(src_op, tgt_op, params, src_framework, tgt_framework):
    1. start_time = time.time()
    
    # Extract constraints from both operators
    2. src_constraints = extract_constraints(src_op, src_framework)
    3. tgt_constraints = extract_constraints(tgt_op, tgt_framework)
    
    # Check parameter compatibility
    4. violations = []
    5. for param_name, value in params.items():
        src_constraint = find_constraint(src_constraints, param_name)
        tgt_constraint = find_constraint(tgt_constraints, param_name)
        
        # Check if constraints are compatible
        if src_constraint and tgt_constraint:
            if not constraints_compatible(src_constraint, tgt_constraint, value):
                violations.append({
                    "param_name": param_name,
                    "value": value,
                    "src_constraint": src_constraint,
                    "tgt_constraint": tgt_constraint
                })
    
    6. validation_time = time.time() - start_time
    
    7. if violations:
        return ContractResult(
            passed=False,
            defect_type="APIIncompatibility",
            details={"violations": violations},
            validation_time=validation_time
        )
    
    8. return ContractResult(passed=True, validation_time=validation_time)
```

### Subtasks [16/16 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | TORCH_CHECK parser | Extract constraints from PyTorch C++ |
| L-5-2 | OP_REQUIRES parser | Extract constraints from TensorFlow |
| L-5-3 | JAX annotation parser | Extract constraints from type hints |
| L-5-4 | Constraint representation | Define OperatorConstraint dataclass |
| L-5-5 | Range constraints | Handle [min, max) range checks |
| L-5-6 | Enum constraints | Handle allowed value sets |
| L-5-7 | Dependency constraints | Handle param A depends on param B |
| L-5-8 | Constraint compatibility | Check if src/tgt constraints compatible |
| L-5-9 | Parameter mapping | Map equivalent params across frameworks |
| L-5-10 | Default value handling | Handle different default values |
| L-5-11 | Violation reporting | Format actionable error messages |
| L-5-12 | Operator registry | Cache extracted constraints |
| L-5-13 | Unit tests | Test on known API incompatibilities |
| L-5-14 | Integration test | Test on ONNX converter failures |
| L-5-15 | Timeout handling | Max 10s per constraint extraction |
| L-5-16 | Error recovery | Handle missing/unparseable constraints |

---

## A-6: Contract Validator [Complexity: 10, Budget: 10]

### API Signatures

```python
@dataclass
class DefectReport:
    """Report for single detected defect."""
    defect_type: str  # "DtypeCorruption", "ShapeInconsistency", etc.
    contract_name: str  # Which contract detected it
    details: Dict[str, Any]
    validation_time: float


@dataclass
class ValidationReport:
    """Aggregated validation report."""
    passed: bool  # All contracts passed
    defects_detected: List[DefectReport]
    validation_time: float
    contract_results: Dict[str, ContractResult]


class ContractValidator:
    """Execute contracts at conversion boundaries."""
    
    def __init__(self, timeout: float = 10.0):
        """Initialize validator. timeout: Max seconds per contract"""
        self.timeout = timeout
    
    def validate_conversion(
        self,
        src_model: Any,
        tgt_model: Any,
        test_inputs: List[np.ndarray],
        contracts: List[callable],
        src_adapter: FrameworkAdapter,
        tgt_adapter: FrameworkAdapter
    ) -> ValidationReport:
        """Run all contracts on multiple test inputs.
        
        Args:
            src_model: Source framework model
            tgt_model: Target framework model
            test_inputs: List of test inputs [10-100 inputs]
            contracts: List of contract functions
            src_adapter: Adapter for source framework
            tgt_adapter: Adapter for target framework
        
        Returns:
            ValidationReport with aggregated results
        """
        ...
```

### Pseudo-code

```
ContractValidator.validate_conversion(src_model, tgt_model, test_inputs, contracts, src_adapter, tgt_adapter):
    1. start_time = time.time()
    2. contract_results = {}
    3. defects_detected = []
    
    # Execute each contract
    4. for contract_func in contracts:
        contract_name = contract_func.__name__
        
        # Aggregate results across multiple test inputs
        results = []
        for test_input in test_inputs:
            try:
                # Run contract with timeout
                result = run_with_timeout(
                    contract_func,
                    args=(src_model, tgt_model, test_input, src_adapter, tgt_adapter),
                    timeout=self.timeout
                )
                results.append(result)
            except TimeoutError:
                results.append(ContractResult(
                    passed=False,
                    defect_type="Timeout",
                    details={"timeout_seconds": self.timeout}
                ))
        
        # Aggregate results (contract passes if all inputs pass)
        aggregated = aggregate_results(results)
        contract_results[contract_name] = aggregated
        
        # Record defects
        if not aggregated.passed:
            defects_detected.append(DefectReport(
                defect_type=aggregated.defect_type,
                contract_name=contract_name,
                details=aggregated.details,
                validation_time=aggregated.validation_time
            ))
    
    5. validation_time = time.time() - start_time
    6. passed = len(defects_detected) == 0
    
    7. return ValidationReport(
        passed=passed,
        defects_detected=defects_detected,
        validation_time=validation_time,
        contract_results=contract_results
    )
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Contract execution | Call each contract function |
| L-6-2 | Timeout wrapper | Implement run_with_timeout() |
| L-6-3 | Multi-input aggregation | Aggregate results across test inputs |
| L-6-4 | Result collection | Store ContractResult per contract |
| L-6-5 | Defect mapping | Create DefectReport from failures |
| L-6-6 | ValidationReport | Create final report object |
| L-6-7 | Parallel execution | Run contracts in parallel (optional) |
| L-6-8 | Error recovery | Handle contract crashes gracefully |
| L-6-9 | Unit tests | Test validator on sample models |
| L-6-10 | Integration test | Test on full ONNX corpus |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From h-m3 Actual Code)

h-c2 does NOT directly call h-m3 code, but follows the same decorator and exception pattern:

```python
# From: docs/youra_research/h-m3/code/composition_validator.py (ACTUAL CODE)

class CompositionViolation(Exception):
    """Base exception for composition-level violations."""
    def __init__(self, message: str, violations: List[Dict[str, Any]]):
        super().__init__(message)
        self.violations = violations


def validate_composition(
    device_consistency: bool = True,
    dtype_spec: Optional[Dict[str, torch.dtype]] = None,
    layout_spec: Optional[Dict[str, torch.layout]] = None
) -> Callable:
    """Decorator for composition-level contract validation."""
    ...
```

**Pattern Application**: h-c2 extends this decorator pattern to cross-framework validation using `@cross_framework_contract` decorator and `ContractResult` dataclass.

**Verified from**: `docs/youra_research/h-m3/code/composition_validator.py` (actual implementation)

---

## Edge Cases & Error Handling

### Edge Case 1: Dynamic Shapes (Batch Size, Sequence Length)

**Scenario**: PyTorch model uses dynamic batch size (-1), TensorFlow uses fixed batch  
**Solution**: Normalize shapes by replacing dynamic dimensions with wildcard  
**Validation**: Shape comparison ignores batch dimension if both use dynamic

### Edge Case 2: Mixed Precision (float32 vs float16)

**Scenario**: Model converted with mixed precision optimization  
**Solution**: Adjust numerical tolerance (rtol=1e-3 for float16)  
**Validation**: Detect mixed precision and auto-adjust tolerance

### Edge Case 3: Framework Version Differences

**Scenario**: PyTorch 1.13 vs PyTorch 2.0 operator differences  
**Solution**: Pin framework versions in requirements.txt  
**Validation**: Check framework versions before validation

### Edge Case 4: Operator Not Found in Target Framework

**Scenario**: Custom operator in PyTorch has no TensorFlow equivalent  
**Solution**: Skip operator_semantics contract for custom ops  
**Validation**: Detect custom operators and log warning

### Edge Case 5: ONNX Opset Version Mismatch

**Scenario**: PyTorch exports to ONNX opset 13, converter expects opset 14  
**Solution**: Check ONNX opset version before validation  
**Validation**: Log opset version in ValidationReport

---

## Algorithm Complexity Analysis

| Component | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| Dtype inference | O(1) | O(1) | Metadata lookup only |
| Shape inference | O(1) | O(1) | Metadata lookup only |
| Numerical tolerance | O(N×C) | O(N×C) | N=batch, C=output dim (inference) |
| Operator semantics | O(P×K) | O(K) | P=params, K=constraints |
| Contract aggregation | O(C×T) | O(C×T) | C=contracts, T=test inputs |
| Total per model | O(C×T×N×C) | O(T×N×C) | Dominated by numerical contract |

**Expected Latency**: <5s per model (target: 3s average)

---

## Numerical Tolerance Specification

### Default Tolerances (float32)

- **rtol**: 1e-5 (relative tolerance)
- **atol**: 1e-7 (absolute tolerance for near-zero)
- **Formula**: `|src - tgt| <= atol + rtol * |tgt|`

### Per-Operator Tolerances

| Operator | rtol | atol | Rationale |
|----------|------|------|-----------|
| matmul | 1e-5 | 1e-7 | Accumulation order differences |
| conv2d | 1e-4 | 1e-6 | Kernel implementation variance |
| softmax | 1e-5 | 1e-8 | Numerical stability differences |
| batchnorm | 1e-4 | 1e-6 | Running stats accumulation |
| layernorm | 1e-5 | 1e-7 | Standard tolerance |

### Mixed Precision Adjustments

- **float16**: rtol=1e-3, atol=1e-5
- **bfloat16**: rtol=1e-2, atol=1e-4
- **int8**: Exact match (no tolerance)

---

## Shape Type System

### Static Shapes

```python
shape: Tuple[int, ...]  # (1, 10) - all dimensions known
```

### Dynamic Shapes

```python
shape: Tuple[Optional[int], ...]  # (None, 10) - batch dimension dynamic
```

### Shape Inference Algorithm

```
infer_shape(model, test_input):
    1. input_shape = test_input.shape
    2. output_metadata = model.get_output_metadata()  # Framework-specific
    3. if output_metadata.shape contains -1 or None:
        # Dynamic dimension - need actual inference
        output = model(test_input)
        return output.shape
    4. else:
        # Static shape from metadata
        return output_metadata.shape
```

---

## Timeout & Error Recovery

### Timeout Mechanism

```python
import signal
from contextlib import contextmanager


@contextmanager
def timeout(seconds: float):
    """Context manager for timeout."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation exceeded {seconds}s")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(seconds))
    try:
        yield
    finally:
        signal.alarm(0)


# Usage in contract
with timeout(10.0):
    result = contract_func(src_model, tgt_model, test_input, src_adapter, tgt_adapter)
```

### Error Recovery Strategy

1. **Framework Crash**: Catch all exceptions, return ContractResult with passed=False
2. **OOM Error**: Reduce batch size, retry with smaller input
3. **Timeout**: Log timeout, continue with next contract
4. **Adapter Failure**: Skip contract, log warning in ValidationReport

---

## Summary

This logic design provides **copy-paste ready APIs** for cross-framework contract validation. Key components:

1. **Framework Adapters**: Unified interface for PyTorch, TensorFlow, JAX, ONNX
2. **4 Contract Types**: Dtype, shape, numerical tolerance, operator semantics
3. **Contract Validator**: Aggregate results across multiple test inputs
4. **Numerical Specification**: np.allclose semantics with per-operator tuning
5. **Error Handling**: Timeout + framework crash recovery

All modules designed for <5s validation time and extends h-m3's decorator pattern to cross-framework scenarios.

**Total Budget Used**: 68/68 (100%)  
**Ready for Phase 4 Coding**: Yes
