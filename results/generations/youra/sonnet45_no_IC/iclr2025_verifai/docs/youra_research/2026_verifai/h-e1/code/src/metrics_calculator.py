"""Metrics Calculator - Completeness rate and statistics."""

from typing import List, Dict
from .completeness_validator import CompletenessValidator


class MetricsCalculator:
    """Calculate completeness metrics."""

    def __init__(self, validator: CompletenessValidator):
        """Initialize with validator instance."""
        self.validator = validator

    def calculate_overall_completeness(self, traces: List[Dict]) -> float:
        """Calculate overall completeness rate.

        Args:
            traces: List of trace dicts

        Returns:
            Completeness rate [0.0, 1.0]
        """
        total_calls = 0
        complete_calls = 0

        for trace in traces:
            for tool_call in trace['tool_calls']:
                total_calls += 1
                if self.validator.validate_tool_call(tool_call):
                    complete_calls += 1

        if total_calls == 0:
            return 0.0

        return complete_calls / total_calls

    def calculate_per_file_stats(self, traces: List[Dict]) -> Dict[str, float]:
        """Calculate per-file statistics.

        Args:
            traces: List of trace dicts

        Returns:
            Dict with keys: min, max, mean
        """
        per_file_rates = []

        for trace in traces:
            if len(trace['tool_calls']) == 0:
                continue

            complete = sum(
                1 for tc in trace['tool_calls']
                if self.validator.validate_tool_call(tc)
            )
            rate = complete / len(trace['tool_calls'])
            per_file_rates.append(rate)

        if not per_file_rates:
            return {'min': 0.0, 'max': 0.0, 'mean': 0.0}

        return {
            'min': min(per_file_rates),
            'max': max(per_file_rates),
            'mean': sum(per_file_rates) / len(per_file_rates)
        }

    def verify_failure_traces(self, traces: List[Dict]) -> Dict[str, bool]:
        """Verify h-e1 and h-m1 failure traces present.

        Args:
            traces: List of trace dicts

        Returns:
            Dict with keys: h_e1_present, h_m1_present
        """
        failure_traces = [t for t in traces if t['outcome'] == 'fail']

        h_e1_present = any(
            'h-e1' in t['file'].lower() or 'h_e1' in t['file'].lower()
            for t in failure_traces
        )

        h_m1_present = any(
            'h-m1' in t['file'].lower() or 'h_m1' in t['file'].lower()
            for t in failure_traces
        )

        return {
            'h_e1_present': h_e1_present,
            'h_m1_present': h_m1_present
        }
