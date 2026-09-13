"""
Contract Library for H-C2 Cross-Framework Validation
Implements dtype, shape, and numerical tolerance contracts
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import time
import numpy as np


@dataclass
class ContractResult:
    """Result of contract validation."""
    passed: bool
    defect_type: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
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
    src_adapter,
    tgt_adapter
) -> ContractResult:
    """Validate dtype consistency across framework conversion."""
    start_time = time.time()

    try:
        src_dtype = src_adapter.infer_dtype(src_model, test_input)
        tgt_dtype = tgt_adapter.infer_dtype(tgt_model, test_input)

        # Normalize dtype names (float32, float16, etc.)
        src_normalized = src_dtype.replace('torch.', '').replace('_ref', '')
        tgt_normalized = tgt_dtype.replace('torch.', '').replace('_ref', '')

        passed = (src_normalized == tgt_normalized)
        validation_time = time.time() - start_time

        if not passed:
            return ContractResult(
                passed=False,
                defect_type="DtypeCorruption",
                details={"expected": src_normalized, "actual": tgt_normalized},
                validation_time=validation_time
            )

        return ContractResult(passed=True, validation_time=validation_time)

    except Exception as e:
        validation_time = time.time() - start_time
        return ContractResult(
            passed=False,
            defect_type="ContractExecutionError",
            details={"error": str(e)},
            validation_time=validation_time
        )


@cross_framework_contract
def shape_consistent(
    src_model: Any,
    tgt_model: Any,
    test_input: np.ndarray,
    src_adapter,
    tgt_adapter
) -> ContractResult:
    """Validate output shape equivalence across frameworks."""
    start_time = time.time()

    try:
        src_shape = src_adapter.infer_shape(src_model, test_input)
        tgt_shape = tgt_adapter.infer_shape(tgt_model, test_input)

        passed = (src_shape == tgt_shape)
        validation_time = time.time() - start_time

        if not passed:
            # Check for transpose error
            error_type = "transpose_error" if src_shape == tuple(reversed(tgt_shape)) else "dimension_mismatch"

            return ContractResult(
                passed=False,
                defect_type="ShapeInconsistency",
                details={
                    "expected": src_shape,
                    "actual": tgt_shape,
                    "error_type": error_type
                },
                validation_time=validation_time
            )

        return ContractResult(passed=True, validation_time=validation_time)

    except Exception as e:
        validation_time = time.time() - start_time
        return ContractResult(
            passed=False,
            defect_type="ContractExecutionError",
            details={"error": str(e)},
            validation_time=validation_time
        )


@cross_framework_contract
def numerical_tolerance(
    src_model: Any,
    tgt_model: Any,
    test_input: np.ndarray,
    src_adapter,
    tgt_adapter,
    rtol: float = 1e-5,
    atol: float = 1e-7
) -> ContractResult:
    """Validate numerical equivalence using np.allclose semantics."""
    start_time = time.time()

    try:
        src_output = src_adapter.run_inference(src_model, test_input)
        tgt_output = tgt_adapter.run_inference(tgt_model, test_input)

        # Shape must match for numerical comparison
        if src_output.shape != tgt_output.shape:
            return ContractResult(
                passed=False,
                defect_type="ShapeInconsistency",
                details={
                    "src_shape": src_output.shape,
                    "tgt_shape": tgt_output.shape
                },
                validation_time=time.time() - start_time
            )

        # Numerical comparison using np.allclose
        passed = np.allclose(src_output, tgt_output, rtol=rtol, atol=atol)
        validation_time = time.time() - start_time

        if not passed:
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
                    "worst_index": str(worst_idx),
                    "src_value": float(src_output[worst_idx]),
                    "tgt_value": float(tgt_output[worst_idx]),
                    "rtol": rtol,
                    "atol": atol
                },
                validation_time=validation_time
            )

        return ContractResult(passed=True, validation_time=validation_time)

    except Exception as e:
        validation_time = time.time() - start_time
        return ContractResult(
            passed=False,
            defect_type="ContractExecutionError",
            details={"error": str(e)},
            validation_time=validation_time
        )
