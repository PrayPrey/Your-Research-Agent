"""
Structural Contract Validator
Implements decorator-based shape/dtype/device validation at import time
"""
import torch
import functools
from typing import Callable, Dict, Any, Tuple
import time


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
):
    """
    Decorator for structural contract validation

    Args:
        input_shapes: Expected shapes for input tensors (supports symbolic 'B' for batch)
        output_shape: Expected output shape
        device: Expected device ('cpu' or 'cuda')
        dtype: Expected dtype (e.g., torch.float32)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validate inputs
            if input_shapes:
                # Extract tensors from args
                tensors = [arg for arg in args if isinstance(arg, torch.Tensor)]

                for i, (name, expected_shape) in enumerate(input_shapes.items()):
                    if i < len(tensors):
                        actual_shape = tuple(tensors[i].shape)

                        # Check shape (allow symbolic B for batch dimension)
                        if expected_shape:
                            expected_resolved = tuple(
                                s if s != 'B' else actual_shape[j]
                                for j, s in enumerate(expected_shape)
                            )
                            if len(actual_shape) != len(expected_resolved):
                                raise ShapeViolation(
                                    f"Shape mismatch for {name}: "
                                    f"expected {expected_shape}, got {actual_shape}"
                                )

                            for j, (exp, act) in enumerate(zip(expected_resolved, actual_shape)):
                                if isinstance(exp, int) and exp != act:
                                    raise ShapeViolation(
                                        f"Shape mismatch for {name} at dim {j}: "
                                        f"expected {expected_resolved}, got {actual_shape}"
                                    )

                        # Check device
                        if device and str(tensors[i].device).startswith(device):
                            pass  # Device matches
                        elif device:
                            raise DeviceViolation(
                                f"Device mismatch for {name}: "
                                f"expected {device}, got {tensors[i].device}"
                            )

                        # Check dtype
                        if dtype and tensors[i].dtype != dtype:
                            raise DtypeViolation(
                                f"Dtype mismatch for {name}: "
                                f"expected {dtype}, got {tensors[i].dtype}"
                            )

            # Execute function
            result = func(*args, **kwargs)

            # Validate output
            if output_shape and isinstance(result, torch.Tensor):
                actual_shape = tuple(result.shape)
                expected_resolved = tuple(
                    s if s != 'B' else actual_shape[j]
                    for j, s in enumerate(output_shape)
                )

                if len(actual_shape) != len(expected_resolved):
                    raise ShapeViolation(
                        f"Output shape mismatch: expected {output_shape}, got {actual_shape}"
                    )

                for j, (exp, act) in enumerate(zip(expected_resolved, actual_shape)):
                    if isinstance(exp, int) and exp != act:
                        raise ShapeViolation(
                            f"Output shape mismatch at dim {j}: "
                            f"expected {expected_resolved}, got {actual_shape}"
                        )

            return result

        return wrapper
    return decorator


# Import-time validation cache
_validation_cache = {}


def validate_at_import(model_class):
    """
    Class decorator that validates structural contracts at import/setup time
    Uses probe inputs to trigger validation before training
    """
    original_init = model_class.__init__

    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        # Call original __init__
        original_init(self, *args, **kwargs)

        # Run import-time validation with probe inputs
        cache_key = f"{model_class.__name__}_{id(self)}"
        if cache_key not in _validation_cache:
            try:
                # Check layer shapes at init time (import-time validation)
                # Inspect first conv layer to validate input shape
                if hasattr(self, 'conv1') and isinstance(self.conv1, torch.nn.Conv2d):
                    expected_in_channels = 3  # CIFAR-10 RGB
                    actual_in_channels = self.conv1.in_channels

                    if actual_in_channels != expected_in_channels:
                        raise ShapeViolation(
                            f"Import-time validation failed: "
                            f"conv1 expects {actual_in_channels} input channels, "
                            f"but dataset provides {expected_in_channels} channels"
                        )

                # Generate 1-sample probe batch for forward pass validation
                probe_input = torch.randn(1, 3, 32, 32)  # CIFAR-10 shape

                # Attempt forward pass to validate contracts
                with torch.no_grad():
                    _ = self.forward(probe_input)

                _validation_cache[cache_key] = True
            except ContractViolationError:
                # Contract violation detected at import time
                raise
            except Exception as e:
                # Other errors (not contract violations)
                # Re-raise if it's a RuntimeError from conv layer mismatch
                if "expected input" in str(e) and "to have" in str(e) and "channels" in str(e):
                    raise ShapeViolation(
                        f"Import-time shape validation failed: {str(e)}"
                    )
                _validation_cache[cache_key] = False

    model_class.__init__ = new_init
    return model_class
