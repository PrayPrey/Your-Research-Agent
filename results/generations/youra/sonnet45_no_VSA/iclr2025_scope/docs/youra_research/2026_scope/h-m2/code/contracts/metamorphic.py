"""
Metamorphic Contract Validators for PyTorch Operations

Validates mathematical invariants (softmax sums, dropout identity)
via lightweight probe inputs without full inference.

Based on: h-m1 structural contracts (prerequisite)
"""

import torch
import torch.nn as nn
from typing import Callable, Dict
from contracts.validator import ContractViolationError


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
            True if property holds

        Raises:
            SoftmaxSumViolation if sum ≠ 1.0
        """
        # Apply function
        output = func(probe_input, dim=dim)

        # Compute sum along specified dimension
        output_sum = output.sum(dim=dim)

        # Expected sum: all ones (batch of 1.0 values)
        expected_sum = torch.ones_like(output_sum)

        # Check with numerical tolerance
        is_valid = torch.allclose(output_sum, expected_sum, rtol=rtol, atol=atol)

        if not is_valid:
            # Compute max deviation for error message
            max_deviation = (output_sum - expected_sum).abs().max().item()
            raise SoftmaxSumViolation(
                f"Softmax sum property violated: sum={output_sum.mean().item():.6f}, "
                f"expected=1.0, max_deviation={max_deviation:.6e}",
                actual_sum=output_sum.mean().item(),
                tolerance={"rtol": rtol, "atol": atol}
            )

        return True

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
            True if property holds (output == input)

        Raises:
            DropoutIdentityViolation if output ≠ input
        """
        # Set module to eval mode if requested
        if eval_mode:
            module.eval()

        # Apply module
        output = module(probe_input)

        # Check exact equality (dropout in eval mode should be identity)
        is_valid = torch.equal(probe_input, output)

        if not is_valid:
            # Compute difference for error message
            diff = (probe_input - output).abs()
            max_diff = diff.max().item()
            mean_diff = diff.mean().item()
            raise DropoutIdentityViolation(
                f"Dropout identity property violated in eval mode: "
                f"max_diff={max_diff:.6e}, mean_diff={mean_diff:.6e}"
            )

        return True


def validate_metamorphic(
    softmax: bool = False,
    dropout_identity: bool = False,
    dim: int = -1,
    rtol: float = 1e-5,
    atol: float = 1e-7,
    probe_size: int = 100
):
    """Decorator for metamorphic property validation.

    Args:
        softmax: Validate softmax sum property
        dropout_identity: Validate dropout identity property
        dim: Dimension for softmax validation
        rtol: Relative tolerance for softmax
        atol: Absolute tolerance for softmax
        probe_size: Size of probe input for validation

    Example:
        @validate_metamorphic(softmax=True, dim=-1)
        def my_softmax(x, dim=-1):
            return torch.softmax(x, dim=dim)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate probe input
            if softmax:
                probe_input = torch.randn(4, probe_size)  # Batch of 4 samples
                MetamorphicValidator.validate_softmax(
                    func, probe_input, dim=dim, rtol=rtol, atol=atol
                )

            # Call original function
            result = func(*args, **kwargs)

            # Validate dropout identity (module-based)
            if dropout_identity and isinstance(args[0], nn.Module):
                probe_input = torch.randn(probe_size)
                MetamorphicValidator.validate_dropout_identity(
                    args[0], probe_input, eval_mode=True
                )

            return result

        return wrapper

    return decorator
