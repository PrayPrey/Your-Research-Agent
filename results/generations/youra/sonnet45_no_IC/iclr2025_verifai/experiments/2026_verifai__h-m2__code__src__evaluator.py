"""Evaluator for H-M1 - NL content gate logic."""

import json
from typing import Dict, List
from pathlib import Path
from .metrics_calculator import MetricsCalculator


class Evaluator:
    """Evaluate H-M1 hypothesis."""

    def __init__(self, calculator: MetricsCalculator, threshold: float = 0.90):
        """Initialize with metrics calculator and threshold."""
        self.calculator = calculator
        self.threshold = threshold

    def evaluate_hypothesis(self, traces: List[Dict]) -> Dict:
        """Evaluate H-M1 success criteria.

        Args:
            traces: List of trace dicts

        Returns:
            Results dict with all metrics
        """
        # Primary metric
        nl_rate = self.calculator.calculate_nl_presence_rate(traces)
        primary_pass = nl_rate >= self.threshold

        # Secondary metrics
        source_breakdown = self.calculator.calculate_source_breakdown(traces)
        tool_type_breakdown = self.calculator.calculate_tool_type_breakdown(traces)
        word_distribution = self.calculator.calculate_word_count_distribution(traces)

        # Gate decision
        gate_passed = primary_pass

        return {
            'nl_presence_rate': nl_rate,
            'threshold': self.threshold,
            'gate_passed': gate_passed,
            'source_breakdown': source_breakdown,
            'tool_type_breakdown': tool_type_breakdown,
            'word_count_distribution': word_distribution,
            'total_traces': len(traces),
            'total_tool_calls': sum(len(t['tool_calls']) for t in traces)
        }

    def check_gate_condition(self, results: Dict) -> bool:
        """Check if gate condition is satisfied."""
        return results['gate_passed']

    def save_results(self, results: Dict, output_path: Path) -> None:
        """Save results to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to: {output_path}")

    def print_summary(self, results: Dict) -> None:
        """Print evaluation summary to console."""
        print("\n" + "=" * 60)
        print("H-M1: NATURAL LANGUAGE CONTENT VALIDATION")
        print("=" * 60)
        print(f"\nPrimary Metric:")
        print(f"  NL Presence Rate: {results['nl_presence_rate']:.2%}")
        print(f"  Threshold: {results['threshold']:.2%}")
        print(f"  Status: {'✓ PASS' if results['gate_passed'] else '✗ FAIL'}")

        print(f"\nSource Breakdown:")
        for source_type, count in results['source_breakdown'].items():
            print(f"  {source_type}: {count}")

        print(f"\nWord Count Distribution:")
        for bin_name, count in results['word_count_distribution'].items():
            print(f"  {bin_name}: {count}")

        print(f"\nGate Decision:")
        if results['gate_passed']:
            print(f"  ✓ GATE PASSED - Proceed to H-M2")
        else:
            print(f"  ✗ GATE FAILED - STOP pipeline")

        print(f"\nDataset Statistics:")
        print(f"  Total traces: {results['total_traces']}")
        print(f"  Total tool calls: {results['total_tool_calls']}")

        print("=" * 60)
