"""
H-M3: Composition-Level Contract Validation
Validates device placement, dtype consistency, and tensor layout across library boundaries
"""
import torch
import functools
import inspect
from typing import Callable, Dict, List, Optional, Any, Tuple


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


class CompositionValidator:
    """Core validator for composition-level contracts."""

    def validate_device_consistency(self, tensors: Dict[str, torch.Tensor]) -> Tuple[bool, Optional[List[Dict]]]:
        """Validate all tensors on same device.

        Args:
            tensors: Dict of param_name -> tensor

        Returns:
            (is_valid, violations). violations is None if valid.
        """
        if len(tensors) == 0:
            return (True, None)

        devices = {name: str(t.device) for name, t in tensors.items()}
        unique_devices = set(devices.values())

        if len(unique_devices) > 1:
            violations = [
                {
                    'param_name': name,
                    'device': dev,
                    'violation_type': 'device_mismatch'
                }
                for name, dev in devices.items()
            ]
            return (False, violations)

        return (True, None)

    def validate_dtype_consistency(
        self,
        tensors: Dict[str, torch.Tensor],
        dtype_spec: Dict[str, torch.dtype]
    ) -> Tuple[bool, Optional[List[Dict]]]:
        """Validate tensors match expected dtypes.

        Args:
            tensors: Dict of param_name -> tensor
            dtype_spec: Dict of param_name -> expected_dtype

        Returns:
            (is_valid, violations). violations is None if valid.
        """
        violations = []

        for param_name, expected_dtype in dtype_spec.items():
            if param_name not in tensors:
                continue

            tensor = tensors[param_name]
            if tensor.dtype != expected_dtype:
                violations.append({
                    'param_name': param_name,
                    'expected': str(expected_dtype),
                    'actual': str(tensor.dtype),
                    'violation_type': 'dtype_mismatch'
                })

        if violations:
            return (False, violations)
        return (True, None)

    def validate_layout_consistency(self, tensors: Dict[str, torch.Tensor]) -> Tuple[bool, Optional[List[Dict]]]:
        """Validate tensors have compatible layouts.

        Args:
            tensors: Dict of param_name -> tensor

        Returns:
            (is_valid, violations). violations is None if valid.
        """
        if len(tensors) == 0:
            return (True, None)

        layouts = {name: t.layout for name, t in tensors.items()}
        unique_layouts = set(layouts.values())

        # Check for incompatible combinations (e.g., strided + sparse)
        if torch.strided in unique_layouts and torch.sparse_coo in unique_layouts:
            violations = [
                {
                    'param_name': name,
                    'layout': str(layout),
                    'violation_type': 'layout_incompatible'
                }
                for name, layout in layouts.items()
            ]
            return (False, violations)

        return (True, None)

    def format_violation_message(self, violations: List[Dict[str, Any]], violation_type: str) -> str:
        """Format structured violation data into actionable error message.

        Args:
            violations: List of violation dicts
            violation_type: Type of violation (device/dtype/layout)

        Returns:
            Formatted error message with suggestions
        """
        if violation_type == 'device':
            devices = {v['param_name']: v['device'] for v in violations}
            msg = "Device consistency violation detected:\n"
            for param, dev in devices.items():
                msg += f"  - {param}: {dev}\n"
            msg += "\nSuggestion: Ensure all tensors are moved to same device before cross-library operations."
            return msg

        elif violation_type == 'dtype':
            msg = "Dtype consistency violation detected:\n"
            for v in violations:
                msg += f"  - {v['param_name']}: expected {v['expected']}, got {v['actual']}\n"
            msg += "\nSuggestion: Convert tensors to matching dtype before composition."
            return msg

        elif violation_type == 'layout':
            msg = "Layout consistency violation detected:\n"
            for v in violations:
                msg += f"  - {v['param_name']}: {v['layout']}\n"
            msg += "\nSuggestion: Convert all tensors to same layout (e.g., .to_dense() for sparse tensors)."
            return msg

        return "Unknown violation type"


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
            dtype_spec={'query': torch.float32, 'key': torch.float32}
        )
        def attention(query, key, value):
            return (query @ key.T) @ value
    """
    validator = CompositionValidator()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract tensors from args/kwargs
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            tensor_dict = {}
            for param_name, value in bound.arguments.items():
                if isinstance(value, torch.Tensor):
                    tensor_dict[param_name] = value

            # Device consistency check
            if device_consistency and len(tensor_dict) > 1:
                is_valid, violations = validator.validate_device_consistency(tensor_dict)
                if not is_valid:
                    message = validator.format_violation_message(violations, 'device')
                    raise DeviceConsistencyViolation(message, violations)

            # Dtype consistency check
            if dtype_spec:
                is_valid, violations = validator.validate_dtype_consistency(tensor_dict, dtype_spec)
                if not is_valid:
                    message = validator.format_violation_message(violations, 'dtype')
                    raise DtypeConsistencyViolation(message, violations)

            # Layout consistency check
            if layout_spec is not None:
                is_valid, violations = validator.validate_layout_consistency(tensor_dict)
                if not is_valid:
                    message = validator.format_violation_message(violations, 'layout')
                    raise LayoutConsistencyViolation(message, violations)

            # Execute function
            return func(*args, **kwargs)

        return wrapper
    return decorator
