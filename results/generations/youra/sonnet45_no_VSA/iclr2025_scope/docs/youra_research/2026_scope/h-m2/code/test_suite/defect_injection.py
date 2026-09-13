"""
Defect Injection for Controlled Metamorphic Property Violations

Implements controlled violation injection for:
1. Softmax Perturbation: Multiply output to break sum=1.0 property
2. Dropout Mode Forcing: Force dropout to apply even in eval mode
"""

import torch
import torch.nn as nn
from typing import Callable


class DefectInjector:
    """Injects controlled defects for testing metamorphic validators"""

    @staticmethod
    def perturb_softmax(
        output: torch.Tensor,
        perturbation_factor: float = 0.9
    ) -> torch.Tensor:
        """Perturb softmax output to violate sum=1.0 property

        Args:
            output: Valid softmax output (sum=1.0)
            perturbation_factor: Multiplication factor (e.g., 0.9 → sum=0.9)

        Returns:
            Perturbed output with sum ≠ 1.0
        """
        return output * perturbation_factor

    @staticmethod
    def create_broken_softmax(
        perturbation_factor: float = 0.9,
        dim: int = -1
    ) -> Callable:
        """Create a broken softmax function that violates sum property

        Args:
            perturbation_factor: Factor to multiply softmax output
            dim: Softmax dimension

        Returns:
            Broken softmax function
        """
        def broken_softmax(x, dim=dim):
            valid_output = torch.softmax(x, dim=dim)
            return DefectInjector.perturb_softmax(valid_output, perturbation_factor)

        return broken_softmax

    @staticmethod
    def create_broken_dropout(p: float = 0.5) -> nn.Module:
        """Create a broken dropout module that applies dropout even in eval mode

        Args:
            p: Dropout probability

        Returns:
            Broken dropout module
        """
        class BrokenDropout(nn.Module):
            """Dropout that ignores eval mode (simulates API bug)"""

            def __init__(self, p: float = 0.5):
                super().__init__()
                self.p = p

            def forward(self, x):
                # Bug: Always applies dropout regardless of training mode
                return torch.nn.functional.dropout(x, self.p, training=True)

        return BrokenDropout(p)

    @staticmethod
    def force_dropout_train_mode(module: nn.Dropout) -> None:
        """Force dropout module to stay in train mode

        Args:
            module: Dropout module to modify

        Note:
            This modifies the module in-place
        """
        # Override train/eval methods to keep training=True
        original_forward = module.forward

        def forced_train_forward(x):
            return torch.nn.functional.dropout(x, module.p, training=True)

        module.forward = forced_train_forward


class DefectScenarioExecutor:
    """Executes test scenarios with injected defects"""

    def __init__(self):
        self.injector = DefectInjector()

    def execute_softmax_scenario(
        self,
        probe_input: torch.Tensor,
        inject_defect: bool,
        perturbation_factor: float = 0.9,
        dim: int = -1
    ) -> tuple[torch.Tensor, bool]:
        """Execute softmax scenario with optional defect injection

        Args:
            probe_input: Input tensor
            inject_defect: Whether to inject defect
            perturbation_factor: Perturbation factor if defect injected
            dim: Softmax dimension

        Returns:
            (output, has_defect) tuple
        """
        if inject_defect:
            # Broken softmax
            func = self.injector.create_broken_softmax(perturbation_factor, dim)
            output = func(probe_input)
            return output, True
        else:
            # Valid softmax
            output = torch.softmax(probe_input, dim=dim)
            return output, False

    def execute_dropout_scenario(
        self,
        probe_input: torch.Tensor,
        inject_defect: bool,
        dropout_p: float = 0.5,
        eval_mode: bool = True
    ) -> tuple[torch.Tensor, bool]:
        """Execute dropout scenario with optional defect injection

        Args:
            probe_input: Input tensor
            inject_defect: Whether to inject defect
            dropout_p: Dropout probability
            eval_mode: Whether to set eval mode

        Returns:
            (output, has_defect) tuple
        """
        if inject_defect:
            # Broken dropout (applies even in eval mode)
            module = self.injector.create_broken_dropout(dropout_p)
            if eval_mode:
                module.eval()  # Set eval mode, but defect ignores it
            output = module(probe_input)
            return output, True
        else:
            # Valid dropout
            module = nn.Dropout(p=dropout_p)
            if eval_mode:
                module.eval()  # Eval mode → identity function
            output = module(probe_input)
            return output, False


# Ground Truth Labeling
class GroundTruthLabeler:
    """Assigns ground truth labels to test scenarios"""

    @staticmethod
    def label_softmax_scenario(
        output: torch.Tensor,
        dim: int = -1,
        rtol: float = 1e-5,
        atol: float = 1e-7
    ) -> dict:
        """Determine ground truth for softmax scenario

        Args:
            output: Softmax output
            dim: Dimension to check
            rtol: Relative tolerance
            atol: Absolute tolerance

        Returns:
            Ground truth dictionary with violation status
        """
        output_sum = output.sum(dim=dim)
        expected_sum = torch.ones_like(output_sum)
        is_valid = torch.allclose(output_sum, expected_sum, rtol=rtol, atol=atol)

        return {
            "has_violation": not is_valid,
            "actual_sum": output_sum.mean().item(),
            "expected_sum": 1.0,
            "max_deviation": (output_sum - expected_sum).abs().max().item()
        }

    @staticmethod
    def label_dropout_scenario(
        input_tensor: torch.Tensor,
        output: torch.Tensor
    ) -> dict:
        """Determine ground truth for dropout scenario

        Args:
            input_tensor: Input to dropout
            output: Output from dropout

        Returns:
            Ground truth dictionary with violation status
        """
        is_identity = torch.equal(input_tensor, output)

        return {
            "has_violation": not is_identity,
            "is_identity": is_identity,
            "max_diff": (input_tensor - output).abs().max().item(),
            "mean_diff": (input_tensor - output).abs().mean().item()
        }


# Example usage
if __name__ == "__main__":
    print("=== Defect Injection Examples ===\n")

    executor = DefectScenarioExecutor()
    labeler = GroundTruthLabeler()

    # Softmax defect injection
    print("1. Softmax Defect Injection:")
    probe = torch.randn(4, 10)
    output, has_defect = executor.execute_softmax_scenario(
        probe, inject_defect=True, perturbation_factor=0.9
    )
    label = labeler.label_softmax_scenario(output)
    print(f" Defect injected: {has_defect}")
    print(f" Ground truth violation: {label['has_violation']}")
    print(f" Actual sum: {label['actual_sum']:.6f}")
    print(f" Max deviation: {label['max_deviation']:.6e}\n")

    # Dropout defect injection
    print("2. Dropout Defect Injection:")
    probe = torch.randn(100)
    output, has_defect = executor.execute_dropout_scenario(
        probe, inject_defect=True, dropout_p=0.5, eval_mode=True
    )
    label = labeler.label_dropout_scenario(probe, output)
    print(f" Defect injected: {has_defect}")
    print(f" Ground truth violation: {label['has_violation']}")
    print(f" Is identity: {label['is_identity']}")
    print(f" Max diff: {label['max_diff']:.6e}")
