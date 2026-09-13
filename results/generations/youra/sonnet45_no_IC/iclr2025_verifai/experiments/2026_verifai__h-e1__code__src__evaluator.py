"""Evaluator - Gate condition logic and results output."""

import json
from typing import Dict, List
from pathlib import Path
from .metrics_calculator import MetricsCalculator


class Evaluator:
    """Evaluate hypothesis and save results."""

    def __init__(self, calculator: MetricsCalculator, threshold: float = 0.95):
        """Initialize with metrics calculator and threshold."""
        self.calculator = calculator
        self.threshold = threshold

    def evaluate_hypothesis(self, traces: List[Dict]) -> Dict:
        """Evaluate H-E1 success criteria.

        Args:
            traces: List of trace dicts

        Returns:
            Results dict with all metrics
        """
        # Primary metric
        completeness_rate = self.calculator.calculate_overall_completeness(traces)
        primary_pass = completeness_rate >= self.threshold

        # Secondary metrics
        per_file_stats = self.calculator.calculate_per_file_stats(traces)
        failure_trace_check = self.calculator.verify_failure_traces(traces)

        # Gate decision
        gate_passed = (
            primary_pass
            and failure_trace_check['h_e1_present']
            and failure_trace_check['h_m1_present']
        )

        return {
            'completeness_rate': completeness_rate,
            'threshold': self.threshold,
            'primary_pass': primary_pass,
            'per_file_min': per_file_stats['min'],
            'per_file_max': per_file_stats['max'],
            'per_file_mean': per_file_stats['mean'],
            'h_e1_present': failure_trace_check['h_e1_present'],
            'h_m1_present': failure_trace_check['h_m1_present'],
            'gate_passed': gate_passed,
            'total_traces': len(traces),
            'total_tool_calls': sum(len(t['tool_calls']) for t in traces)
        }

    def check_gate_condition(self, results: Dict) -> bool:
        """Check if gate condition is satisfied.

        Args:
            results: Results dict from evaluate_hypothesis

        Returns:
            True if gate passed
        """
        return results['gate_passed']

    def save_results(self, results: Dict, output_path: Path) -> None:
        """Save results to JSON file.

        Args:
            results: Results dict
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to: {output_path}")

    def print_summary(self, results: Dict) -> None:
        """Print evaluation summary to console.

        Args:
            results: Results dict
        """
        print("\n" + "=" * 60)
        print("H-E1 EVALUATION SUMMARY")
        print("=" * 60)
        print(f"\nPrimary Metric:")
        print(f"  Completeness Rate: {results['completeness_rate']:.2%}")
        print(f"  Threshold: {results['threshold']:.2%}")
        print(f"  Status: {'✓ PASS' if results['primary_pass'] else '✗ FAIL'}")

        print(f"\nPer-File Statistics:")
        print(f"  Min: {results['per_file_min']:.2%}")
        print(f"  Max: {results['per_file_max']:.2%}")
        print(f"  Mean: {results['per_file_mean']:.2%}")

        print(f"\nFailure Trace Verification:")
        print(f"  h-e1 present: {'✓ Yes' if results['h_e1_present'] else '✗ No'}")
        print(f"  h-m1 present: {'✓ Yes' if results['h_m1_present'] else '✗ No'}")

        print(f"\nGate Decision:")
        if results['gate_passed']:
            print(f"  ✓ GATE PASSED - Proceed to H-M1")
        else:
            print(f"  ✗ GATE FAILED - STOP pipeline")

        print(f"\nDataset Statistics:")
        print(f"  Total traces: {results['total_traces']}")
        print(f"  Total tool calls: {results['total_tool_calls']}")

        print("=" * 60)
