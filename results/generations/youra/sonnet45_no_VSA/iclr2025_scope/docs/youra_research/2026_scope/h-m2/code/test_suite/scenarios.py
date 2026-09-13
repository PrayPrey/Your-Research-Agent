"""
Test Scenario Generation for Metamorphic Property Validation

Generates three types of scenarios:
1. Control (No Defect): Valid PyTorch operations, properties hold
2. Softmax Violation: Perturbed softmax output where sum ≠ 1.0
3. Dropout Identity Violation: Dropout applied in eval mode
"""

import torch
import torch.nn as nn
from dataclasses import dataclass
from typing import Literal, Optional
from enum import Enum


class ScenarioType(Enum):
    """Enumeration of scenario types"""
    CONTROL = "control"
    SOFTMAX_VIOLATION = "softmax_violation"
    DROPOUT_VIOLATION = "dropout_violation"


@dataclass
class Scenario:
    """Test scenario with known ground truth"""
    id: str
    type: ScenarioType
    operation: str  # "softmax" or "dropout"
    probe_input: torch.Tensor
    expected_violation: bool
    description: str
    defect_description: Optional[str] = None


class ScenarioGenerator:
    """Generates test scenarios for metamorphic property validation"""

    def __init__(self, seed: int = 42):
        """Initialize generator with fixed seed for reproducibility

        Args:
            seed: Random seed for deterministic generation
        """
        self.seed = seed
        torch.manual_seed(seed)

    def generate_control_scenarios(self, count: int = 10) -> list[Scenario]:
        """Generate control scenarios with no defects

        Args:
            count: Number of control scenarios to generate

        Returns:
            List of control scenarios (valid operations)
        """
        scenarios = []

        # Softmax controls (5 scenarios)
        for i in range(count // 2):
            probe = torch.randn(4, 10 + i)  # Varying input sizes
            scenarios.append(Scenario(
                id=f"control-softmax-{i:02d}",
                type=ScenarioType.CONTROL,
                operation="softmax",
                probe_input=probe,
                expected_violation=False,
                description=f"Valid softmax operation on tensor shape {list(probe.shape)}"
            ))

        # Dropout controls (5 scenarios)
        for i in range(count - count // 2):
            probe = torch.randn(100 + i * 10)  # Varying sizes
            scenarios.append(Scenario(
                id=f"control-dropout-{i:02d}",
                type=ScenarioType.CONTROL,
                operation="dropout",
                probe_input=probe,
                expected_violation=False,
                description=f"Valid dropout in eval mode on tensor size {probe.numel()}"
            ))

        return scenarios

    def generate_softmax_violation_scenarios(self, count: int = 20) -> list[Scenario]:
        """Generate softmax violation scenarios (perturbed outputs)

        Args:
            count: Number of softmax violation scenarios

        Returns:
            List of softmax violation scenarios
        """
        scenarios = []

        perturbation_factors = [0.9, 0.95, 0.85, 0.8, 1.1, 1.05]  # Various violations

        for i in range(count):
            probe = torch.randn(4, 10 + (i % 5))  # Varying input sizes
            factor = perturbation_factors[i % len(perturbation_factors)]

            scenarios.append(Scenario(
                id=f"softmax-violation-{i:02d}",
                type=ScenarioType.SOFTMAX_VIOLATION,
                operation="softmax",
                probe_input=probe,
                expected_violation=True,
                description=f"Softmax with sum property violated (factor={factor})",
                defect_description=f"Output multiplied by {factor}, sum ≠ 1.0"
            ))

        return scenarios

    def generate_dropout_violation_scenarios(self, count: int = 20) -> list[Scenario]:
        """Generate dropout identity violation scenarios

        Args:
            count: Number of dropout violation scenarios

        Returns:
            List of dropout identity violation scenarios
        """
        scenarios = []

        dropout_probs = [0.1, 0.3, 0.5, 0.7, 0.9]  # Various dropout rates

        for i in range(count):
            probe = torch.randn(100 + i * 10)  # Varying sizes
            p = dropout_probs[i % len(dropout_probs)]

            scenarios.append(Scenario(
                id=f"dropout-violation-{i:02d}",
                type=ScenarioType.DROPOUT_VIOLATION,
                operation="dropout",
                probe_input=probe,
                expected_violation=True,
                description=f"Dropout identity violated (p={p}, forced train mode)",
                defect_description=f"Dropout applied even in eval mode (p={p})"
            ))

        return scenarios

    def generate_full_suite(
        self,
        num_control: int = 10,
        num_softmax: int = 20,
        num_dropout: int = 20
    ) -> dict[str, list[Scenario]]:
        """Generate complete test suite with all scenario types

        Args:
            num_control: Number of control scenarios
            num_softmax: Number of softmax violation scenarios
            num_dropout: Number of dropout violation scenarios

        Returns:
            Dictionary with scenario types as keys and lists as values
        """
        # Reset seed for deterministic generation
        torch.manual_seed(self.seed)

        suite = {
            "control": self.generate_control_scenarios(num_control),
            "softmax_violations": self.generate_softmax_violation_scenarios(num_softmax),
            "dropout_violations": self.generate_dropout_violation_scenarios(num_dropout)
        }

        return suite

    def get_suite_statistics(self, suite: dict[str, list[Scenario]]) -> dict:
        """Get statistics about the test suite

        Args:
            suite: Test suite dictionary

        Returns:
            Statistics dictionary
        """
        total_scenarios = sum(len(scenarios) for scenarios in suite.values())
        violation_count = sum(
            len([s for s in scenarios if s.expected_violation])
            for scenarios in suite.values()
        )

        return {
            "total_scenarios": total_scenarios,
            "control_count": len(suite["control"]),
            "softmax_violation_count": len(suite["softmax_violations"]),
            "dropout_violation_count": len(suite["dropout_violations"]),
            "expected_violations": violation_count,
            "expected_passes": total_scenarios - violation_count
        }


# Example usage
if __name__ == "__main__":
    generator = ScenarioGenerator(seed=42)
    suite = generator.generate_full_suite(
        num_control=10,
        num_softmax=20,
        num_dropout=20
    )

    stats = generator.get_suite_statistics(suite)
    print(f"Test Suite Statistics:")
    print(f" Total scenarios: {stats['total_scenarios']}")
    print(f" Control: {stats['control_count']}")
    print(f" Softmax violations: {stats['softmax_violation_count']}")
    print(f" Dropout violations: {stats['dropout_violation_count']}")
    print(f" Expected violations: {stats['expected_violations']}")
    print(f" Expected passes: {stats['expected_passes']}")
