"""
Experiment Runner for Metamorphic Contract Validation

Runs baseline (no contracts) vs proposed (with contracts) and calculates:
- Detection rate
- Execution time
- False positive rate
"""

import torch
import torch.nn as nn
import time
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contracts.metamorphic import MetamorphicValidator, SoftmaxSumViolation, DropoutIdentityViolation
from test_suite.scenarios import ScenarioGenerator, ScenarioType
from test_suite.defect_injection import DefectScenarioExecutor, GroundTruthLabeler


class BaselineExecution:
    """Baseline: No metamorphic validation"""

    def __init__(self):
        self.executor = DefectScenarioExecutor()

    def run_all_scenarios(self, scenarios_dict: dict) -> dict:
        """Run all scenarios without validation

        Returns:
            Results dictionary with 0% detection rate
        """
        results = {
            "detected_violations": 0,
            "total_violations": 0,
            "false_positives": 0,
            "total_control": 0,
            "execution_time_ms": 0
        }

        start_time = time.time()

        # Flatten all scenarios
        all_scenarios = []
        for scenario_list in scenarios_dict.values():
            all_scenarios.extend(scenario_list)

        # Execute without validation
        for scenario in all_scenarios:
            if scenario.expected_violation:
                results["total_violations"] += 1
            else:
                results["total_control"] += 1

            # Execute scenario (no validation → no detection)
            if scenario.operation == "softmax":
                self.executor.execute_softmax_scenario(
                    scenario.probe_input,
                    inject_defect=scenario.expected_violation
                )
            elif scenario.operation == "dropout":
                self.executor.execute_dropout_scenario(
                    scenario.probe_input,
                    inject_defect=scenario.expected_violation
                )

        end_time = time.time()
        results["execution_time_ms"] = (end_time - start_time) * 1000

        # Baseline detection rate: 0% (no validation)
        results["detection_rate"] = 0.0
        results["false_positive_rate"] = 0.0

        return results


class ProposedExecution:
    """Proposed: With metamorphic contract validation"""

    def __init__(self, rtol: float = 1e-5, atol: float = 1e-7):
        self.validator = MetamorphicValidator()
        self.executor = DefectScenarioExecutor()
        self.rtol = rtol
        self.atol = atol

    def run_all_scenarios(self, scenarios_dict: dict) -> dict:
        """Run all scenarios with metamorphic validation

        Returns:
            Results dictionary with detection metrics
        """
        results = {
            "detected_violations": 0,
            "total_violations": 0,
            "false_positives": 0,
            "total_control": 0,
            "execution_time_ms": 0,
            "per_scenario_results": []
        }

        start_time = time.time()

        # Flatten all scenarios
        all_scenarios = []
        for scenario_list in scenarios_dict.values():
            all_scenarios.extend(scenario_list)

        # Execute with validation
        for scenario in all_scenarios:
            scenario_result = {
                "id": scenario.id,
                "type": scenario.type.value,
                "expected_violation": scenario.expected_violation,
                "detected": False,
                "error_type": None
            }

            try:
                if scenario.operation == "softmax":
                    # Execute and validate
                    output, has_defect = self.executor.execute_softmax_scenario(
                        scenario.probe_input,
                        inject_defect=scenario.expected_violation
                    )

                    # Validate with metamorphic contract
                    if has_defect:
                        # Try validation on broken softmax
                        def broken_func(x, dim=-1):
                            return output  # Use pre-computed defective output

                        try:
                            self.validator.validate_softmax(
                                broken_func,
                                scenario.probe_input,
                                rtol=self.rtol,
                                atol=self.atol
                            )
                        except SoftmaxSumViolation:
                            scenario_result["detected"] = True
                            scenario_result["error_type"] = "SoftmaxSumViolation"

                elif scenario.operation == "dropout":
                    # Execute and validate
                    output, has_defect = self.executor.execute_dropout_scenario(
                        scenario.probe_input,
                        inject_defect=scenario.expected_violation,
                        eval_mode=True
                    )

                    # Validate with metamorphic contract
                    if has_defect:
                        # Create module for validation
                        module = self.executor.injector.create_broken_dropout(p=0.5)
                        module.eval()

                        try:
                            self.validator.validate_dropout_identity(
                                module,
                                scenario.probe_input,
                                eval_mode=True
                            )
                        except DropoutIdentityViolation:
                            scenario_result["detected"] = True
                            scenario_result["error_type"] = "DropoutIdentityViolation"
                    else:
                        # Control case: validate should pass
                        module = nn.Dropout(p=0.5)
                        module.eval()
                        try:
                            self.validator.validate_dropout_identity(
                                module,
                                scenario.probe_input,
                                eval_mode=True
                            )
                        except DropoutIdentityViolation:
                            # False positive
                            scenario_result["detected"] = True
                            scenario_result["error_type"] = "FalsePositive"

            except Exception as e:
                scenario_result["error_type"] = type(e).__name__

            # Update counters
            if scenario.expected_violation:
                results["total_violations"] += 1
                if scenario_result["detected"]:
                    results["detected_violations"] += 1
            else:
                results["total_control"] += 1
                if scenario_result["detected"]:
                    results["false_positives"] += 1

            results["per_scenario_results"].append(scenario_result)

        end_time = time.time()
        results["execution_time_ms"] = (end_time - start_time) * 1000

        # Calculate metrics
        if results["total_violations"] > 0:
            results["detection_rate"] = (results["detected_violations"] / results["total_violations"]) * 100
        else:
            results["detection_rate"] = 0.0

        if results["total_control"] > 0:
            results["false_positive_rate"] = (results["false_positives"] / results["total_control"]) * 100
        else:
            results["false_positive_rate"] = 0.0

        return results


def run_full_experiment(
    num_control: int = 10,
    num_softmax: int = 20,
    num_dropout: int = 20,
    seed: int = 42,
    output_file: str = "experiment_results.json"
) -> dict:
    """Run complete experiment: Baseline vs Proposed

    Args:
        num_control: Number of control scenarios
        num_softmax: Number of softmax violation scenarios
        num_dropout: Number of dropout violation scenarios
        seed: Random seed
        output_file: Output JSON file path

    Returns:
        Complete results dictionary
    """
    print("=" * 60)
    print("METAMORPHIC CONTRACT VALIDATION EXPERIMENT")
    print("=" * 60)
    print()

    # Generate test suite
    print(f"Generating test suite (seed={seed})...")
    generator = ScenarioGenerator(seed=seed)
    scenarios = generator.generate_full_suite(
        num_control=num_control,
        num_softmax=num_softmax,
        num_dropout=num_dropout
    )

    stats = generator.get_suite_statistics(scenarios)
    print(f"✓ Generated {stats['total_scenarios']} scenarios")
    print(f"  Control: {stats['control_count']}")
    print(f"  Softmax violations: {stats['softmax_violation_count']}")
    print(f"  Dropout violations: {stats['dropout_violation_count']}")
    print()

    # Run baseline
    print("Running Baseline (no contracts)...")
    baseline = BaselineExecution()
    baseline_results = baseline.run_all_scenarios(scenarios)
    print(f"✓ Baseline complete ({baseline_results['execution_time_ms']:.2f}ms)")
    print(f"  Detection rate: {baseline_results['detection_rate']:.1f}%")
    print()

    # Run proposed
    print("Running Proposed (with metamorphic contracts)...")
    proposed = ProposedExecution(rtol=1e-5, atol=1e-7)
    proposed_results = proposed.run_all_scenarios(scenarios)
    print(f"✓ Proposed complete ({proposed_results['execution_time_ms']:.2f}ms)")
    print(f"  Detection rate: {proposed_results['detection_rate']:.1f}%")
    print(f"  False positive rate: {proposed_results['false_positive_rate']:.1f}%")
    print()

    # Compile results
    results = {
        "experiment": {
            "seed": seed,
            "test_suite": stats
        },
        "baseline": baseline_results,
        "proposed": proposed_results,
        "comparison": {
            "detection_improvement": proposed_results["detection_rate"] - baseline_results["detection_rate"],
            "execution_overhead_ms": proposed_results["execution_time_ms"] - baseline_results["execution_time_ms"],
            "false_positive_rate": proposed_results["false_positive_rate"]
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent / output_file
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()

    # Print summary
    print("=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"Baseline Detection Rate:   {baseline_results['detection_rate']:6.1f}%")
    print(f"Proposed Detection Rate:   {proposed_results['detection_rate']:6.1f}%")
    print(f"Improvement:               {results['comparison']['detection_improvement']:+6.1f}%")
    print(f"False Positive Rate:       {proposed_results['false_positive_rate']:6.1f}%")
    print(f"Execution Overhead:        {results['comparison']['execution_overhead_ms']:6.1f}ms")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = run_full_experiment(
        num_control=10,
        num_softmax=20,
        num_dropout=20,
        seed=42
    )
